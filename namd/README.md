# NAMD Workflows

## Overview

This section contains the NAMD-based molecular dynamics workflows developed during the MSc thesis project.

NAMD was used as the scientific application for evaluating HPC execution, containerized workflows, MPI-based execution models, GPU acceleration, and performance testing across different runtime configurations.

The work included:

- execution of ApoA1 molecular dynamics simulations
- execution of STMV molecular dynamics simulations
- single-node and multi-node experiments
- CPU-only and GPU-accelerated workflows
- source-built and precompiled NAMD versions
- MPI and MPI-SMP execution models
- Slurm-based job execution
- containerized NAMD workflows with Apptainer
- performance testing and scaling experiments

The NAMD workflows provided a realistic computational biology workload for investigating scalability, execution behavior, and orchestration across HPC environments.

---

## Repository Contents

```text
namd/
├── README.md
├── scripts/
├── performance_tests/
└── figures/
```

---

## Objectives

The primary objectives of the NAMD workflows were:

- validating scientific workloads on HPC infrastructure
- testing Slurm-based execution workflows
- investigating MPI and distributed execution behavior
- evaluating CPU and GPU performance scaling
- analyzing single-node and multi-node execution
- integrating NAMD with Apptainer container workflows
- generating reproducible execution environments

The experiments were also used to better understand runtime behavior, scheduler interaction, and distributed execution limitations on the available HPC infrastructure.

---

## Tested Molecular Systems

### ApoA1

The ApoA1 benchmark system was used as the primary validation workload during the early stages of testing.

ApoA1 was used for:

- validating NAMD execution
- testing Slurm job submission
- MPI runtime testing
- container validation
- initial performance measurements

The relatively smaller system size made it suitable for rapid iteration and debugging workflows.

---

### STMV

The Satellite Tobacco Mosaic Virus (STMV) system was later used for larger-scale GPU-focused experiments.

The STMV workload was used for:

- GPU acceleration tests
- CPU/GPU balance experiments
- multi-node execution tests
- execution stability analysis
- CUDA-enabled workflows

The larger system size provided a more realistic HPC-scale molecular dynamics workload.

---

## Execution Modes

Several different NAMD execution models were investigated throughout the project.

### Precompiled Multicore Version

The precompiled NAMD 3.0.2 multicore version was initially used for stable single-node execution.

This workflow provided:

- simplified setup
- multicore CPU execution
- reliable Slurm integration
- stable ApoA1 execution

The multicore version was also later integrated into Apptainer container workflows.

---

### Source-Built MPI Version

NAMD 3.0.2 was also compiled from source using MPI-enabled Charm++ builds.

This workflow was used to investigate:

- MPI-based execution
- distributed execution behavior
- multi-node runtime configuration
- OpenMPI/HPC-X integration

Both MPI non-SMP and MPI-SMP configurations were tested.

---

### CUDA-Enabled NAMD

CUDA-enabled NAMD workflows were later tested on GPU-enabled compute nodes.

The GPU workflows focused on:

- CUDA acceleration
- CPU/GPU resource balance
- STMV execution
- multi-GPU scaling behavior
- execution optimization

These experiments demonstrated significant performance improvements compared to CPU-only execution.

---

## MPI and Multi-Node Experiments

Multiple MPI runtime configurations were investigated during the project.

The experiments included:

- single-node MPI execution
- multi-node MPI execution
- Charm++ MPI builds
- MPI-SMP builds
- OpenMPI/HPC-X runtime testing
- Slurm-based MPI launches
- `srun --mpi=pmix`
- `mpirun` execution workflows

Early multi-node experiments revealed several runtime and communication issues related to distributed execution behavior.

Initial observations showed that:

- single-node MPI execution worked correctly
- multi-node communication behavior was unstable
- Charm++ megatest could hang across nodes
- runtime configuration strongly affected execution stability

Later rebuilds using updated HPC-X environments and CUDA-enabled configurations improved execution stability and enabled larger-scale runs.

---

## Performance Testing and Scaling Experiments

The NAMD workloads were used to investigate execution behavior and performance under different CPU, GPU, and node configurations.

The experiments included:

- CPU scaling tests
- GPU scaling tests
- single-node vs multi-node execution
- CPU-only vs GPU-accelerated execution
- runtime behavior analysis
- wall-clock observations
- execution stability testing

Performance plots and execution summaries are provided in:

```text
performance_tests/
figures/
```

---

## Slurm Integration

All major NAMD workflows were executed through Slurm-managed compute nodes.

The execution workflows included:

- single-node jobs
- multi-node jobs
- CPU-only jobs
- GPU-enabled jobs
- MPI launches through Slurm
- execution automation workflows

The scheduler-based approach allowed reproducible execution and controlled resource allocation across the HPC environment.

---

## Apptainer Integration

NAMD workflows were also integrated with Apptainer-based container environments.

The containerized workflows included:

- multicore CPU execution
- CUDA-enabled execution
- bind-mounted simulation directories
- Slurm-based container execution
- portable runtime environments

Additional details about containerization workflows are documented in:

```text
../apptainer/
```

---

## Current Status

The following workflows were successfully validated:

- precompiled multicore NAMD execution
- source-built MPI NAMD execution
- MPI-SMP builds
- Slurm-based execution
- ApoA1 simulations
- STMV simulations
- CUDA-enabled execution
- Apptainer-based NAMD workflows
- CPU and GPU performance testing
- multi-node execution experiments

The project established a functional framework for running and analyzing molecular dynamics workloads across HPC infrastructure using both native and containerized execution environments.

---

## Related Components

Additional workflow components are documented in:

- `../apptainer/`
- `../slurm/`
- `../hpc-kubernetes/`

