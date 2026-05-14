#!/bin/bash
set -e

# NAMD 3.0.2 MPI-SMP source build workflow

# Expected file in the current directory:
#   NAMD_3.0.2_Source.tar.gz

# Before running this script, load a working MPI environment.

#   module purge
#   module load <openmpi-or-hpcx-module>

# Required tools:
#   mpicxx
#   make
#   wget
#   cmake

# If cmake is not available through the environment,
#  it can be installed in user space:

#   python3 -m pip install --user cmake
#   export PATH="$HOME/.local/bin:$PATH"

which mpicxx
which make
which wget
which cmake

# extract NAMD source

tar -xzf NAMD_3.0.2_Source.tar.gz

cd NAMD_3.0.2_Source

# extract charm++
tar -xf charm-8.0.0.tar

cd charm-8.0.0

# building charm++ MPI-SMP version

env MPICXX=mpicxx ./build charm++ mpi-linux-x86_64-smp --with-production

cd ..

# FFTW and TCL - necessary libraries

wget -nc http://www.ks.uiuc.edu/Research/namd/libraries/fftw-linux-x86_64.tar.gz

wget -nc http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64.tar.gz

wget -nc http://www.ks.uiuc.edu/Research/namd/libraries/tcl8.5.9-linux-x86_64-threaded.tar.gz

tar xzf fftw-linux-x86_64.tar.gz
mv linux-x86_64 fftw

tar xzf tcl8.5.9-linux-x86_64.tar.gz
tar xzf tcl8.5.9-linux-x86_64-threaded.tar.gz

mv tcl8.5.9-linux-x86_64 tcl
mv tcl8.5.9-linux-x86_64-threaded tcl-threaded

SOURCE_ROOT="$(pwd)"

# edit the configuration files

cat > arch/Linux-x86_64.tcl <<EOF
TCLDIR=${SOURCE_ROOT}/tcl-threaded
TCLINCL=-I\$(TCLDIR)/include
TCLLIB=-L\$(TCLDIR)/lib -ltcl8.5 -ldl -lpthread
TCLFLAGS=-DNAMD_TCL
TCL=\$(TCLINCL) \$(TCLFLAGS)
EOF

cat > arch/Linux-x86_64.fftw <<EOF
FFTDIR=${SOURCE_ROOT}/fftw
FFTINCL=-I\$(FFTDIR)/include
FFTLIB=-L\$(FFTDIR)/lib -lsrfftw -lsfftw
FFTFLAGS=-DNAMD_FFTW
FFT=\$(FFTINCL) \$(FFTFLAGS)
EOF

# build and compile

sed -i "s|^CHARMBASE.*|CHARMBASE = ${SOURCE_ROOT}/charm-8.0.0|" Make.charm

./config Linux-x86_64-g++ --charm-arch mpi-linux-x86_64-smp

cd Linux-x86_64-g++

make -j4

# or just make but its slower
