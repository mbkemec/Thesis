# NAMD 3.0.2 Installation and ApoA1 Test on CNAF HPC

**Author:** Barkın Kemec  
**Cluster:** CNAF INFN HPC  
**Login node:** `ui-terabit.cr.cnaf.infn.it`  
**Scheduler:** SLURM  
**MPI stack:** OpenMPI / HPC-X  
**Date:** 2026-03-10

---
`https://www.ks.uiuc.edu/Research/namd/3.0.2/download/564278/NAMD_3.0.2_Source.tar.gz`

## Overview

This document records the full workflow used to:

1. Install and test **NAMD 3.0.2 multicore binary**
2. Download and run the **ApoA1 benchmark**
3. Transfer files to local machine and visualize with **VMD**
4. Build **NAMD 3.0.2 from source**
5. Build both:
   - **MPI non-SMP**
   - **MPI-SMP**
6. Test single-node and multi-node execution on CNAF
7. Summarize working and non-working configurations

This file is intended both as:
- a personal technical log
- a report that can be shown to supervisors/instructors

---

# Part A — Precompiled NAMD 3.0.2 Multicore

## 1. Create a working directory

```bash
mkdir ~/namd3
cd ~/namd3
```

## 2. Download the Precompiled Binary

Downloaded binary used:

`NAMD_3.0.2_Linux-x86_64-multicore.tar.gz`

Extract it:

```bash
tar -xzf NAMD_3.0.2_Linux-x86_64-multicore.tar.gz
cd NAMD_3.0.2_Linux-x86_64-multicore
ls
```

Expected files include:

- `namd3`
- `charmrun`
- `psfgen`
- `flipdcd`
- `flipbinpdb`
- `sortreplicas`

---

## 3. Verify that the Binary Runs

Run:

```bash
./namd3
```

Expected behavior:

- program starts
- prints NAMD version info
- stops with:

```
FATAL ERROR: No simulation config file specified on command line.
```

This is expected and confirms the binary is working.

---

# Part B — ApoA1 Benchmark with Precompiled Multicore Version

## 4. Download ApoA1 Benchmark

Go back to the workspace:

```bash
cd ~/namd3
```

Download:

```bash
wget --no-check-certificate https://www.ks.uiuc.edu/Research/namd/utilities/apoa1.tar.gz
```

Extract:

```bash
tar -xvzf apoa1.tar.gz
cd apoa1
ls
```

Important files inside:

- `apoa1.namd`
- `apoa1.psf`
- `apoa1.pdb`
- `par_all22_prot_lipid.xplor`
- `par_all22_popc.xplor`

## 5. Fix Output Path Inside `apoa1.namd`

Original file had:

```
outputname           /usr/tmp/apoa1-out
```

This was changed to:

```
outputname           apoa1-out
```

This ensures output files are written in the current working directory.

---

## 6. Run ApoA1 with Multicore NAMD Using SLURM

Job file:

```bash
nano apoa1.job
```

Contents:

```bash
#!/bin/bash
#SBATCH --job-name=apoa1
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --output=apoa1.out

cd $SLURM_SUBMIT_DIR

~/namd3/NAMD_3.0.2_Linux-x86_64-multicore/namd3 +p8 apoa1.namd > apoa1.log
```

Submit:

```bash
sbatch apoa1.job
```

Check queue:

```bash
squeue -u kemec
```

---

## 7. Output Files Produced by Multicore Run

The following files were generated:

- `apoa1.log`
- `apoa1.out`
- `apoa1-out.coor`
- `apoa1-out.vel`
- `apoa1-out.xsc`

No `.dcd` trajectory was produced because the input file did not contain `DCDfile` / `DCDfreq`.

# Part C — Copy Files to Local Machine and Visualize in VMD

## 8. Transfer Files from CNAF to Local Machine

Because access uses a bastion host, files were transferred with `scp -J`.

Important hostnames:

Bastion:

```
bastion.cnaf.infn.it
```

Login node:

```
ui-terabit.cr.cnaf.infn.it
```

Example transfer commands from local machine:

```bash
scp -J kemec@bastion.cnaf.infn.it kemec@ui-terabit.cr.cnaf.infn.it:~/namd3/apoa1/apoa1.psf .
scp -J kemec@bastion.cnaf.infn.it kemec@ui-terabit.cr.cnaf.infn.it:~/namd3/apoa1/apoa1.pdb .
scp -J kemec@bastion.cnaf.infn.it kemec@ui-terabit.cr.cnaf.infn.it:~/namd3/apoa1/apoa1-out.coor .
```

Main files needed for visualization:

- `apoa1.psf`
- `apoa1.pdb`
- `apoa1-out.coor`

---

## 9. Install VMD on Local Ubuntu Machine

Downloaded package used:

```
vmd-1.9.4a57.bin.LINUXAMD64-CUDA102-OptiX650-OSPRay185.opengl.tar.gz
```

Installation steps:

```bash
cd ~/Downloads
tar -xzf vmd-1.9.4a57.bin.LINUXAMD64-CUDA102-OptiX650-OSPRay185.opengl.tar.gz
cd vmd-1.9.4a57
./configure
cd src
sudo make install
```

Verify installation:

```bash
which vmd
vmd
```

---

## 10. Load ApoA1 in VMD

Inside VMD:

```
File -> New Molecule
```

Load files in this order:

```
apoa1.psf
apoa1.pdb
```

Recommended representations:

Protein

```
Selected Atoms: protein
Drawing Method: NewCartoon
Coloring Method: Structure
```

Lipids

```
Selected Atoms: lipid
Drawing Method: Lines
Coloring Method: Name
```

This correctly displayed the ApoA1 nanodisc system.

# Part D — NAMD 3.0.2 Source Build (MPI)

## 11. Create a New Directory for Source Build

A separate source-build directory was created to avoid mixing with the multicore binary installation.

```bash
mkdir -p ~/namd3_mpi
cd ~/namd3_mpi
```

---

## 12. Place Source Tarball There

Source file used:

```
NAMD_3.0.2_Source.tar.gz
```

Extract:

```bash
tar -xzf NAMD_3.0.2_Source.tar.gz
cd NAMD_3.0.2_Source
```

Contents included:

- `charm-8.0.0.tar`
- `arch`
- `config`
- `src`
- `Make.charm`
- `Makefile`

---

## 13. Check MPI Toolchain

Checked tools:

```bash
which mpicxx
which mpirun
mpicxx --version
mpirun --version
gcc --version
g++ --version
make --version
```

Observed environment:

- `mpicxx` from **HPC-X / OpenMPI**
- `mpirun` from **HPC-X / OpenMPI**
- **GCC / G++** available
- **GNU Make** available

---

## 14. Extract Charm++ Source

```bash
tar -xf charm-8.0.0.tar
```

Result:

```
NAMD_3.0.2_Source/charm-8.0.0
```

## 15. Install `cmake` Locally with `pip`

Charm++ build initially failed because `cmake` was not found, and fallback build required missing `autoconf` / `automake`.

Installed `cmake` in user space:

```bash
python3 -m pip install --user cmake
```

Then added it to `PATH`:

```bash
export PATH=$HOME/.local/bin:$PATH
hash -r
which cmake
cmake --version
```

Recommended permanent addition:

```bash
echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

---

## 16. Build Charm++ (MPI non-SMP)

Go to Charm++ directory:

```bash
cd ~/namd3_mpi/NAMD_3.0.2_Source/charm-8.0.0
```

Build:

```bash
env MPICXX=mpicxx ./build charm++ mpi-linux-x86_64 --with-production
```

Expected result:

```
Build successful.
```

Produced directory:

```
mpi-linux-x86_64
```

---

## 17. Build and Run Charm++ Megatest (Single Node)

Go to megatest directory:

```bash
cd ~/namd3_mpi/NAMD_3.0.2_Source/charm-8.0.0/mpi-linux-x86_64/tests/charm++/megatest
```

Build:

```bash
make
```

This produced:

```
megatest
```

Single-node SLURM test:

```bash
nano megatest.job
```

Job file contents:

```bash
#!/bin/bash
#SBATCH --job-name=megatest
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=megatest.out

cd $SLURM_SUBMIT_DIR

srun --mpi=pmix ./megatest
```

Submit:

```bash
sbatch megatest.job
```

Result:

- `megatest` passed on **1 node**
- All Charm++ tests completed successfully

---

## 18. Download FFTW and TCL for Source Build

Return to source directory:

```bash
cd ~/namd3_mpi/NAMD_3.0.2_Source
```

Download:

```bash
wget http://www.ks.uiuc.edu/Research/namd/libraries/fftw-linux-x86_64.tar.gz
wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64.tar.gz
wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64-threaded.tar.gz
```

Extract and rename:

```bash
tar xzf fftw-linux-x86_64.tar.gz
mv linux-x86_64 fftw

tar xzf tcl8.5.9-linux-x86_64.tar.gz
tar xzf tcl8.5.9-linux-x86_64-threaded.tar.gz

mv tcl8.5.9-linux-x86_64 tcl
mv tcl8.5.9-linux-x86_64-threaded tcl-threaded
```

---

## 19. Configure and Build NAMD (MPI non-SMP)

Configure:

```bash
./config Linux-x86_64-g++ --charm-arch mpi-linux-x86_64
```

Enter build directory:

```bash
cd Linux-x86_64-g++
```

Compile:

```bash
make -j4
```

Result:

```
namd3
```

This produced a working **MPI non-SMP binary**.

# Part E — Testing NAMD MPI (non-SMP)

## 20. Single-node ApoA1 Test with MPI non-SMP

In ApoA1 directory:

```bash
cd ~/namd3/apoa1
```

Job file:

```bash
nano apoa1_mpi_1n_debug.job
```

Contents:

```bash
#!/bin/bash
#SBATCH --job-name=apoa1_mpi_1n
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=apoa1_mpi_1n.out

cd $SLURM_SUBMIT_DIR

echo "SLURM_JOB_NODELIST=$SLURM_JOB_NODELIST"
srun --mpi=pmix hostname

srun --mpi=pmix ~/namd3_mpi/NAMD_3.0.2_Source/Linux-x86_64-g++/namd3 apoa1.namd
```

This run worked:

- `ENERGY:` lines appeared
- Output files were produced

---

## 21. Multi-node Tests with MPI non-SMP

2-node and 4-node tests were attempted with both:

```
srun --mpi=pmix
```

and

```
mpirun --bind-to none
```

Observed behavior:

- `mpirun -n 2 hostname` worked across nodes
- `megatest` on 2 nodes **hung**
- `NAMD` on 2 nodes **hung**
- `NAMD` on 4 nodes **hung**

Conclusion:

- Single-node MPI works
- Multi-node MPI communication does **not work correctly**

The issue appears to be **cluster/runtime related**, not a build error in NAMD itself.

---

# Part F — NAMD 3.0.2 Source Build (MPI-SMP)

## 22. Create a Separate Directory for SMP Build

```bash
mkdir -p ~/namd3_smp
cd ~/namd3_smp
```

Copy source tarball there and extract:

```bash
cp ~/namd3_mpi/NAMD_3.0.2_Source.tar.gz .
tar -xzf NAMD_3.0.2_Source.tar.gz
cd NAMD_3.0.2_Source
```

Extract Charm++:

```bash
tar -xf charm-8.0.0.tar
```

---

## 23. Build Charm++ MPI-SMP

Go to Charm++ directory:

```bash
cd charm-8.0.0
```

Build:

```bash
env MPICXX=mpicxx ./build charm++ mpi-linux-x86_64-smp --with-production
```

Result:

```
Build successful.
```

Produced directory:

```
mpi-linux-x86_64-smp
```

---

## 24. Download FFTW and TCL Again for SMP Source Tree

In the SMP source tree, the same FFTW and TCL packages were downloaded and extracted:

```bash
cd ~/namd3_smp/NAMD_3.0.2_Source

wget http://www.ks.uiuc.edu/Research/namd/libraries/fftw-linux-x86_64.tar.gz
wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64.tar.gz
wget http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64-threaded.tar.gz

tar xzf fftw-linux-x86_64.tar.gz
mv linux-x86_64 fftw

tar xzf tcl8.5.9-linux-x86_64.tar.gz
tar xzf tcl8.5.9-linux-x86_64-threaded.tar.gz

mv tcl8.5.9-linux-x86_64 tcl
mv tcl8.5.9-linux-x86_64-threaded tcl-threaded
```

## 25. Fix Wrong Paths in Source Files

The source tree contained hard-coded old paths like:

```
/Projects/namd2/...
```

These had to be corrected.

### `arch/Linux-x86_64.tcl`

Final content:

```
TCLDIR=/home/k/kemec/namd3_smp/NAMD_3.0.2_Source/tcl-threaded
TCLINCL=-I$(TCLDIR)/include
TCLLIB=-L$(TCLDIR)/lib -ltcl8.5 -ldl -lpthread
TCLFLAGS=-DNAMD_TCL
TCL=$(TCLINCL) $(TCLFLAGS)
```

### `arch/Linux-x86_64.fftw`

Final content:

```
FFTDIR=/home/k/kemec/namd3_smp/NAMD_3.0.2_Source/fftw
FFTINCL=-I$(FFTDIR)/include
FFTLIB=-L$(FFTDIR)/lib -lsrfftw -lsfftw
FFTFLAGS=-DNAMD_FFTW
FFT=$(FFTINCL) $(FFTFLAGS)
```

### `Make.charm`

The `CHARMBASE` line was corrected to:

```
CHARMBASE = /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/charm-8.0.0
```

---

## 26. Verify Required Files Exist

Checks used:

```bash
ls /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/tcl-threaded/include/tcl.h
ls /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/tcl-threaded/lib
ls /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/fftw/include
ls /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/fftw/lib
ls -d /home/k/kemec/namd3_smp/NAMD_3.0.2_Source/charm-8.0.0/mpi-linux-x86_64-smp
```

All required files were present.

---

## 27. Configure and Build NAMD (MPI-SMP)

Clean old build directory:

```bash
rm -rf Linux-x86_64-g++
```

Configure:

```bash
./config Linux-x86_64-g++ --charm-arch mpi-linux-x86_64-smp
```

Enter build directory:

```bash
cd Linux-x86_64-g++
```

Compile:

```bash
make -j4
```

Result:

```
namd3
```

A working **MPI-SMP binary** was produced.

---

# Part G — Testing NAMD MPI-SMP

## 28. Single-node MPI-SMP Test

In ApoA1 directory, set:

```
outputname           apoa1-mpi-smp-1n
```

Job file used:

```bash
nano apoa1_mpi_smp_1n.job
```

Contents:

```bash
#!/bin/bash
#SBATCH --job-name=apoa1_smp_1n
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --output=apoa1_mpi_smp_1n.out

cd $SLURM_SUBMIT_DIR

echo "SLURM_JOB_NODELIST=$SLURM_JOB_NODELIST"
srun --mpi=pmix hostname

echo "Starting NAMD SMP on 1 node..."
srun --mpi=pmix ~/namd3_smp/NAMD_3.0.2_Source/Linux-x86_64-g++/namd3 apoa1.namd
echo "Finished with exit code $?"
```

This run worked:

- Startup completed
- `ENERGY:` lines appeared
- Output files were generated

## 29. Multi-node MPI-SMP Test

A 2-node SMP job was also tested with:

```bash
mpirun --bind-to none -n 2 ~/namd3_smp/NAMD_3.0.2_Source/Linux-x86_64-g++/namd3 +ppn 3 apoa1.namd
```

and also with: `srun --mpi=pmix`.

Observed behavior:

- Startup messages / hostnames appeared
- No `ENERGY:` lines appeared
- Run did not proceed correctly across nodes

Conclusion:

- Single-node MPI-SMP works
- Multi-node MPI-SMP does **not work correctly** on this cluster setup

---

# Part H — Summary of What Works and What Does Not

## Working Configurations

### 1. Precompiled Multicore Binary

- Works on **1 node**
- Works through **SLURM**
- **ApoA1** runs successfully

### 2. Source-built MPI non-SMP

- Builds successfully
- Works on **1 node**
- ApoA1 works on **1 node**

### 3. Source-built MPI-SMP

- Builds successfully
- Works on **1 node**
- ApoA1 works on **1 node**
- `ENERGY:` lines appear
- Output files are generated

---

## Not Working Correctly

### Multi-node MPI non-SMP

- `hostname` across multiple nodes works
- Charm++ **megatest across multiple nodes hangs**
- **NAMD across multiple nodes hangs**

### Multi-node MPI-SMP

- Same issue
- No proper multi-node NAMD progression observed

---

# Part I — Technical Conclusion

The source builds themselves are successful.

The evidence strongly suggests:

- The **NAMD build is correct**
- The **Charm++ build is correct**
- The **single-node MPI runtime is correct**

The remaining problem is likely related to:

```
CNAF multi-node OpenMPI / HPC-X / UCX runtime configuration
```

This conclusion is supported by the fact that:

- `mpirun -n 2 hostname` works
- But real multi-node MPI communication in **megatest** and **NAMD** does not

Therefore, the multi-node issue appears to be **runtime/environment-related**, not a simple source-build mistake.

---

# Part J — Recommended Message for Supervisor / Support

A short technical summary that can be sent:

```
I successfully built NAMD 3.0.2 from source on CNAF, both in MPI and MPI-SMP modes.
Single-node runs work correctly for both builds, including the ApoA1 benchmark.
However, multi-node runs do not progress correctly.

Simple tests like `mpirun -n 2 hostname` work across nodes, but real MPI communication tests
(Charm++ megatest and NAMD itself) hang on 2 nodes and above.

This suggests the problem is likely related to the CNAF multi-node MPI/HPC-X/UCX runtime
configuration rather than the NAMD build itself.
```

---

# Part K — Important Files

## Precompiled Multicore Installation

```
~/namd3/NAMD_3.0.2_Linux-x86_64-multicore/namd3
```

## MPI non-SMP Build

```
~/namd3_mpi/NAMD_3.0.2_Source/Linux-x86_64-g++/namd3
```

## MPI-SMP Build

```
~/namd3_smp/NAMD_3.0.2_Source/Linux-x86_64-g++/namd3
```

## ApoA1 Benchmark Directory

```
~/namd3/apoa1
```

---

# Part L — Notes for Future Work

Possible next steps:

1. Ask cluster support / supervisor about the correct **multi-node MPI launch settings** on CNAF
2. Check whether specific **environment modules** are required for multi-node Charm++ / NAMD
3. Try trajectory output by adding:

```
DCDfile apoa1.dcd
DCDfreq 10
```

to `apoa1.namd`

4. Visualize generated trajectory in **VMD**

5. Compare performance of:

- Multicore
- MPI non-SMP
- MPI-SMP

on a **single node**
