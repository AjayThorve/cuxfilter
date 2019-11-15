#!/bin/bash
# Copyright (c) 2018, NVIDIA CORPORATION.
#########################################
# cuDF GPU build and test script for CI #
#########################################
set -e
NUMARGS=$#
ARGS=$*

# Logger function for build status output
function logger() {
  echo -e "\n>>>> $@\n"
}

# Arg parsing function
function hasArg {
    (( ${NUMARGS} != 0 )) && (echo " ${ARGS} " | grep -q " $1 ")
}

# Set path and build parallel level
export PATH=/conda/bin:/usr/local/cuda/bin:$PATH
export PARALLEL_LEVEL=4
export CUDA_REL=${CUDA_VERSION%.*}

# Set home to the job's workspace
export HOME=$WORKSPACE

# Parse git describe
cd $WORKSPACE
export GIT_DESCRIBE_TAG=`git describe --tags`
export MINOR_VERSION=`echo $GIT_DESCRIBE_TAG | grep -o -E '([0-9]+\.[0-9]+)'`

################################################################################
# SETUP - Check environment
################################################################################

logger "Check environment..."
env

logger "Check GPU usage..."
nvidia-smi

logger "Activate conda env..."
source activate gdf
conda install "cudf=$MINOR_VERSION.*" "cudatoolkit=$CUDA_REL" \
              "numpy>=1.16" "cupy>=6.0.0" "pandas>=0.24.2,<0.25" "panel=0.6.*" \
              "bokeh>=1.2.*" "geopandas>=0.6.*" "pyproj=1.9.*" "pytest"

# Install the master version of cudatashader
logger "pip install git+https://github.com/rapidsai/cuDataShader.git --upgrade --no-deps"
pip install git+https://github.com/rapidsai/cuDataShader.git --upgrade --no-deps

logger "Check versions..."
python --version
$CC --version
$CXX --version
conda list

################################################################################
# BUILD - Build cuXfilter from source
################################################################################

logger "Build libcudf..."
$WORKSPACE/build.sh clean cuXfilter

################################################################################
# TEST - Run pytest 
################################################################################

if hasArg --skip-tests; then
    logger "Skipping Tests..."
else
    logger "Check GPU usage..."
    nvidia-smi

    cd $WORKSPACE/python/cuXfilter/tests
    logger "Python py.test for cuXfilter..."
    py.test --cache-clear --junitxml=${WORKSPACE}/junit-cuXfilter.xml -v --cov-config=.coveragerc --cov=cuXfilter --cov-report=xml:${WORKSPACE}/python/cuXfilter/cuXfilter-coverage.xml --cov-report term

fi