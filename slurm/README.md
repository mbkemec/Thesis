# Slurm Workflows

## Overview

This section contains the initial Slurm and MPI-based experiments performed during the early stages of the HPC workflow development process.

The purpose of these experiments was to:

* understand Slurm job scheduling
* test resource allocation behavior
* validate MPI execution
* investigate multi-process execution
* become familiar with distributed runtime environments on the CNAF HPC infrastructure

These workflows were later used as the foundation for the larger NAMD and Kubernetes-HPC integration experiments developed during the thesis project.

---

## Repository Structure

```text
slurm/
├── README.md
└── scripts/
    ├── basic_node_allocation.job
    ├── mpi_pi_example.cpp
    └── mpi_pi_example.job
```

---

# Basic Slurm Job Test

The first experiments focused on understanding how Slurm allocates compute resources and launches tasks across compute nodes.

The `basic_node_allocation.job` script was used to:

* allocate compute resources
* inspect node allocation
* test `srun`
* verify task execution on compute nodes

The script prints:

* allocated node names
* task hostnames
* job start and finish times

This workflow was useful for understanding the execution model later used by larger MPI and NAMD jobs.

---

## Example Execution

```bash
sbatch basic_node_allocation.job
```

---

# MPI Pi Example

A simple MPI-based numerical approximation of Pi was later implemented using C++ and OpenMPI.

The purpose of this workflow was to:

* test MPI compilation
* validate multi-process execution
* verify MPI runtime behavior under Slurm
* understand rank distribution across tasks

The implementation uses:

* `MPI_Init`
* `MPI_Comm_rank`
* `MPI_Comm_size`
* `MPI_Reduce`

to distribute the workload across MPI ranks and combine the final result.

---

## MPI Compilation

The MPI example can be compiled using:

```bash
mpicxx -O2 mpi_pi_example.cpp -o pi4
```

---

## MPI Slurm Job

The `mpi_pi_example.job` script launches the compiled MPI application using:

```bash
mpirun --bind-to none
```

The `--bind-to none` option was used because some default CPU binding configurations caused runtime errors on the target environment.

---

## Example Execution

```bash
sbatch mpi_pi_example.job
```

---

## Example Output

```text
Rank 0/4 running on xxx
Rank 1/4 running on xxx
Rank 2/4 running on xxx
Rank 3/4 running on xxx

pi = 3.14159265359022
```

---

# Runtime Observations

During the experiments, several OpenMPI and UCX-related runtime warnings were observed depending on the execution environment.

Typical observations included:

* UCX transport warnings
* network interface warnings
* CPU binding issues
* runtime environment differences between login and compute nodes

These observations later became important during larger-scale NAMD and multi-node MPI experiments.

---

# Purpose Within the Thesis Project

Although these examples are relatively small, they were important for understanding the core concepts later used throughout the thesis project:

* Slurm scheduling
* MPI execution
* distributed task launching
* process allocation
* runtime environment behavior
* HPC execution workflows

The knowledge gained from these experiments was later applied to:

* NAMD MPI workflows
* multi-node execution
* GPU-enabled workloads
* Apptainer container execution
* Kubernetes-to-Slurm orchestration workflows

---

# Related Components

Additional workflow components are documented in:

* `../namd/`
* `../apptainer/`
* `../hpc-kubernetes/`
