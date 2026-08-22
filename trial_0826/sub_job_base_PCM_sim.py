import os

this_file_path = os.path.dirname(os.path.realpath(__file__))

def submit_job(job_name):
    # create a directory to save job scripts
    job_scripts_dir = os.path.join(this_file_path, "sim_job_scripts")
    if not os.path.isdir(job_scripts_dir):
        os.mkdir(job_scripts_dir)

    file_name = os.path.join(job_scripts_dir, f"{job_name}.sh")
    with open(file_name, "w") as f:
        f.write(
            "#!/bin/bash\n"
            + "#$ -M ylu28@nd.edu\n"
            + "#$ -m ae\n"
            + "#$ -q long\n"
            + f"#$ -N {job_name}\n"
            + f"conda activate PCM0826\n"
            # FIXME: points at the 'regen' env, not PCM0826 — reason unknown;
            # resolve during pilot batch (doc 14 §5.2)
            + "export LD_LIBRARY_PATH=~/.conda/envs/regen/lib:$LD_LIBRARY_PATH \n"
            + "module load gurobi\n"
            + f"python ./base_pcm_test.py"
        )

    os.system(f"qsub {file_name}")

if __name__ == "__main__":
    job_name = "base_case_PCM_test"
    submit_job(job_name)
