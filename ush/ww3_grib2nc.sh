#!/bin/ksh -l

# these must be loaded
module load intel/19.0.5.281 gnu/9.2.0 wgrib2/2.0.8 netcdf/4.7.2

function myconvert {
wgrib2 ${1}.grib2 -netcdf nc/${1}.nc3 1>/dev/null 2>&1
nccopy -7 -d 4 nc/${1}.nc3 nc/${1}.nc
rm nc/${1}.nc3
}

START_DATE=$1

MAXJOBS=10
#MAXJOBS=4   ## for manual runs
BASEDIR='/scratch2/NCEPDEV/ocean/Deanna.Spindler/noscrub/GEFS_grib/archive'

njobs=0

if [[ ! -n $SLURM_JOB_NAME ]]; then
  echo "---------------------------------------------------"
  echo "THIS CANNOT RUN ON THE FRONT END.  TERMINATING NOW."
  echo "---------------------------------------------------"
  printenv
  exit
fi

cd $BASEDIR/$START_DATE
mkdir -p nc

for file in *.grib2; do
	fname=$(basename $file .grib2)
	if [[ -a nc/${fname}.nc ]]; then
	  continue
	fi
	myconvert $fname &	  
	njobs=$(( $njobs + 1 ))
	if (( $njobs >= $MAXJOBS )); then
	  wait
	  njobs=0
	fi
done
wait

