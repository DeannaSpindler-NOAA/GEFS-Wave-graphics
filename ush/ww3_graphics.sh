#!/bin/ksh -l

#-------------------------------------------------------
# GEFS-WAVE (GEFSv12) Visualizations
# Version 0.1      
# Todd Spindler    
# 26 September 2020
#-------------------------------------------------------

# set up module environment
module use /scratch2/NCEPDEV/ocean/Deanna.Spindler/save/modulefiles
module load intel/19.0.5.281 wgrib2/2.0.8 gnu/9.2.0 netcdf/4.7.2
module load anaconda-work/1.0.0 

START_DATE=${1:-$(date --date='yesterday' +%Y%m%d)}
STOP_DATE=${2:-$START_DATE}

TASK_QUEUE='batch'
WALL='2:00:00'
WALL2='3:00:00'
PROJ='ovp'
STMP="/scratch2/NCEPDEV/stmp1/Deanna.Spindler"
LOGPATH="$STMP/logs/gefs-wave"
JOB='gefs_graphics'

mkdir -p $LOGPATH
#rm -f $LOGPATH/*.log

# clean out all images from all V&V tasks yesterday
#rm -rf $STMP/images/gfs-waves/GEFS/*

SRC_DIR='/scratch2/NCEPDEV/ocean/Deanna.Spindler/save/VPPPG/EMC_waves-verification/GEFSv12'
JOB1_SCRIPT="${SRC_DIR}/ush/gefs_archive.sh"
JOB2_SCRIPT="${SRC_DIR}/ush/ww3_grib2nc.sh"
JOB3_SCRIPT="ipython ${SRC_DIR}/scripts/ww3_graphics.py"
JOB4_SCRIPT="${SRC_DIR}/ush/transfer_ww3_graphics.sh"

while(( $START_DATE <= $STOP_DATE )); do
	job1=$(sbatch --parsable                            -J ${JOB}1 -o $LOGPATH/job1_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=1  --partition=service --wrap "$JOB1_SCRIPT $START_DATE")
	job2=$(sbatch --parsable --dependency=afterok:$job1 -J ${JOB}2 -o $LOGPATH/job2_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=10 --nodes=1           --wrap "$JOB2_SCRIPT $START_DATE")
	job3=$(sbatch --parsable --dependency=afterok:$job2 -J ${JOB}3 -o $LOGPATH/job3_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL2 --ntasks=21 --nodes=1           --wrap "$JOB3_SCRIPT $START_DATE")
	job4=$(sbatch --parsable --dependency=afterok:$job3 -J ${JOB}4 -o $LOGPATH/job4_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=1  --partition=service --wrap "$JOB4_SCRIPT $START_DATE")
  START_DATE=$(date --date="$START_DATE + 1 day" '+%Y%m%d')
done

