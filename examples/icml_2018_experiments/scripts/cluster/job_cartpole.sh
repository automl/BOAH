#!/bin/bash
#SBATCH -p queue-name # partition (queue)
#SBATCH --mem 4000 # memory pool for all cores (4GB)
#SBATCH -t 1-10:00 # time (D-HH:MM)
#SBATCH -c 4 # number of cores
#SBATCH -o log/%x.%N.%j.out # STDOUT  (the folder log has to be created prior to running or this won't work)
#SBATCH -e log/%x.%N.%j.err # STDERR  (the folder log has to be created prior to running or this won't work)
#SBATCH -J cartpole # sets the job name. If not specified, the file name will be used as job name
#SBATCH --mail-type=END,FAIL # (recive mails about end and timeouts/crashes of your job)
#SBATCH --array 0-3
# Print some information about the job to STDOUT
echo "Workingdir: $PWD";
echo "NOTE: Always submit from dir with run_experiment.py";
echo "Started at $(date)";
echo "Running job $SLURM_JOB_NAME using $SLURM_JOB_CPUS_PER_NODE cpus per node with given JID $SLURM_JOB_ID on queue $SLURM_JOB_PARTITION"; 
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"; 

source ~/BOHBsCAVE/.ve_BOHBsCAVE/bin/activate;

# Job to perform
if [ $SLURM_ARRAY_TASK_ID -eq 0 ]
then
   python run_experiment.py --exp_name cartpole --run_id 43 --nic_name eth0 --no_worker --opt_method bohb --dest_dir opt_results/cartpole/bohb --max_budget 9 --min_budget 1 --n_workers 4
else
   python run_experiment.py --exp_name cartpole --run_id 43 --nic_name eth0 --worker --opt_method bohb --dest_dir opt_results/cartpole/bohb --max_budget 9 --min_budget 1 --n_workers 4
fi

# Print some Information about the end-time to STDOUT
echo "DONE";
echo "Finished at $(date)";
