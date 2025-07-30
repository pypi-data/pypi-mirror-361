# infrastructure.py

import simpy
from edgefedsim.utils import *

class Network:
    """Models the network connecting clusters."""
    def __init__(self, env):
        self.env = env
        self.latencies = {}
        self.bandwidths = {}

    def get_transfer_time(self, from_cluster_id, to_cluster_id, data_size_mb):
        """Calculates data transfer time in seconds."""
        # Convert data size from Megabytes to Megabits
        data_size_mbits = data_size_mb * 8
        
        if from_cluster_id == to_cluster_id:
            latency = NETWORK_LATENCY_INTRA_CLUSTER / 1000  # to seconds
            bandwidth = NETWORK_BANDWIDTH_INTRA_CLUSTER     # Mbps
        else:
            latency = NETWORK_LATENCY_INTER_CLUSTER / 1000  # to seconds
            bandwidth = NETWORK_BANDWIDTH_INTER_CLUSTER     # Mbps
            
        transfer_time = latency + (data_size_mbits / bandwidth)
        return transfer_time

class Node:
    """Models a single compute node (e.g., a VM or physical server)."""
    def __init__(self, env, node_id, cluster_id, config):
        self.env = env
        self.id = node_id
        self.cluster_id = cluster_id
        
        self.cpu_capacity, self.mem_capacity = NODE_CONFIGS[config]
        self.cpu = simpy.Container(env, capacity=self.cpu_capacity, init=self.cpu_capacity)
        self.mem = simpy.Container(env, capacity=self.mem_capacity, init=self.mem_capacity)

        self.image_cache = set()
        self.power_model = lambda util: POWER_IDLE_CPU + (POWER_MAX_CPU - POWER_IDLE_CPU) * util
        
        self.cost_per_hour = CLOUD_NODE_COST_PER_HOUR if "Cloud" in self.cluster_id else EDGE_NODE_COST_PER_HOUR
        
        # For metrics
        self.utilization_history = []
        self.total_energy_consumed = 0.0 # in Joules

    def get_cpu_utilization(self):
        return (self.cpu_capacity - self.cpu.level) / self.cpu_capacity

    def update_energy_consumption(self, last_update_time):
        """Calculate energy consumed since the last update."""
        time_delta = self.env.now - last_update_time
        if time_delta > 0:
            current_power = self.power_model(self.get_cpu_utilization()) # in Watts (Joules/sec)
            energy_joules = current_power * time_delta
            self.total_energy_consumed += energy_joules
        
class Cluster:
    """Models a cluster of nodes."""
    def __init__(self, env, cluster_id, config_name):
        self.env = env
        self.id = cluster_id
        self.type = config_name
        
        node_type = CLUSTER_CONFIGS[config_name]["type"]
        node_count = CLUSTER_CONFIGS[config_name]["count"]
        
        self.nodes = [Node(env, f"{cluster_id}_node_{i}", cluster_id, node_type) for i in range(node_count)]

class Federation:
    """Models the entire federation of clusters."""
    def __init__(self, env):
        self.env = env
        self.clusters = {}
        self.network = Network(env)
        
        cluster_definitions = [
            ("Cloud", "Cloud"),
            ("Factory_Floor_1", "Factory_Floor"), ("Factory_Floor_2", "Factory_Floor"), ("Factory_Floor_3", "Factory_Floor"),
            ("Retail_Edge_1", "Retail_Edge"), ("Retail_Edge_2", "Retail_Edge"), ("Retail_Edge_3", "Retail_Edge"),
            ("Retail_Edge_4", "Retail_Edge"), ("Retail_Edge_5", "Retail_Edge"), ("Retail_Edge_6", "Retail_Edge"),
        ]
        
        for cid, ctype in cluster_definitions:
            self.clusters[cid] = Cluster(env, cid, ctype)

    def get_all_nodes(self):
        all_nodes = []
        for cluster in self.clusters.values():
            all_nodes.extend(cluster.nodes)
        return all_nodes