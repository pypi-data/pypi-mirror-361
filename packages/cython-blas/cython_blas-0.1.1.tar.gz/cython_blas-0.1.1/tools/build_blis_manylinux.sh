#!/bin/bash

# This script is used to build BLIS inside a manylinux container.
# The host file system is mounted as /host in the container.
# It is run by the .github/workflows/blis.yml job.

# This is the path to ./vendor/blis on the host
SRC_DIR="$1"

# Copy ./vendor/blis to container
mkdir -p /project/blis
echo "/host$SRC_DIR"
cp -r /host$SRC_DIR /project
cd /project/blis

# Configure and build
export CONFIGURE_OPTS="$CONFIGURE_OPTS --disable-shared --enable-static"
export CONFIGURE_OPTS="$CONFIGURE_OPTS --disable-blas"
export CONFIGURE_OPTS="$CONFIGURE_OPTS --disable-cblas"
export CONFIGURE_OPTS="$CONFIGURE_OPTS --enable-threading=openmp"
./configure --prefix=/opt/blis $CONFIGURE_OPTS --enable-arg-max-hack x86_64
make -j2 V=1
make install

# Copy compiled library back to host
mkdir -p /host/opt/blis
cp -r /opt/blis /host/opt/blis