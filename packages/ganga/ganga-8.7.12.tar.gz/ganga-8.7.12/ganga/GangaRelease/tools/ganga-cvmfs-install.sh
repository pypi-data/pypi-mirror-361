#!/bin/bash

cvmfs_server transaction ganga.cern.ch

micromamba activate

cd /cvmfs/ganga.cern.ch/Ganga/install

python -m venv $1

. $1/bin/activate

pip install --upgrade pip setuptools

pip install ganga[LHCb,Dirac]@git+https://github.com/ganga-devs/ganga.git@$1

# We need to uninstall htcondor from the default installation to use the preinstalled versions on cvmfs
pip uninstall htcondor

deactivate

micromamba deactivate

rm -f /cvmfs/ganga.cern.ch/Ganga/install/LATEST

ln -s /cvmfs/ganga.cern.ch/Ganga/install/$1 /cvmfs/ganga.cern.ch/Ganga/install/LATEST

cd ~

cvmfs_server publish ganga.cern.ch


