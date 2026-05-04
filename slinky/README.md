# Slinky Summary

## 1. What is Slinky?

Slinky is a project developed by SchedMD (the main developers of Slurm), with support from NVIDIA.

Its main goal is to integrate two different worlds:

- Kubernetes (K8s) → cloud-native applications and containers  
- Slurm → high-performance computing (HPC) workloads  

In simple terms:

Slinky tries to combine cloud computing (Kubernetes) with HPC computing (Slurm).

---

## 2. Why do we need Slinky?

Kubernetes and Slurm are both workload managers, but they are designed for different purposes.

### Kubernetes is good at:
- Running containers and microservices  
- Long-running applications (e.g. APIs, web services)  
- Flexible resource usage  
- Scaling dynamically  

### Slurm is good at:
- Batch jobs (finite jobs with clear start/end)  
- Multi-node and MPI workloads  
- GPU-heavy computations  
- Strict scheduling policies (queues, priorities, fair-share)  

---

### The Problem

Modern workloads (especially AI and bioinformatics) often require both:

- A frontend or orchestration layer → Kubernetes  
- A compute-heavy backend → Slurm (HPC cluster)

Without integration, these two systems remain isolated.

---

### Slinky Solution

Slinky enables Kubernetes and Slurm to work together instead of operating as completely separate systems.

---

## 3. Core Idea of Slinky

Slinky does not simply mean:

“Kubernetes sends jobs to any external Slurm cluster.”

Instead, Slinky focuses on tight integration between Kubernetes and Slurm.

From the documentation, Slinky mainly supports:

1. Running Slurm inside Kubernetes  
2. Sharing the same infrastructure between Kubernetes and Slurm  
3. Using Slurm as a scheduler for Kubernetes workloads  

---

## 4. Main Components of Slinky

Slinky consists of three main parts:

1. slurm-operator  
2. slurm-bridge  
3. slinky-containers  

Each component addresses a different aspect of integration.

---

## 5. slurm-operator (Run Slurm inside Kubernetes)

This component allows deployment and management of a full Slurm cluster inside Kubernetes.

### Idea

Instead of having a separate HPC cluster, a Slurm cluster is created inside Kubernetes:

```text
Kubernetes cluster
   └── Slurm cluster (as pods)
```

### What runs as containers?

- slurmctld (controller)  
- slurmd (worker nodes)  
- slurmdbd (accounting)  
- slurmrestd (API)  
- login nodes  

### How it works

- A Kubernetes operator watches the cluster  
- It automatically creates and manages Slurm components  
- It uses Custom Resource Definitions (CRDs) such as NodeSet and LoginSet  

In this model, Kubernetes acts as the infrastructure layer for Slurm.

---

## 6. slurm-bridge (Use Slurm as Kubernetes Scheduler)

This component allows Kubernetes workloads to be scheduled by Slurm.

### Idea

Instead of Kubernetes deciding where a pod runs, Slurm takes over scheduling decisions.

---

### How it works

1. A Kubernetes pod is submitted  
2. slurm-bridge intercepts the request  
3. The pod is translated into a Slurm job (placeholder)  
4. Slurm schedules the job  
5. Once resources are allocated, the pod is executed  

---

### Flow

```text
Kubernetes Pod
   ↓
Slurm Bridge
   ↓
Slurm Job (placeholder)
   ↓
Slurm scheduler allocates resources
   ↓
Pod runs on allocated node
```

---

### Important Detail

- Slurm decides when and where resources are allocated  
- Kubernetes is still responsible for running the container  

In other words:

```text
Slurm = resource allocator  
Kubernetes = execution engine
```

---

### Key Assumption

slurm-bridge assumes that:

```text
Kubernetes nodes == Slurm nodes
```

This means:

- The same hardware is shared  
- Nodes run both kubelet and slurmd  
- Kubernetes and Slurm operate on the same cluster  

---
## 7. slinky-containers

This component provides ready-to-use container images for Slurm components.

Examples include:

- slurmctld  
- slurmd  
- slurmdbd  
- slurmrestd  
- login nodes  
- slurm-bridge components  

### Purpose

These containers are used to:

- Run Slurm components inside Kubernetes  
- Support slurm-operator and slurm-bridge deployments  

They are not a standalone integration solution, but rather supporting building blocks for the Slinky ecosystem.

---

## 8. Comparison with Our Thesis Use-Case

Our project follows a different architecture.

### Our Current Setup

We already have:

- A Kubernetes cluster (RKE2)  
- A production Slurm HPC cluster (CNAF)  
- MinIO (S3-compatible storage)  

---

### Our Goal

```text
Kubernetes application
   ↓
Submit job to external Slurm cluster
   ↓
Execution on HPC compute nodes
   ↓
Data exchange via MinIO/S3
```

---

## 9. Key Differences

### Slinky (Current Design)

```text
Kubernetes and Slurm are tightly integrated
Same infrastructure and shared nodes
```

### Our Project

```text
Kubernetes and Slurm are separate systems
External job submission and execution
```

---

### Detailed Comparison

| Feature | Slinky | Our Project |
|--------|--------|------------|
| Slurm location | Inside or co-located with Kubernetes | External HPC cluster |
| Execution | Kubernetes nodes | HPC compute nodes |
| Scheduling | Slurm integrated with K8s | Slurm external |
| Integration type | Tight coupling | Loose coupling (offloading) |

---

## 10. Key Insight

Slinky mainly solves the following problem:

> How to integrate Slurm into Kubernetes environments.

Our project focuses on a different problem:

> How to connect Kubernetes to an already existing external Slurm cluster.

---

## 11. Final Takeaway

Slinky is a powerful system for combining Kubernetes and Slurm, especially when:

- A cloud-native HPC environment is desired  
- Infrastructure is shared between systems  
- Both Kubernetes and Slurm are under the same control  

However, our use-case differs:

> We are not creating or embedding a Slurm cluster — we are connecting to an existing one.

---

## 12. Main Question for the Meeting

The key question to ask is:

> Can Slinky be extended to support job submission and monitoring on an external Slurm cluster, instead of only tightly integrated deployments?

---

## 13. Why This is Important

This distinction is important because:

- It reflects real-world infrastructure setups  
- It is not fully solved by current tools  
- It represents a potential research contribution  

This makes it directly relevant for our thesis work.
