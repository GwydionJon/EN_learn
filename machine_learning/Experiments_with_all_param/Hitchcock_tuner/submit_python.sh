#!/bin/bash
#***you need to change the jobname in the below line to something meaningful, ie run010
#SBATCH --job-name="ml_overlap_from_spectrum_tuner"
#SBATCH --nodes=1
#SBATCH --ntasks=1 
#SBATCH --cpus-per-task=24
#SBATCH --mem=32G
#SBATCH --output="j%j.%N.out"
####SBATCH --partition=all

myinp="ml_overlap_from_spectrum_tuner.py"

myop="all_param_4_values_with_overlap.csv"
# we will make use of altering parameters via the command line
run="ml_overlap_from_spectrum_tuner"
outname='tuner_out2'
source ~/.bashrc
myexec="/home/tcstud25/anaconda3/bin/python"
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
cp -r $START_DIR/"$myinp" $RUN_PATH
cp -r $START_DIR/"$myop" $RUN_PATH
cd $RUN_PATH
echo "Run parameters are : $myexec $run $myinp"
srun $myexec $run $myinp 

# If you do use MPI, use 'mpirun' to start the job.
# Check the various mpirun options for performance 
# optimizations. 
# After the job has completed copy output 
# to /tmpa on hitchcock
mkdir -p /tmpa/$USER
OUTPUT_PATH="/tmpa/$USER/$outname.output"
mkdir $OUTPUT_PATH
LINK_OUTDIR="$START_DIR/$outname.output"
cp -r $RUN_PATH/* $OUTPUT_PATH || exit 1

# remove data on /scratch
rm -rf $RUN_PATH 

# make a link in the start dir for convenience
ln -s $OUTPUT_PATH $LINK_OUTDIR

# and write to the jobinfo file that the job has finished
DATE=$(/bin/date)
echo  "STOP DATE: $DATE" >> "$JOBINFO"

exit 0


