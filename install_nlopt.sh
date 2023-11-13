#! /bin/bash

# Install NLopt
#https://nlopt.readthedocs.io/en/latest/

source .venv/bin/activate
PYTHON_INTERP_PATH=${which python}

source deactivate

mkdir ./nlopt_build
cd ./nlopt_build || exit
wget https://github.com/stevengj/nlopt/archive/v2.7.1.tar.gz
tar -xvf v2.7.1.tar.gz
cd nlopt-2.7.1 || exit

cmake -DNLOPT_GUILE=OFF -DNLOPT_MATLAB=OFF -DNLOPT_OCTAVE=OFF -DNLOPT_TESTS=OFF -DPYTHON_EXECUTABLE="$PYTHON_INTERP_PATH"
make
make install