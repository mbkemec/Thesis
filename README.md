# MSc Thesis Repository

This repository contains the practical work, notes, scripts, and reports developed during an MSc thesis focused on integrating Kubernetes, Slurm-based HPC systems, containerized scientific applications, and S3-compatible storage for scalable bioinformatics workflows.

The work is organized into several technical areas, each representing a different part of the overall thesis workflow.

---

## 1. Kubernetes Environment

A Kubernetes environment was prepared using an RKE2-based cluster composed of one server node and multiple worker nodes.

This environment was used as the cloud-side orchestration layer of the thesis. Basic deployment workflows were tested, including services, deployments, ingress configuration, and communication between Kubernetes components.

The Kubernetes side represents the entry point from which workloads can eventually be submitted toward external HPC resources.

---

## 2. Slurm HPC Environment

The HPC side of the project is based on a Slurm-managed cluster.

Several Slurm workflows were tested, including:

- single-node job submission
- multi-node job submission
- CPU-based jobs
- GPU-based jobs
- MPI-based execution
- job monitoring with Slurm commands
- analysis of job states, logs, and resource allocation

These tests were used to understand how scientific workloads can be executed, monitored, and automated on an HPC cluster.

---

## 3. MPI and Distributed Execution Tests

MPI-based workloads were tested to evaluate distributed execution across HPC nodes.

Initial tests included simple distributed programs, followed by larger scientific workloads. These experiments helped identify the differences between local execution, single-node MPI execution, and multi-node MPI execution.

Particular attention was given to MPI environment configuration, runtime libraries, network transport behavior, and multi-node execution stability.

---

## 4. NAMD Molecular Dynamics Benchmarks

NAMD was used as the main scientific application for HPC benchmarking.

The benchmarking work included:

- running ApoA1 molecular dynamics simulations
- running STMV molecular dynamics simulations
- comparing CPU-only and GPU-accelerated configurations
- testing different CPU/GPU balances
- collecting wall-clock time and performance metrics
- generating speedup and efficiency plots
- comparing single-node and multi-node behavior

The NAMD experiments provided a realistic bioinformatics/HPC workload for evaluating performance, scalability, and execution behavior on the cluster.

---

## 5. GPU-Based NAMD Experiments

GPU-accelerated NAMD runs were performed using CUDA-enabled nodes.

Different CPU and GPU combinations were tested to understand the balance between CPU resources and GPU acceleration. The results showed that increasing GPU count alone is not always sufficient, since CPU-GPU balance and job configuration strongly affect performance.

These experiments were used to identify efficient configurations for molecular dynamics workloads on the available HPC infrastructure.

---

## 6. Visualization with VMD and FFmpeg

Simulation outputs were processed and visualized using VMD and FFmpeg.

Trajectory files produced by NAMD were rendered into molecular visualization frames using VMD. These frames were then converted into video format using FFmpeg.

This part of the work demonstrates a complete post-processing workflow after simulation execution, from raw trajectory output to visual molecular animation.

---

## 7. Apptainer-Based Containerization

Apptainer was used to containerize scientific tools for execution on the HPC cluster.

Containerized workflows included:

- VMD execution inside an Apptainer container
- FFmpeg execution inside a separate container
- binding input/output directories into containers
- running rendering and video generation workflows through Slurm jobs

This allowed scientific software to be executed in a more reproducible and portable way within the HPC environment.

---

## 8. MinIO and S3-Compatible Storage

MinIO was used as an S3-compatible storage layer for communication between systems.

The storage tests included:

- accessing MinIO from the HPC login environment
- accessing MinIO from Slurm compute jobs
- uploading and downloading files through MinIO
- testing MinIO client and AWS CLI based access
- validating object storage as a shared data exchange layer

These tests showed that MinIO can be used as an intermediate storage system between Kubernetes-side workflows and HPC-side execution.

---

## 9. Kubernetes to HPC Workflow

An end-to-end workflow was developed to connect the Kubernetes-side environment with the HPC cluster.

The workflow includes:

- initiating the process from a cloud/Kubernetes-side environment
- connecting to the HPC login environment through an intermediate access path
- dynamically generating Slurm job scripts
- submitting jobs to the HPC scheduler
- passing temporary storage credentials to the job environment
- allowing compute jobs to access S3-compatible storage
- retrieving or uploading results after job execution

This represents one of the central integration points of the thesis.

---

## 10. OIDC and Temporary Credentials

OIDC-based authentication was tested for generating temporary credentials for S3-compatible storage access.

Instead of relying on long-term static credentials, the workflow was adapted to use short-lived credentials for MinIO access. These credentials were passed to the HPC job environment so that compute nodes could interact with object storage during job execution.

This approach improves the security and flexibility of the data exchange workflow.

---

## Current Status

At the current stage, the thesis work includes:

- a working Kubernetes-side test environment
- Slurm job submission and monitoring workflows
- CPU and GPU NAMD benchmark results
- VMD and FFmpeg post-processing workflows
- Apptainer-based container execution on HPC
- MinIO access from both login and compute environments
- an end-to-end Kubernetes-to-HPC submission prototype
- OIDC-based temporary credential handling for storage access
- ongoing research on deeper Slurm-Kubernetes integration models

---

## Thesis Focus

The overall focus of the thesis is to explore how cloud-native orchestration, HPC scheduling, containerized scientific software, and object storage can be combined to support scalable and reproducible computational biology workflows.

The practical workflow connects multiple components into a single pipeline:

```text
Kubernetes / Cloud-side environment
        ↓
Bridge / access layer
        ↓
Slurm HPC cluster
        ↓
Scientific workload execution
        ↓
S3-compatible object storage
        ↓
Result collection and post-processing
```

