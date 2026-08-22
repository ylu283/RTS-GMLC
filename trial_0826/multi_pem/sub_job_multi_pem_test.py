import os
import json

this_file_path = os.path.dirname(os.path.realpath(__file__))

def submit_job(index, output_directory="./multi_pem_test", retrofit_gen_dict={}):
    # create a directory to save job scripts
    job_scripts_dir = os.path.join(this_file_path, "..", "sim_job_scripts")
    if not os.path.isdir(job_scripts_dir):
        os.mkdir(job_scripts_dir)

    file_name = os.path.join(job_scripts_dir, f"test_multi_pem_{index}.sh")
    with open(file_name, "w") as f:
        f.write(
            "#!/bin/bash\n"
            + "#$ -M ylu28@nd.edu\n"
            + "#$ -m ae\n"
            + "#$ -q long\n"
            + f"#$ -N test_multi_pem_{index}\n"
            + "conda activate PCM0826\n"
            + "module load gurobi\n"
            + f"python ./multi_PEM_PCM.py --index {index} --output_directory {output_directory} --retrofit_gen_dict '{json.dumps(retrofit_gen_dict)}'\n"
        )

    os.system(f"qsub {file_name}")


if __name__ == "__main__":
    index = "7_days"
    output_directory = f"multi_pem_test_{index}"
    retrofit_gen_dict = {
        "121_NUCLEAR_1": {"PEM_bid": 25, "PEM_fraction": 0.5},
        "303_WIND_1": {"PEM_bid": 20, "PEM_fraction": 0.2, "gen_pmax": 847},
        "319_PV_1": {"PEM_bid": 30, "PEM_fraction": 0.3, "gen_pmax": 188.2},
    }
    submit_job(index, output_directory, retrofit_gen_dict)