# Apptainer Workflows

## Overview

This section contains the Apptainer-based container workflows developed during the MSc thesis project.

Apptainer was used to provide portable and reproducible runtime environments for scientific applications executed on HPC infrastructure. The containerized workflows were primarily focused on molecular dynamics simulations, visualization, and post-processing tasks.

The work includes:

- containerized NAMD execution
- CUDA-enabled NAMD tests
- VMD-based molecular visualization
- FFmpeg-based video generation
- Slurm integration for container execution
- bind-mounted input/output workflows on HPC systems

The goal was to establish stable and reproducible execution environments for HPC workloads without relying on local software installation on compute nodes.

---

## Repository Contents

```text
apptainer/
├── README.md
└── scripts/
    ├── namd3_multicore.def
    ├── namd3_cuda.def
    ├── vmd193_text_mode.def
    └── ffmpeg_ubuntu.def
```

---

## Objectives

The main objectives of the containerization workflow were:

- simplifying scientific software deployment
- improving reproducibility across environments
- isolating runtime dependencies
- enabling portable HPC workflows
- integrating containerized applications with Slurm-based execution

The initial focus was placed on stable single-node execution before investigating more advanced distributed workflows.

---

## Definition Files

### `namd3_multicore.def`

Builds a NAMD 3.0.2 multicore container for single-node CPU execution.

This workflow was used for:

- ApoA1 / STMV simulations
- stable multicore execution
- initial Apptainer integration tests
- Slurm-based CPU jobs

The multicore version was selected because it avoided MPI-related complexity (used Infiniband) and provided a stable environment for validating the container workflow.

---

### `namd3_cuda.def`

Builds a CUDA-enabled NAMD 3.0.2 container for GPU-enabled nodes.

This workflow was used for:

- GPU-accelerated simulations
- CUDA-enabled NAMD execution
- STMV benchmark experiments
- CPU/GPU balance testing

The container includes additional runtime libraries required for CUDA-enabled and verbs-based execution environments.

The container is intended to be executed with:

```bash
apptainer exec --nv image.sif namd3 ...
```

---

### `vmd193_text_mode.def`

Builds a lightweight text-mode VMD 1.9.3 container for headless molecular rendering workflows.

A text-based VMD environment was selected because newer graphical builds introduced additional complexity and significantly increased container size.

The workflow supports:

- batch TCL execution
- TachyonInternal rendering
- trajectory visualization
- headless HPC execution

The container includes several environment and Tcl path fixes required for stable non-graphical execution.

---

### `ffmpeg_ubuntu.def`

Builds an FFmpeg container used for post-processing and video generation.

This container was used together with the VMD workflow to convert rendered molecular frames into video animations.

The resulting workflow was:

```text
NAMD simulation
      ↓
VMD frame rendering
      ↓
FFmpeg video generation
```

This established a complete visualization pipeline directly on the HPC environment.

---

## Building Images

Apptainer images can be built from the provided definition files using:

```bash
apptainer build image.sif definition.def
```

---

## Slurm Integration

The containerized applications were executed through Slurm job scripts on compute nodes.

The workflows included:

- single-node and multiple-node CPU jobs
- GPU-enabled jobs
- bind-mounted working directories
- container execution through `apptainer exec`
- output collection on the host filesystem or upload to S3-compatible object storage

The scheduler-based workflow ensured that simulations and rendering tasks were executed on allocated HPC resources rather than login environments.

---

## Data Access and Bind Mount Workflows

Bind mounts were used to expose external working directories inside the containers during execution.

This approach allowed the workflows to remain flexible with respect to data location and storage management. Simulation inputs could be provided from different sources depending on the execution scenario, including:

- host-side working directories
- shared HPC storage
- S3-compatible object storage workflows

Similarly, outputs could be written either to the host filesystem or transferred to external storage systems after execution.

Using bind-mounted execution environments provided several advantages:

- separation of runtime environment and persistent data
- reusable and lightweight containers
- flexible data management workflows
- compatibility with HPC storage and object storage systems

The containers were therefore used primarily as portable runtime environments rather than persistent storage environments.

---

## Notes

The NAMD definition files use placeholder paths such as:

```text
/path/to/NAMD_...
```

These paths must be replaced with the local NAMD runtime directory before building the image.

The VMD definition file expects the text-mode VMD 1.9.3 archive to be available locally during the build process. The archive itself is not included in this repository.


---

## Current Status

The following workflows were successfully validated:

- Apptainer execution on HPC systems
- single-node / multiple-node containerized NAMD runs
- CUDA-enabled NAMD execution
- Slurm-based container execution
- VMD text-based rendering workflows
- FFmpeg-based molecular video generation
- bind-mounted HPC data workflows

These results established a functional foundation for portable and reproducible HPC workflows based on Apptainer containers.

---

## Related Components

Additional workflow components are documented in:

- `../namd/`
- `../slurm/`
- `../hpc-kubernetes/`

