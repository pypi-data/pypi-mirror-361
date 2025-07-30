# scheduler.py

import community as community_louvain
import networkx as nx
import numpy as np
import time
from collections import defaultdict
from edgefedsim.utils import *

class BaseScheduler:
    """Abstract base class for all schedulers."""
    def __init__(self, env, federation):
        self.env = env
        self.federation = federation
        self.name = "BaseScheduler"

    def schedule(self, workflow):
        """The main scheduling logic to be implemented by subclasses."""
        raise NotImplementedError

    def _get_decision_latency(self):
        """Simulates the time taken to make a scheduling decision."""
        # Base latency is negligible, can be overridden by complex schedulers
        return 0.001 # 1ms

# --- CEREBRUM IMPLEMENTATION ---

def hierarchical_workflow_decomposition(workflow):
    """
    Implements the HWD algorithm using Louvain community detection.
    """
    g = workflow.dag.to_undirected()
    
    # Use data transfer size as weight for community detection
    for u, v, data in workflow.dag.edges(data=True):
        g[u][v]['weight'] = data.get('data_size', 1.0)

    partition = community_louvain.best_partition(g, weight='weight')
    
    num_communities = len(set(partition.values()))
    if num_communities <= 1: # No meaningful decomposition
        return None, None

    # Create micro-DAGs (subgraphs for each community)
    micro_dags = defaultdict(nx.DiGraph)
    for node, comm_id in partition.items():
        micro_dags[comm_id].add_node(node, **workflow.dag.nodes[node])

    for u, v, data in workflow.dag.edges(data=True):
        comm_u = partition[u]
        comm_v = partition[v]
        if comm_u == comm_v:
            micro_dags[comm_u].add_edge(u, v, **data)

    # Create macro-DAG (dependencies between micro-DAGs)
    macro_dag = nx.DiGraph()
    for comm_id in micro_dags:
        # Calculate aggregate resource demand for the micro-dag
        agg_cpu = sum(d['task_obj'].cpu_req for _, d in micro_dags[comm_id].nodes(data=True))
        agg_mem = sum(d['task_obj'].mem_req for _, d in micro_dags[comm_id].nodes(data=True))
        macro_dag.add_node(comm_id, micro_dag=micro_dags[comm_id], agg_cpu=agg_cpu, agg_mem=agg_mem)

    for u, v, data in workflow.dag.edges(data=True):
        comm_u = partition[u]
        comm_v = partition[v]
        if comm_u != comm_v:
            # Add or update edge weight in macro-dag
            if macro_dag.has_edge(comm_u, comm_v):
                macro_dag[comm_u][comm_v]['data_size'] += data['data_size']
            else:
                macro_dag.add_edge(comm_u, comm_v, data_size=data['data_size'])
                
    return macro_dag, micro_dags


class CerebrumScheduler(BaseScheduler):
    """
    Implements the full Cerebrum architecture: GCC for macro-scheduling
    and LCAs for proactive, multi-objective micro-scheduling.
    """
    def __init__(self, env, federation, policy='balanced'):
        super().__init__(env, federation)
        self.name = f"Cerebrum ({policy})"
        self.policy_weights = CEREBRUM_POLICY_WEIGHTS[policy]
        self.lcas = {cid: self.LCA(self, cid) for cid in self.federation.clusters}
        self.decision_latencies = []

    def schedule(self, workflow):
        start_time = time.time()
        # 1. Global Controller (GCC) Logic
        macro_dag, _ = hierarchical_workflow_decomposition(workflow)
        
        if macro_dag is None:
            # If decomposition fails or is trivial, treat whole workflow as one micro-dag
            macro_dag = nx.DiGraph()
            macro_dag.add_node(0, micro_dag=workflow.dag)
        
        # Macro-scheduling: Assign each micro-dag to a cluster
        micro_dag_placements = self._gcc_assign_micro_dags(macro_dag)

        # 2. Local Agent (LCA) Logic
        # For each micro-dag, the assigned LCA schedules its tasks
        task_placements = {}
        for comm_id, cluster_id in micro_dag_placements.items():
            micro_dag = macro_dag.nodes[comm_id]['micro_dag']
            lca = self.lcas[cluster_id]
            placements = lca.schedule_micro_dag(micro_dag)
            task_placements.update(placements)

        end_time = time.time()
        self.decision_latencies.append((end_time - start_time) * 1000) # in ms
        return task_placements

    def _gcc_assign_micro_dags(self, macro_dag):
        """Simple greedy macro-scheduler."""
        placements = {}
        # Prioritize assigning connected micro-DAGs to the same cluster
        sorted_nodes = list(nx.topological_sort(macro_dag))
        
        for comm_id in sorted_nodes:
            preds = list(macro_dag.predecessors(comm_id))
            # If predecessors are placed, try to place in the same cluster
            # to minimize inter-cluster communication
            best_cluster = None
            if preds:
                pred_cluster = placements.get(preds[0])
                if pred_cluster:
                    best_cluster = pred_cluster

            if not best_cluster:
                # Simple greedy placement: find cluster with most available CPU
                best_cluster = max(self.federation.clusters.keys(),
                                 key=lambda cid: sum(n.cpu.level for n in self.federation.clusters[cid].nodes))
            
            placements[comm_id] = best_cluster
        return placements

    class LCA:
        """Local Cerebrum Agent: performs proactive scheduling within a cluster."""
        def __init__(self, parent_scheduler, cluster_id):
            self.scheduler = parent_scheduler
            self.env = parent_scheduler.env
            self.cluster_id = cluster_id
            self.cluster = parent_scheduler.federation.clusters[cluster_id]
            self.node_load_history = {node.id: [] for node in self.cluster.nodes}

        def _predict_future_load(self, node_id):
            """Simple moving average predictor."""
            history = self.node_load_history[node_id]
            if len(history) < 5:
                # Not enough data, assume current load persists
                node = next(n for n in self.cluster.nodes if n.id == node_id)
                return node.get_cpu_utilization()
            
            # Predict based on the average of the last 5 readings
            return np.mean([h[1] for h in history[-5:]])

        def _calculate_utility_score(self, task, node):
            """
            Simulates a trained RL agent's policy by calculating a utility score.
            Lower score is better.
            """
            # Proactive check
            predicted_cpu_util = self._predict_future_load(node.id)
            predicted_free_cpu = node.cpu_capacity * (1 - predicted_cpu_util)

            if node.cpu.level < task.cpu_req or node.mem.level < task.mem_req:
                return float('inf') # Infeasible
            if predicted_free_cpu < task.cpu_req:
                 # High penalty for scheduling on a node predicted to be busy
                return float('inf') 

            w = self.scheduler.policy_weights
            
            # Performance component (lower is better)
            # Factors: contention + image pull time
            contention_factor = 1 / node.cpu.level
            image_pull_time = 0 if task.image in node.image_cache else \
                (CONTAINER_IMAGE_SIZE * 8) / NETWORK_BANDWIDTH_INTRA_CLUSTER
            perf_score = contention_factor + image_pull_time

            # Energy component (lower is better)
            # Power draw if task is added
            future_util = (node.cpu_capacity - node.cpu.level + task.cpu_req) / node.cpu_capacity
            energy_score = node.power_model(future_util)

            # Cost component (lower is better)
            cost_score = node.cost_per_hour

            # Weighted sum
            utility = (w['w_perf'] * perf_score +
                       w['w_energy'] * energy_score +
                       w['w_cost'] * cost_score)
            
            return utility

        def schedule_micro_dag(self, micro_dag):
            """Schedules tasks of a micro-dag onto nodes in its cluster."""
            placements = {}
            sorted_tasks = list(nx.topological_sort(micro_dag))
            
            for task_id in sorted_tasks:
                task = micro_dag.nodes[task_id]['task_obj']
                
                best_node = None
                min_score = float('inf')

                for node in self.cluster.nodes:
                    score = self._calculate_utility_score(task, node)
                    if score < min_score:
                        min_score = score
                        best_node = node
                
                if best_node:
                    placements[task_id] = (self.cluster_id, best_node.id)
                    # "Reserve" resources for planning subsequent tasks in the same micro-dag
                    best_node.cpu.get(task.cpu_req)
                    best_node.mem.get(task.mem_req)
                else:
                    # No suitable node found, mark as failed (or handle differently)
                    placements[task_id] = (self.cluster_id, None)

            # Release the "reserved" resources after planning is done
            for task_id, placement in placements.items():
                if placement[1] is not None:
                    task = micro_dag.nodes[task_id]['task_obj']
                    node = next(n for n in self.cluster.nodes if n.id == placement[1])
                    node.cpu.put(task.cpu_req)
                    node.mem.put(task.mem_req)

            return placements

# --- BASELINE SCHEDULERS ---

class NetworkAwareHeuristicScheduler(BaseScheduler):
    """A baseline that tries to co-locate data-intensive tasks."""
    def __init__(self, env, federation):
        super().__init__(env, federation)
        self.name = "Network-Aware Heuristic"
        self.decision_latencies = []

    def schedule(self, workflow):
        start_time = time.time()
        placements = {}
        sorted_tasks = list(nx.topological_sort(workflow.dag))
        
        all_nodes = self.federation.get_all_nodes()

        for task_id in sorted_tasks:
            task = workflow.tasks[task_id]
            
            # Heuristic: try to place on the same node as the heaviest data-producing predecessor
            best_node = None
            max_data = -1
            for pred_id in workflow.dag.predecessors(task_id):
                pred_placement = placements.get(pred_id)
                if pred_placement and pred_placement[1] is not None:
                    data_size = workflow.dag[pred_id][task_id]['data_size']
                    if data_size > max_data:
                        max_data = data_size
                        # Find the node object for this placement
                        pred_node = next((n for n in all_nodes if n.id == pred_placement[1]), None)
                        if pred_node and pred_node.cpu.level >= task.cpu_req and pred_node.mem.level >= task.mem_req:
                            best_node = pred_node

            # If no suitable predecessor placement, find first available node
            if not best_node:
                for node in sorted(all_nodes, key=lambda n: n.cpu.level, reverse=True):
                    if node.cpu.level >= task.cpu_req and node.mem.level >= task.mem_req:
                        best_node = node
                        break
            
            if best_node:
                placements[task_id] = (best_node.cluster_id, best_node.id)
                # Temporarily reserve for planning
                best_node.cpu.get(task.cpu_req)
                best_node.mem.get(task.mem_req)
            else:
                placements[task_id] = (None, None)

        # Release temporary reservations
        for task_id, placement in placements.items():
            if placement[1] is not None:
                task = workflow.tasks[task_id]
                node = next(n for n in all_nodes if n.id == placement[1])
                node.cpu.put(task.cpu_req)
                node.mem.put(task.mem_req)
        
        end_time = time.time()
        self.decision_latencies.append((end_time - start_time) * 1000)
        return placements

class FLBlockScheduler(NetworkAwareHeuristicScheduler):
    """
    Simulates a scheduler that uses Federated Learning with a Blockchain layer.
    Inherits basic logic but adds significant decision latency.
    """
    def __init__(self, env, federation):
        super().__init__(env, federation)
        self.name = "FL-Block"
    
    def schedule(self, workflow):
        # Simulate high latency due to blockchain consensus
        self.env.process(self.env.timeout(FL_BLOCK_LATENCY))
        return super().schedule(workflow)