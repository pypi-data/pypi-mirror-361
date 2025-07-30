# EdgeFedSim: A Simulator for Federated Edge-Cloud Environments


EdgeFedSim is a Python-based simulation framework for modeling and evaluating workflow scheduling strategies in a federated edge-cloud computing environment. It is built upon the `simpy` discrete-event simulation library and allows for detailed modeling of infrastructure, applications, and scheduling policies.

The simulator is designed to assess the performance of different schedulers based on key metrics such as makespan, energy consumption, cost, and scheduling latency.

## Features

*   **Federated Infrastructure Model**: Simulates a hierarchical environment composed of multiple edge and cloud clusters.
*   **Detailed Resource Modeling**: Nodes are defined by CPU and memory capacity, with distinct power consumption models (idle and max) and hourly costs.
*   **Realistic Network Simulation**: Models network latency and bandwidth for both intra-cluster (within a cluster) and inter-cluster (between clusters) communication.
*   **Complex Application Workflows**: Applications are modeled as Directed Acyclic Graphs (DAGs) of tasks, with dependencies and data transfer sizes between them.
*   **Extensible Scheduler Architecture**: Provides a base scheduler class to easily implement and plug in new scheduling algorithms.
*   **Configurable Experiments**: All simulation parameters, from infrastructure setup to workflow characteristics, are managed through a central `config.yaml` file.
*   **Built-in Schedulers for Comparison**: Includes several implemented schedulers:
    *   **Cerebrum**: A hierarchical scheduler that decomposes workflows and uses policy-based (performance, energy, cost, balanced) utility functions for placement.
    *   **Network-Aware Heuristic**: A scheduler that prioritizes placing tasks on the same node as their largest data dependency.
    *   **FL-Block**: A variant of the network-aware scheduler that introduces a fixed latency, mimicking federated learning cycles.
*   **Comprehensive Metrics Reporting**: Automatically calculates and displays key performance indicators (KPIs) like average workflow makespan, energy usage (kJ), financial cost ($), and scheduling decision latency (ms).

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ahmadpanah/EdgeFedSim.git
    cd EdgeFedSim
    ```

2.  **Install the required Python packages:**
    It is recommended to use a virtual environment.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    ```

## Usage

The main entry point for running simulations is `main.py`. By default, it runs an experiment comparing the built-in schedulers and prints a summary of the results.

To run the simulation, execute the following command:

```bash
python main.py
```

The script will output the results for each scheduler and finish with an overall comparison table.

```
--- Overall Comparison ---
+---------------------------+--------------------+-------------------+--------------+--------------------+
| Scheduler                 |   Avg Makespan (s) |   Avg Energy (kJ) |   Avg Cost ($) |   Avg Latency (ms) |
+===========================+====================+===================+==============+====================+
| Network-Aware Heuristic   |             129.55 |           3881.33 |        $21.78 |               0.15 |
| FL-Block                  |             129.56 |           3881.33 |        $21.78 |               0.14 |
| Cerebrum (balanced)       |              97.94 |           3311.11 |        $13.43 |               1.54 |
| Cerebrum (performance)    |              97.94 |           3311.11 |        $13.43 |               1.49 |
| Cerebrum (energy)         |              97.94 |           3311.11 |        $13.43 |               1.49 |
| Cerebrum (cost)           |              97.94 |           3311.11 |        $13.43 |               1.49 |
+---------------------------+--------------------+-------------------+--------------+--------------------+
```
*(Note: Results may vary based on the configuration.)*

## Configuration

The simulation behavior is controlled by the `config.yaml` file. Here you can adjust parameters for the infrastructure, workflows, and schedulers.

### Key Configuration Parameters:

*   **`infrastructure`**:
    *   `node_configs`: Defines CPU and memory capacities for different node types (e.g., `small_edge`, `large_cloud`).
    *   `cluster_configs`: Specifies the composition of each cluster type (e.g., number of nodes and their type).
    *   `network_*`: Sets latency (ms) and bandwidth (Mbps) for intra- and inter-cluster networks.
    *   `*_node_cost_per_hour`: Defines the operational cost for edge and cloud nodes.

*   **`workflow`**:
    *   `num_workflows`: The total number of workflows to simulate.
    *   `min_tasks`, `max_tasks`: The range for the number of tasks in each workflow.
    *   `task_*_range`: Defines the range for CPU/memory requirements, runtime, and data sizes for tasks.

*   **`scheduler`**:
    *   `cerebrum_policy_weights`: Sets the weights for performance, energy, and cost for the different `Cerebrum` scheduler policies.
    *   `fl_block_latency`: The additional scheduling latency for the `FL-Block` scheduler.

## Project Structure

```
EdgeFedSim/
│
├── .github/workflows/      # GitHub Actions for CI/CD
│
├── examples/schedulers/    # Example implementations of custom schedulers
│   ├── LeastLoadedScheduler.py
│   ├── Network-AwareScheduler.py
│   └── RandomScheduler.py
│
├── application.py          # Defines Task and Workflow classes
├── config.yaml             # Central configuration file for the simulation
├── infrastructure.py       # Defines Federation, Cluster, Node, and Network classes
├── main.py                 # Main script to run experiments
├── requirements.txt        # Python package dependencies
├── scheduler.py            # Implementation of the core scheduling algorithms
├── simulation.py           # Core simulation logic orchestrating the environment
└── utils.py                # Utility functions and configuration loader
```

## How to Extend

### Adding a New Scheduler

You can easily add your own custom scheduler to the framework:

1.  Create a new Python file in the `examples/schedulers/` directory or another location.
2.  Define a class that inherits from `AbstractScheduler` (from `edgefedsim/schedulers/abstract_scheduler.py`).
3.  Implement the `schedule` method as required by your logic. See the provided examples for the expected signature.
4.  Import your new scheduler in `main.py` and add it to the experiment runs.

Here is a simple example of a random scheduler:

```python
# examples/schedulers/RandomScheduler.py
import random
from edgefedsim.schedulers.abstract_scheduler import AbstractScheduler # Or import BaseScheduler

class RandomScheduler(AbstractScheduler):
    def schedule(self, current_time, ready_tasks, federation_state):
        placements = []
        all_nodes = list(federation_state.nodes.values())

        for task in ready_tasks:
            suitable_nodes = [
                node for node in all_nodes
                if node.resources["cpu_mips"] >= task.requirements["cpu_mips"]
            ]

            if suitable_nodes:
                selected_node = random.choice(suitable_nodes)
                placements.append((task, selected_node))
        return placements
```

## Dependencies

The project relies on the following Python libraries:

*   `simpy`: For discrete-event simulation.
*   `networkx`: For creating and managing DAG-based workflows.
*   `numpy`: For numerical operations and random number generation.
*   `python-louvain`: For community detection in the Cerebrum scheduler.
*   `tabulate`: For printing formatted result tables.
*   `pyyaml`: For parsing the `config.yaml` file.

## License

This project is distributed under the MIT License. See the `LICENSE` file for more details.
