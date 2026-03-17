# Report: Running NAMD on a Single Node with Apptainer at HPC

## Objective

The goal of this work was to run **NAMD** inside an **Apptainer container** on the **HPC cluster** using **a single compute node**. 

---

## 1. Checking Apptainer Availability

The first step was to verify whether Apptainer was available on the system.

Initial checks with the module system suggested that there was no `apptainer` module loaded. However, direct inspection showed that Apptainer was already installed system-wide and accessible from the command line.

This established that no extra module loading was required and Apptainer could be used directly.

**Conclusion:** Apptainer was already installed and usable on the cluster.

---

## 2. Choosing the NAMD Version

Several NAMD builds were available, including manually compiled versions, MPI variants, SMP variants, and prebuilt binaries.

For this first container test, the safest choice was the **prebuilt NAMD 3.0.2 multicore package**, because:

- it was already organized as a runtime directory,
- it included the main `namd3` executable,
- it avoided the extra complexity of MPI,
- it was better suited for a single-node test.

The selected runtime directory was:

`/home/k/kemec/namd3/NAMD_3.0.2_Linux-x86_64-multicore`

**Conclusion:** The prebuilt multicore NAMD package was selected as the base for the container.

---

## 3. Inspecting Dependencies

Before building the container, the selected `namd3` binary was checked with `ldd` to understand its runtime dependencies.

This confirmed that the executable worked on the host system and revealed a dependency related to `libgdrapi.so`, which later explained a preload warning observed inside the container.

The warning did not prevent NAMD from starting, so it was treated as an environment issue rather than a blocking runtime error.

**Conclusion:** The binary was valid on the host, and its main dependencies were identified before containerization.

---

## 4. Preparing the ApoA1 Test Case

To validate the workflow, the built-in **ApoA1 example** was used.

The necessary input files were copied into a separate run directory so that the original example directory would remain untouched. This also made the test cleaner and easier to reproduce.

The selected input file was `apoa1.namd`, and it referenced all required files through relative paths. Because of that, it was important to run NAMD from the same working directory that contained the input files.

**Conclusion:** A clean and isolated run directory was prepared for the ApoA1 test.

---

## 5. Building the Apptainer Image

A simple Apptainer definition file was created using a Rocky Linux 9 base image. The prebuilt NAMD multicore runtime directory was copied into the container under `/opt/namd`.

The image was then successfully built as a `.sif` file.

This produced a portable container image containing the NAMD runtime environment.

**Conclusion:** The Apptainer image was built successfully.

---

## 6. Testing the Container Interactively

After building the image, an interactive shell was opened inside the container.

From there, `namd3` was started without an input file. NAMD launched correctly and reported that no simulation config file had been specified. This was actually the expected behavior for this test and confirmed that the executable was working properly inside the container.

A preload warning related to `libgdrapi.so` also appeared. To minimize host environment interference, later runs used the `-e` option with Apptainer so that the container environment would be cleaner.

**Conclusion:** NAMD was confirmed to start correctly inside the container.

---

## 7. Binding the Input Directory

Because the simulation input files were stored on the host file system, the run directory had to be made visible inside the container with a bind mount.

The host run directory was bound to a working path inside the container. This allowed NAMD to read the input files and write the output files while still keeping the data on the host side.

This step was essential because the container was used only for the application environment, not for storing simulation data.

**Conclusion:** The host run directory was successfully exposed inside the container.

---

## 8. Running the Test Inside the Container

With the bind mount in place, NAMD was executed inside the container from the bound working directory.

This was important because the ApoA1 input file used relative paths for structure, coordinates, and parameter files. Running from the correct working directory ensured that all those references resolved properly.

The test began successfully and started printing energy information, which showed that the simulation was progressing normally.

**Conclusion:** The ApoA1 simulation ran successfully inside the container.

---

## 9. Moving from Login Node to Compute Node

The first direct test was run from the login environment, which was useful only for validation. For a proper HPC workflow, the simulation then had to be submitted to a compute node through the scheduler.

Since Slurm had been used previously on the same system, the workflow used to Slurm.

**Conclusion:** The scheduler in practice was Slurm, not LSF, for this workflow.

---

## 10. Submitting the Job with Slurm

A Slurm job script was prepared for a **single-node** run with **4 CPU cores**.

The job was submitted with `sbatch` and accepted by the scheduler. The running job was then observed with `squeue` and `sacct`.

The job was assigned to a real compute node, confirming that the simulation was no longer running on the login node.

**Conclusion:** The containerized NAMD job was successfully launched on a compute node through Slurm.

---

## 11. Verifying Successful Completion

The simulation output was monitored through the Slurm output file. At the end of the run, NAMD wrote the final coordinate, velocity, and extended system files and exited normally.

Final checks showed that:

- the Slurm job finished with `COMPLETED`,
- the exit code was `0:0`,
- the error file was empty,
- the expected NAMD output files were created in the host run directory.

This confirmed that the entire workflow had worked correctly from start to finish.

**Conclusion:** The single-node containerized NAMD run completed successfully without errors.

---

## Final Result

At the end of this work, a complete and working workflow was established for running **NAMD 3.0.2 multicore** inside an **Apptainer container** on **CNAF HPC** using **a single Slurm-allocated compute node**.

The following were successfully validated:

1. Apptainer was available and usable on the cluster.
2. A prebuilt NAMD multicore runtime could be containerized.
3. NAMD ran correctly inside the Apptainer image.
4. Host input/output directories could be handled through bind mounts.
5. The ApoA1 example executed correctly inside the container.
6. The simulation could be submitted and completed successfully through Slurm on a compute node.

This provides a solid foundation for organizing the workflow more cleanly and, later on, for investigating more advanced setups such as SMP tuning or MPI-based multi-node execution.


# NAMD with Apptainer on CNAF HPC (Single Node)

## Objective

The goal of this work is to run NAMD on the HPC cluster using Apptainer containers on a single node.

Previously, multi-node runs with OpenMPI were failing, so the focus here is to first establish a stable single-node workflow using a container-based setup.

## Context

- HPC system: CNAF
- Scheduler: Slurm
- Container runtime: Apptainer (already installed on the system)
- NAMD version: 3.0.2 multicore (prebuilt binary)

The work is based on the ApoA1 example system provided with NAMD.

- Also Apptainer is available system-wide and can be used directly without loading any module.

## Selecting the NAMD Version

Several different NAMD installations were available, including:

- NAMD 2 and NAMD 3
- MPI-based builds
- SMP builds
- manually compiled versions
- prebuilt binary distributions

Since previous attempts with MPI resulted in errors (especially in multi-node runs), I decided to avoid MPI for now and focus on a simpler and more stable setup.

For this reason, I selected the prebuilt NAMD 3.0.2 multicore version. This version does not require MPI and is designed to run on a single node using multiple CPU cores.

The selected directory was:

/home/k/kemec/namd3/NAMD_3.0.2_Linux-x86_64-multicore

This version already contained the `namd3` executable and all required runtime files, making it suitable for containerization without additional compilation steps.

Conclusion: The multicore (non-MPI) NAMD 3.0.2 version was chosen as the base for the container in order to ensure a stable single-node workflow.

## Preparing the Test System (ApoA1)

To test the workflow, I used the ApoA1 example.

Instead of working directly in the original example directory, I created a separate run directory and copied only the required input files. This was done to keep the original files unchanged and to have a clean working environment.

The following files were used:

- apoa1.namd
- apoa1.pdb
- apoa1.psf
- parameter files

The input file uses relative paths, so it is important to run NAMD from the same directory where these files are located.

Conclusion: A clean and isolated working directory was prepared for running the ApoA1 test.


## Building the Apptainer Container

To run NAMD in a controlled and reproducible environment, I created an Apptainer container.

Instead of compiling NAMD inside the container, I used the prebuilt multicore NAMD directory and included it directly in the container.

A simple Apptainer definition file was created for image. The NAMD directory was copied into the container and placed under a standard location.

After preparing the definition file, the container image was built as a `.sif` file.

This produced a portable container that includes the NAMD executable and its runtime environment.

Conclusion: A working Apptainer image containing NAMD 3.0.2 multicore was successfully created.


## Binding the Working Directory

In order to run the simulation inside the container, the input files stored on the host system must be accessible from within the container.

By default, the container has its own isolated filesystem, so the host working directory needs to be explicitly bound into the container environment.

For this purpose, the run directory containing the ApoA1 input files was mounted into the container at runtime. This allowed NAMD to read the input files and write output files directly to the host filesystem.

It was also necessary to run NAMD from the correct working directory inside the container, since the input file uses relative paths.

Conclusion: The host run directory was successfully bound into the container, enabling proper input/output handling.

## Running NAMD Inside the Container

After binding the working directory, I executed NAMD inside the container to verify that the full workflow was functional.

The simulation was started from the bound working directory to ensure that all input files referenced with relative paths could be accessed correctly.

NAMD began running normally and started printing energy values, indicating that the simulation was progressing as expected.

This confirmed that the container, input files, and bind configuration were all working together correctly.

Conclusion: The ApoA1 test simulation successfully started and ran inside the Apptainer container.

## SLURM Job

I prepared a Slurm job script. This script defines the required computational resources, such as the number of CPUs and runtime limits.

The job was configured to use a single node with multiple CPU cores, matching the multicore version of NAMD.

The container was executed inside the job script, and the working directory was bound in the same way as in the interactive test.

After submitting the job using `sbatch`, the simulation was assigned to a compute node and started running successfully.

Conclusion: The containerized NAMD simulation was successfully executed on a compute node using Slurm.

## Final Run and Output Verification

After preparing a clean workflow and updating the input configuration, the final simulation was executed using a Slurm job on a single compute node with 12 CPU cores.

The number of simulation steps was increased to 5000, and trajectory output was enabled to generate a DCD file for visualization and analysis.

The job completed successfully without errors. NAMD reached the final step and terminated normally, indicating a stable execution.

The trajectory file confirms that the simulation produced time-dependent data, and the presence of all output files indicates that the run was completed correctly.

Performance information was also printed in the output, showing the simulation speed and resource usage.

Conclusion: The full workflow — from container setup to HPC execution — was successfully completed, and the simulation produced valid output files including trajectory data.
