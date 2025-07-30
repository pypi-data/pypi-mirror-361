# simulation.py

import simpy
import numpy as np
import networkx as nx
from collections import defaultdict

from edgefedsim.application import Workflow
from edgefedsim.utils import *
from edgefedsim.infrastructure import Federation
from edgefedsim.scheduler import CerebrumScheduler, NetworkAwareHeuristicScheduler, FLBlockScheduler

class Simulation:
    def __init__(self, env, scheduler_class, policy='balanced'):
        self.env = env
        self.federation = Federation(env)
        if scheduler_class == CerebrumScheduler:
            self.scheduler = scheduler_class(env, self.federation, policy)
        else:
            self.scheduler = scheduler_class(env, self.federation)
        
        self.workflows_to_run = self._generate_workflows()
        self.completed_workflows = []
        
        # For metrics
        self.metrics = {
            'completed_workflows': 0,
            'total_makespan': 0,
            'total_energy': 0,
            'total_cost': 0,
        }

    def _generate_workflows(self):
        """Generates a list of workflow objects."""
        return [Workflow(f"wf_{i}", np.random.randint(MIN_TASKS, MAX_TASKS))
                for i in range(NUM_WORKFLOWS)]

    def _execute_task(self, task, placement, workflow):
        """SimPy process for a single task's lifecycle."""
        cluster_id, node_id = placement
        
        if node_id is None:
            # Scheduling failed for this task
            print(f"{self.env.now:.2f}: Task {task.id} failed to schedule.")
            task.end_time = self.env.now
            return

        node = next(n for n in self.federation.clusters[cluster_id].nodes if n.id == node_id)
        
        # 1. Data transfer from predecessors
        max_transfer_time = 0
        for pred_id in workflow.dag.predecessors(task.id):
            pred_task = workflow.tasks[pred_id]
            pred_cluster_id, _ = pred_task.placement
            data_size = workflow.dag[pred_id][task.id]['data_size']
            transfer_time = self.federation.network.get_transfer_time(pred_cluster_id, cluster_id, data_size)
            max_transfer_time = max(max_transfer_time, transfer_time)
        
        if max_transfer_time > 0:
            yield self.env.timeout(max_transfer_time)
            
        # 2. Image pull (if not cached)
        if task.image not in node.image_cache:
            pull_time = self.federation.network.get_transfer_time(
                "Cloud", cluster_id, CONTAINER_IMAGE_SIZE
            )
            yield self.env.timeout(pull_time)
            node.image_cache.add(task.image)

        task.start_time = self.env.now

        # 3. Resource acquisition and execution
        last_energy_update = self.env.now
        with node.cpu.get(task.cpu_req) as cpu_req, node.mem.get(task.mem_req) as mem_req:
            yield cpu_req
            yield mem_req
            
            node.update_energy_consumption(last_energy_update)
            last_energy_update = self.env.now

            # Actual execution
            yield self.env.timeout(task.base_runtime)

            # 4. Resource release
            node.update_energy_consumption(last_energy_update)
            last_energy_update = self.env.now

        task.end_time = self.env.now

    def _execute_workflow(self, workflow):
        """SimPy process to manage the execution of an entire workflow."""
        workflow.submit_time = self.env.now
        print(f"{self.env.now:.2f}: Workflow {workflow.id} submitted.")

        # Get the complete schedule for the workflow
        placements = self.scheduler.schedule(workflow)

        for task_id, placement in placements.items():
            workflow.tasks[task_id].placement = placement
        
        # Use an event-based progression through the DAG
        task_events = {task_id: self.env.event() for task_id in workflow.dag.nodes()}

        for task_id in nx.topological_sort(workflow.dag):
            task = workflow.tasks[task_id]
            
            # Wait for all predecessors to finish
            predecessor_events = [task_events[pred_id] for pred_id in workflow.dag.predecessors(task_id)]
            if predecessor_events:
                yield self.env.all_of(predecessor_events)
            
            # Start task execution process
            self.env.process(self._execute_task(task, task.placement, workflow)).callbacks.append(
                lambda event, tid=task_id: task_events[tid].succeed()
            )

        # Wait for all exit tasks to complete
        exit_task_events = [task_events[tid] for tid in workflow.exit_nodes]
        yield self.env.all_of(exit_task_events)

        workflow.completion_time = self.env.now
        
        # Calculate final metrics for this workflow
        all_nodes = self.federation.get_all_nodes()
        workflow.total_energy = sum(n.total_energy_consumed for n in all_nodes)
        workflow.total_cost = sum(n.cost_per_hour * (self.env.now / 3600) for n in all_nodes if n.cost_per_hour > 0)

        # Reset node-specific metrics for the next workflow if simulating sequentially
        # In a continuous simulation, this would be handled differently
        for node in all_nodes:
            node.total_energy_consumed = 0

        self.completed_workflows.append(workflow)
        print(f"{self.env.now:.2f}: Workflow {workflow.id} completed. Makespan: {workflow.makespan:.2f}s")

    def _monitor_resources(self):
        """Periodically records node utilization for proactive schedulers."""
        while True:
            if isinstance(self.scheduler, CerebrumScheduler):
                for cid, lca in self.scheduler.lcas.items():
                    for node in self.federation.clusters[cid].nodes:
                        util = node.get_cpu_utilization()
                        lca.node_load_history[node.id].append((self.env.now, util))
                        # Keep history from becoming too large
                        if len(lca.node_load_history[node.id]) > 100:
                            lca.node_load_history[node.id].pop(0)
            yield self.env.timeout(10) # Record every 10 seconds

    def run(self):
        """Main simulation entry point. Submits workflows and waits for all to complete, with a max timeout."""
        print(f"--- Starting Simulation with {self.scheduler.name} ---")
        self.env.process(self._monitor_resources())

        workflow_events = []
        # Submit workflows over time and collect their completion events
        for i, workflow in enumerate(self.workflows_to_run):
            proc = self.env.process(self._execute_workflow(workflow))
            workflow_events.append(proc)
            # Stagger workflow arrivals
            yield self.env.timeout(np.random.exponential(WORKFLOW_ARRIVAL_RATE))

        # Wait for all workflows to complete, or until sim_duration is reached
        completion = self.env.all_of(workflow_events)
        timeout = self.env.timeout(SIM_DURATION)
        result = yield self.env.any_of([completion, timeout])
        if timeout in result:
            print(f"\nSimulation stopped after reaching max duration ({SIM_DURATION} seconds). Some workflows may not have finished.")
        else:
            print("\nAll workflows completed.")
        
    def print_results(self):
        num_completed = len(self.completed_workflows)
        if num_completed == 0:
            print("No workflows were completed.")
            return

        avg_makespan = np.mean([w.makespan for w in self.completed_workflows])
        avg_energy = np.mean([w.total_energy for w in self.completed_workflows]) / 1000 # to kJ
        avg_cost = np.mean([w.total_cost for w in self.completed_workflows])
        
        if hasattr(self.scheduler, 'decision_latencies') and self.scheduler.decision_latencies:
            avg_latency = np.mean(self.scheduler.decision_latencies)
        else:
            avg_latency = 0

        print("\n--- Simulation Results ---")
        print(f"Scheduler: {self.scheduler.name}")
        print(f"Completed Workflows: {num_completed}")
        print(f"Average Makespan: {avg_makespan:.2f} s")
        print(f"Average Energy: {avg_energy:.2f} kJ")
        print(f"Average Cost: ${avg_cost:.2f}")
        print(f"Average Scheduling Latency: {avg_latency:.2f} ms")

        return {
            'scheduler': self.scheduler.name,
            'makespan': avg_makespan,
            'energy': avg_energy,
            'cost': avg_cost,
            'latency': avg_latency
        }