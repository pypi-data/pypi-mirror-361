# utils.py

import yaml
import os

# Load configuration from YAML file if present
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, 'r') as f:
        config = yaml.safe_load(f)
else:
    config = {}

# --- SIMULATION PARAMETERS ---
RANDOM_SEED = config.get('random_seed', 42)
SIM_DURATION = config.get('sim_duration', 10000)
WORKFLOW_ARRIVAL_RATE = config.get('workflow_arrival_rate', 15)

# --- INFRASTRUCTURE PARAMETERS ---
infra = config.get('infrastructure', {})
POWER_IDLE_CPU = infra.get('power_idle_cpu', 100)
POWER_MAX_CPU = infra.get('power_max_cpu', 250)
NODE_CONFIGS = infra.get('node_configs', {
    "small_edge": [4, 8],
    "medium_edge": [8, 16],
    "large_cloud": [32, 128]
})
CLUSTER_CONFIGS = infra.get('cluster_configs', {
    "Retail_Edge": {"type": "small_edge", "count": 5},
    "Factory_Floor": {"type": "medium_edge", "count": 10},
    "Cloud": {"type": "large_cloud", "count": 20}
})
NETWORK_LATENCY_INTRA_CLUSTER = infra.get('network_latency_intra_cluster', 1)
NETWORK_BANDWIDTH_INTRA_CLUSTER = infra.get('network_bandwidth_intra_cluster', 1000)
NETWORK_LATENCY_INTER_CLUSTER = infra.get('network_latency_inter_cluster', 50)
NETWORK_BANDWIDTH_INTER_CLUSTER = infra.get('network_bandwidth_inter_cluster', 100)
CLOUD_NODE_COST_PER_HOUR = infra.get('cloud_node_cost_per_hour', 0.20)
EDGE_NODE_COST_PER_HOUR = infra.get('edge_node_cost_per_hour', 0.0)

# --- WORKFLOW PARAMETERS ---
workflow = config.get('workflow', {})
NUM_WORKFLOWS = workflow.get('num_workflows', 200)
MIN_TASKS = workflow.get('min_tasks', 20)
MAX_TASKS = workflow.get('max_tasks', 100)
TASK_CPU_REQ_RANGE = tuple(workflow.get('task_cpu_req_range', (0.5, 2.0)))
TASK_MEM_REQ_RANGE = tuple(workflow.get('task_mem_req_range', (0.5, 2.0)))
TASK_BASE_RUNTIME_RANGE = tuple(workflow.get('task_base_runtime_range', (5, 20)))
TASK_DATA_SIZE_RANGE = tuple(workflow.get('task_data_size_range', (10, 500)))
CONTAINER_IMAGE_SIZE = workflow.get('container_image_size', 200)

# --- SCHEDULER PARAMETERS ---
sched = config.get('scheduler', {})
PREDICTION_HORIZON = sched.get('prediction_horizon', 60)
CEREBRUM_POLICY_WEIGHTS = sched.get('cerebrum_policy_weights', {
    'performance': {'w_perf': 1.0, 'w_energy': 0.0, 'w_cost': 0.0},
    'energy':      {'w_perf': 0.0, 'w_energy': 1.0, 'w_cost': 0.0},
    'cost':        {'w_perf': 0.0, 'w_energy': 0.0, 'w_cost': 1.0},
    'balanced':    {'w_perf': 0.4, 'w_energy': 0.3, 'w_cost': 0.3},
})
FL_BLOCK_LATENCY = sched.get('fl_block_latency', 0.5)