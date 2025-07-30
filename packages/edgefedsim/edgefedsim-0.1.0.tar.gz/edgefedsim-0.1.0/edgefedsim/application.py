# application.py

import networkx as nx
import numpy as np
from edgefedsim.utils import *

class Task:
    """Models a single containerized task."""
    def __init__(self, task_id, workflow_id):
        self.id = task_id
        self.workflow_id = workflow_id
        
        self.cpu_req = np.random.uniform(*TASK_CPU_REQ_RANGE)
        self.mem_req = np.random.uniform(*TASK_MEM_REQ_RANGE)
        self.base_runtime = np.random.uniform(*TASK_BASE_RUNTIME_RANGE)
        self.image = f"image_{np.random.randint(1, 5)}"
        
        # Placement info (filled by scheduler)
        self.placement = None # (cluster_id, node_id)
        
        # Execution metrics
        self.start_time = -1
        self.end_time = -1

class Workflow:
    """Models an application as a Directed Acyclic Graph (DAG) of tasks."""
    def __init__(self, workflow_id, num_tasks):
        self.id = workflow_id
        self.dag = nx.DiGraph()
        self.tasks = {}
        
        # Create tasks
        for i in range(num_tasks):
            task_id = f"{workflow_id}_task_{i}"
            self.tasks[task_id] = Task(task_id, workflow_id)
            self.dag.add_node(task_id, task_obj=self.tasks[task_id])

        # Create random dependencies to form a DAG
        for i in range(num_tasks):
            for j in range(i + 1, num_tasks):
                if np.random.rand() < 0.2: # probability of an edge
                    from_task = f"{workflow_id}_task_{i}"
                    to_task = f"{workflow_id}_task_{j}"
                    data_size = np.random.uniform(*TASK_DATA_SIZE_RANGE)
                    self.dag.add_edge(from_task, to_task, data_size=data_size)

        # Ensure it's a DAG (remove cycles if any, although above method avoids them)
        if not nx.is_directed_acyclic_graph(self.dag):
            # This part is a safeguard, the generation logic should not create cycles
            print(f"Warning: Workflow {self.id} is not a DAG, attempting to fix.")
            while not nx.is_directed_acyclic_graph(self.dag):
                try:
                    cycle = nx.find_cycle(self.dag)
                    self.dag.remove_edge(cycle[0][0], cycle[0][1])
                except nx.NetworkXNoCycle:
                    break

        self.entry_nodes = [n for n, d in self.dag.in_degree() if d == 0]
        self.exit_nodes = [n for n, d in self.dag.out_degree() if d == 0]

        # Execution metrics
        self.submit_time = -1
        self.completion_time = -1
        self.total_energy = 0
        self.total_cost = 0

    @property
    def makespan(self):
        return self.completion_time - self.submit_time if self.completion_time > 0 else 0