#!/bin/bash
#$ -M ylu28@nd.edu
#$ -m ae
#$ -q long
#$ -N base_case_PCM_test
conda activate PCM0826
export LD_LIBRARY_PATH=~/.conda/envs/regen/lib:$LD_LIBRARY_PATH 
module load gurobi
module load ipopt/3.14.2 
python ./base_pcm_test.py
