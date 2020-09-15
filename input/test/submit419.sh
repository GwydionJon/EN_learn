#!/bin/bash
#***you need to change the jobname in the below line to something meaningful, ie run010
#SBATCH --job-name="run419"
#SBATCH --nodes=1
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --output="j%j.%N.out"
####SBATCH --partition=all

myinp="pyr4"
myop="pyrmod4"
# we will make use of altering parameters via the command line
run="-mnd -D run419 -p k6a1 0.0 -p k6a2 0.5 -p k11 -0.5 -p k12 0.0 -p k9a1 0.0 -p k9a2 0.5"
source ~/.bashrc
myexec="mctdh85P"

# you may want to have some info file created when the job starts
DATE=$(/bin/date)
START_DIR=$(/bin/pwd)
JOBINFO="$START_DIR/$SLURM_JOB_ID.jobinfo"
echo  "" > "$JOBINFO"
echo  "Job started on $HOSTNAME" >> "$JOBINFO"
echo  "START DATE: $DATE" >> "$JOBINFO"

# The job should be executed on the nodes scratch:
# so, create a workdir for the job to run in
RUN_PATH="/scratch/$USER/$SLURM_JOB_ID.dir"
mkdir -p $RUN_PATH 

# Copy stuff to the workdir. Please make
# sure you only copy things that are needed
# by your program to keep the network trafic 
# low. 
cp -r $START_DIR/"$myinp".inp $RUN_PATH
cp -r $START_DIR/"$myop".op $RUN_PATH
cd $RUN_PATH
echo "Run parameters are : $run"
srun "$myexec" "$run" "$myinp".inp 

# If you do use MPI, use 'mpirun' to start the job.
# Check the various mpirun options for performance 
# optimizations. 
# After the job has completed copy output 
# to /tmpa on hitchcock
mkdir -p /tmpa/$USER
OUTPUT_PATH="/tmpa/$USER/$SLURM_JOB_ID.output"
LINK_OUTDIR="$START_DIR/$SLURM_JOB_ID.output"
cp -r $RUN_PATH $OUTPUT_PATH || exit 1

# remove data on /scratch
rm -rf $RUN_PATH 

# make a link in the start dir for convenience
ln -s $OUTPUT_PATH $LINK_OUTDIR

# and write to the jobinfo file that the job has finished
DATE=$(/bin/date)
echo  "STOP DATE: $DATE" >> "$JOBINFO"

exit 0


