# This script will generate job-files for execution on a SLURM cluster.
# You can modify the template (you'll have to set the queue at the very least).
# It is also possible to just run this for a couple of days on a local machine (set submit2cluster=False).
# You might need to change variables when executing the script from a different folder than (...)/scripts/
# To change the number of iterations etc. just set the variables here:

queue_name = ?
n_iterations = {
        'bnn' : 4,
        'cartpole' : 4,
        'paramnet_surrogates' : 10,
        'svm_surrogate' : 10
        }
submit2cluster = True
optimizers = ['randomsearch', 'bohb', 'hyperband', 'smac']
experiments = ['bnn', 'cartpole', 'svm_surrogate', 'paramnet_surrogates']

##############################################################################################################
##############################################################################################################
##### no modifications should be necessary from here on to run on SLURM cluster, but adapt what you need #####
##############################################################################################################
##############################################################################################################

cluster_job_template = """#!/bin/bash
#SBATCH -p {queue_name} # partition (queue)
#SBATCH --mem 4000 # memory pool for all cores (4GB)
#SBATCH -t 1-10:00 # time (D-HH:MM)
#SBATCH -c 4 # number of cores
#SBATCH -o log/%x.%N.%j.out # STDOUT  (the folder log has to be created prior to running or this won't work)
#SBATCH -e log/%x.%N.%j.err # STDERR  (the folder log has to be created prior to running or this won't work)
#SBATCH -J {job} # sets the job name. If not specified, the file name will be used as job name
#SBATCH --mail-type=END,FAIL # (recive mails about end and timeouts/crashes of your job)
#SBATCH --array 0-3

# Print some information about the job to STDOUT
echo "Workingdir: $PWD";
echo "NOTE: Always submit from dir with run_experiment.py";
echo "Started at $(date)";
echo "Running job $SLURM_JOB_NAME using $SLURM_JOB_CPUS_PER_NODE cpus per node with given JID $SLURM_JOB_ID on queue $SLURM_JOB_PARTITION";
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID";

# Activate virtual-environment
source ~/BOHBsCAVE/.ve_BOHBsCAVE/bin/activate;

# Job to perform
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]
then
   python run_experiment.py --exp_name {exp} --run_id {run_id} --nic_name eth0 --no_worker --opt_method {opt} --dest_dir opt_results/ --max_budget {max_b} --min_budget {min_b} --n_workers 4 {additional} --num_iterations {num_it}
else
   python run_experiment.py --exp_name {exp} --run_id {run_id} --nic_name eth0 --worker --opt_method {opt} --dest_dir opt_results/ --max_budget {max_b} --min_budget {min_b} --n_workers 4 {additional} --num_iterations {num_it}
fi

# Print some Information about the end-time to STDOUT
echo "DONE";
echo "Finished at $(date)";
"""

import os
import random

def gen_script(script, job_str):
    """ This will write the script to file """
    path = 'cluster/job_' + job_str
    with open(path, 'w') as fh:
        fh.write(script)
    if submit2cluster:
        os.system('sbatch ' + path)

def run_cartpole():
    for opt in optimizers:
        job_str = '_'.join(['cartpole', opt])
        script = cluster_job_template.format(job=job_str, exp='cartpole', run_id=random.randint(1, 1000000), opt=opt,
                                    max_b=9, min_b=1, additional='',
                                    num_it=n_iterations['cartpole'], queue_name=queue_name)
        gen_script(script, job_str)

def run_svm_surrogate():
    for opt in optimizers:
        job_str = '_'.join(['svm_surrogate', opt])
        script = cluster_job_template.format(job=job_str, exp='svm_surrogate', run_id=random.randint(1, 1000000), opt=opt,
                                    max_b=1, min_b=0.001953125, additional='',
                                    num_it=n_iterations['svm_surrogate'], queue_name=queue_name)
        gen_script(script, job_str)

def run_paramnet_surrogates():
    for dataset in ['adult', 'higgs', 'letter', 'mnist', 'optdigits', 'poker']:
        for opt in optimizers:
            job_str = '_'.join(['paramnet_surrogates', dataset, opt])
            script = cluster_job_template.format(job=job_str, exp='paramnet_surrogates', run_id=random.randint(1, 1000000), opt=opt,
                                        max_b=0, min_b=0, additional='--dataset_paramnet_surrogates ' + dataset,
                                        num_it=n_iterations['paramnet_surrogates'], queue_name=queue_name)
            gen_script(script, job_str)
            if not submit2cluster:
                os.system("python run_experiment.py --exp_name paramnet_surrogates --opt_method {opt} "
                          "--dataset_paramnet_surrogates {dataset} --num_iterations 10 --n_workers 1 "
                          "--dest_dir ../opt_results".format(opt=opt, dataset=dataset))

def run_bnn():
    for dataset in ['bostonhousing', 'toyfunction', 'proteinstructure']:
        for opt in optimizers:
            job_str = '_'.join(['bnn', dataset, opt])
            script = cluster_job_template.format(job=job_str, exp='bnn', run_id=random.randint(1, 1000000), opt=opt,
                                        max_b=10000, min_b=300, additional='--dataset_bnn ' + dataset,
                                        num_it=n_iterations['bnn'], queue_name=queue_name)
            gen_script(script, job_str)


if __name__ == '__main__':
    if 'bnn' in experiments:
        run_bnn()
    if 'cartpole' in experiments:
        run_cartpole()
    if 'paramnet_surrogates' in experiments:
        run_paramnet_surrogates()
    if 'svm_surrogate' in experiments:
        run_svm_surrogate()
