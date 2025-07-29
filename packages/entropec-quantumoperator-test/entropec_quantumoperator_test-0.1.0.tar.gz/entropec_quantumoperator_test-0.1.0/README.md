# DMRG Task Client

A Python client for submitting DMRG calculation tasks to a server and polling results.

## Installation

```bash
pip install entropec-quantumoperator-test
```

## Usage Example

```python
from entropec_quantumoperator_test import DMRGClient

# Initialize client with server URL
client = DMRGClient(api_base="http://192.168.124.22:12805")

# Define task parameters
task_id = "9528"
params = {
    "CaseParams": {
        "Geometry": "OBC",
        "Lx": 3,
        "Ly": 4,
        "t": 1.0,
        "t2": -0.2,
        "J": 3.0,
        "J2": 1.0,
        "phi": 0.1,
        "mu": 0,
        "NumHole": 2,
        "Sweeps": 5,
        "Dmin": 10,
        "Dmax": 10,
        "CutOff": 1e-9,
        "LanczErr": 1e-9,
        "MaxLanczIter": 70,
        "Threads": 2,
        "noise": [0.1, 0.01],
        "Perturbation": 0.0,
        "BondSingletPairPerturbation": 0.0,
        "wavelength": 4
    }
}

# Submit task
try:
    response = client.submit_job(task_id, params)
    print("Task submitted successfully:", response)
    
    # Fetch result (with max 20 retries)
    result = client.fetch_result(task_id, max_retries=20)
    print("Calculation result:", result)
except Exception as e:
    print("Error:", str(e))
```

## API Reference

### DMRGClient

#### `__init__(api_base, timeout=10, retry_interval=5)`
Initialize a new DMRG client.

- `api_base`: Base URL of the DMRG server
- `timeout`: Request timeout in seconds (default: 10)
- `retry_interval`: Interval between result polling attempts (default: 5)

#### `submit_job(task_id, params)`
Submit a DMRG calculation task.

- `task_id`: Unique identifier for the task
- `params`: Dictionary containing calculation parameters
- Returns: Server response JSON

#### `fetch_result(task_id, max_retries=None)`
Poll for calculation results.

- `task_id`: Task identifier to fetch results for
- `max_retries`: Maximum number of retries (None for infinite)
- Returns: Calculation result text

## License
MIT License