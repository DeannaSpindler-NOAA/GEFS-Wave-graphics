#!/bin/ksh -l

#-------------------------------------------------------
# GEFS-WAVE (GEFSv12) Visualizations
# Version 0.1      
# Todd Spindler    
# 26 September 2020
#-------------------------------------------------------

# set up module environment
module use /scratch2/NCEPDEV/ocean/Deanna.Spindler/save/modulefiles
module load intel/19.0.5.281 gnu/9.2.0 wgrib2/2.0.8 netcdf/4.7.2
module load anaconda-work/1.0.0

START_DATE=${1:-$(date --date='yesterday' +%Y%m%d)}
STOP_DATE=${2:-$START_DATE}

TASK_QUEUE='batch'
WALL='3:00:00'
PROJ='ovp'
STMP="/scratch2/NCEPDEV/stmp1/Deanna.Spindler"
LOGPATH="$STMP/logs/gefs-wave"
JOB='gefsg'

mkdir -p $LOGPATH
#rm -f $LOGPATH/*.log

# clean out all images from all V&V tasks yesterday
#rm -rf $STMP/images/*

SRC_DIR='/scratch2/NCEPDEV/ocean/Deanna.Spindler/save/VPPPG/EMC_waves-verification/GEFSv12'
JOB1_SCRIPT="${SRC_DIR}/ush/gefs_archive.sh"
JOB2_SCRIPT="${SRC_DIR}/ush/ww3_grib2nc.sh"
JOB3_SCRIPT="python ${SRC_DIR}/scripts/ww3_graphics.py"
JOB4_SCRIPT="${SRC_DIR}/ush/transfer_ww3_graphics.sh"

## CAN ONLY RUN ONE OF THESE AT A TIME!
GET_DATA=''
MAKE_NC=''
PLOT_IT=''   ## make sure ww3_graphics.sh has the rm workdir commented out
MOVE_IT='yes'

while(( $START_DATE <= $STOP_DATE )); do
  day=$(date --date=${START_DATE} +%d)
  if [[ $GET_DATA = 'yes' ]] ; then
    JOB="G1$day"
	job1=$(sbatch --parsable -J ${JOB} -o $LOGPATH/job1_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=1  --partition=service --wrap "$JOB1_SCRIPT $START_DATE")
  fi
  if [[ $MAKE_NC = 'yes' ]] ; then  
    JOB="G2$day"
    job2=$(sbatch --parsable -J ${JOB} -o $LOGPATH/job2_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=10 --nodes=1           --wrap "$JOB2_SCRIPT $START_DATE")
  fi
  if [[ $PLOT_IT = 'yes' ]] ; then
    JOB="G3$day"
	job3=$(sbatch --parsable -J ${JOB} -o $LOGPATH/job3_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=21 --nodes=1           --wrap "$JOB3_SCRIPT $START_DATE")
  fi
  if [[ $MOVE_IT = 'yes' ]] ; then
    JOB="G4$day"
	job4=$(sbatch --parsable -J ${JOB} -o $LOGPATH/job4_${START_DATE}.log -q $TASK_QUEUE --account=$PROJ --time $WALL --ntasks=1  --partition=service --wrap "$JOB4_SCRIPT $START_DATE")
  fi
  START_DATE=$(date --date="$START_DATE + 1 day" '+%Y%m%d')
done

