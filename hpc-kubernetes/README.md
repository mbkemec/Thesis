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
