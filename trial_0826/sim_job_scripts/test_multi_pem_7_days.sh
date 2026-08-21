#!/bin/bash
#$ -M ylu28@nd.edu
#$ -m ae
#$ -q long
#$ -N test_multi_pem_7_days
conda activate PCM0826
module load gurobi
python ./multi_PEM_PCM.py --index 7_days --output_directory multi_pem_test_7_days --retrofit_gen_dict '{"121_NUCLEAR_1": {"PEM_indifference_point": 25, "PEM_fraction": 0.5}, "303_WIND_1": {"PEM_indifference_point": 20, "PEM_fraction": 0.2, "gen_pmax": 847}, "319_PV_1": {"PEM_indifference_point": 30, "PEM_fraction": 0.3, "gen_pmax": 188.2}}'
