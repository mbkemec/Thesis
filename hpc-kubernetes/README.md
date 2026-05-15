# HPC - Kubernetes Integration Workflows

This section contains the HPC orchestration and Kubernetes integration workflows developed during the MSc thesis project.

The objective of this work was to investigate how containerized scientific workloads can be submitted from Kubernetes-oriented environments to Slurm-managed HPC infrastructure while using S3-compatible object storage as the shared data layer.

The workflows focused on:

- Slurm-based HPC job orchestration
- Kubernetes-to-HPC communication concepts
- SSH ProxyJump workflows
- OIDC-based temporary credential usage
- S3-compatible storage integration
- Apptainer-based execution
- automated job submission pipelines
- reproducible execution environments

The implementation was designed as a lightweight orchestration prototype rather than a production-ready scheduler integration framework.

---

# Architecture Overview

The following diagram summarizes the broader project architecture and the interaction between Kubernetes environments, Slurm-managed HPC infrastructure, authentication components, and S3-compatible object storage.

![Project Architecture](project_architecture.png)

The overall workflow combines:

- Kubernetes-side orchestration concepts
- Slurm-based HPC execution
- temporary authentication credentials
- object storage communication
- containerized scientific workloads

The architecture was used as a conceptual reference throughout the project while developing the orchestration pipeline.

---

# Current Implemented Workflow

The following diagram represents the currently implemented execution workflow used during testing.

![Current Workflow](job_path.png)

The implemented pipeline follows these main steps:

1. temporary credentials are generated using an OIDC-based workflow
2. credentials are transferred through SSH-based communication
3. a bridge VM is used as an SSH jump host
4. jobs are submitted through the HPC login node
5. Slurm schedules execution on compute nodes
6. workloads execute inside Apptainer containers
7. input/output data is exchanged through S3-compatible storage

This workflow was successfully used to execute NAMD-based molecular dynamics workloads on GPU-enabled HPC nodes.

---

# Repository Contents

```text
hpc-kubernetes/
├── README.md
├── job_path.png
├── project_architecture.png
└── scripts/
```

# Scripts

| Script                                                           | Description                     |
| ---------------------------------------------------------------- | ------------------------------- |
| [`run_hpc_namd_pipeline.py`](./scripts/run_hpc_namd_pipeline.py) | Main orchestration entry point  |
| [`config.py`](./scripts/config.py)                               | Centralized configuration       |
| [`hpc_client.py`](./scripts/hpc_client.py)                       | SSH ProxyJump communication     |
| [`slurm_template.py`](./scripts/slurm_template.py)               | Dynamic Slurm script generation |


The `scripts/` directory contains the orchestration and automation components used during workflow testing between the Kubernetes-oriented environment and the Slurm-based HPC infrastructure.

The workflow was later modularized into multiple Python components in order to improve readability, maintainability, and debugging.

---

## Main Entry Point

The primary execution script is:

- [`run_hpc_namd_pipeline.py`](./scripts/run_hpc_namd_pipeline.py)

This is the main orchestration script intended to be executed by the user.

The script handles:

* OIDC agent initialization
* temporary credential generation
* SSH communication setup
* remote workflow generation
* Slurm job submission
* remote job monitoring
* output collection orchestration

The other Python files are helper modules imported by this script and are not intended to be executed directly.

Example execution:

```bash
python3 run_hpc_namd_pipeline.py
```

---

## Script Components

### Configuration

- [`config.py`](./scripts/config.py)

Contains centralized configuration values used across the workflow.

This includes:

* bridge VM information
* HPC login node configuration
* object storage endpoint configuration
* dataset definitions
* GPU/CPU resource settings
* container image paths
* working directory definitions

This file allows the workflow configuration to be modified without changing the main orchestration logic.

---

### Remote HPC Communication

- [`hpc_client.py`](./scripts/hpc_client.py)

Handles SSH-based remote communication with the HPC environment.

The module provides:

* SSH ProxyJump support
* remote shell execution
* retry handling
* connection timeout handling
* remote workflow execution

This component is responsible for connecting to the HPC login node through the bridge VM.

---

### Slurm Template Generation

- [`slurm_template.py`](./scripts/slurm_template.py)

Dynamically generates:

* Slurm job scripts
* remote execution scripts

The generated scripts automate:

* dataset download from object storage
* temporary credential loading
* Apptainer execution
* GPU-enabled NAMD execution
* output collection
* metadata generation
* automatic upload of results/logs

The generated Slurm script is submitted remotely through the HPC login node.

---

### `login_sts.py`

Used for temporary credential generation through an external OIDC/STS workflow.

This component was developed separately and is therefore not included in this public repository.

The orchestration workflow expects this script to generate temporary object-storage credentials before remote job submission.

---

## Shell-Based Workflow

An earlier shell-based implementation was also developed during the initial stages of testing.

- [`submit_namd_cuda_workflow.sh`](./scripts/submit_namd_cuda_workflow.sh)

This version contained the complete workflow inside a single Bash script.

The later Python-based modular implementation replaced this approach in order to improve:

* readability
* maintainability
* debugging
* workflow modularity

---

## Workflow Behavior

The orchestration pipeline performs the following steps automatically:

1. generate temporary credentials
2. establish SSH communication through the bridge VM
3. connect to the HPC login node
4. generate a Slurm job script dynamically
5. submit the job with `sbatch`
6. wait for job completion
7. execute the workload inside an Apptainer container
8. upload logs, outputs, and metadata to object storage

The workflow was validated using CUDA-enabled NAMD molecular dynamics workloads on GPU-enabled HPC nodes.

