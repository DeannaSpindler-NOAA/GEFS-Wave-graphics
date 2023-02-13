#!/usr/bin/bash -l
#
# Convert all daily and 3hrly netcdf and save to noscrub
# Uses GNU Parallel in counting semaphore mode
#

# set up module environment
module load intel/19.0.5.281 gnu/9.2.0 netcdf/4.7.2

TODAY=`date "+%Y%m%d"`
RUNDATE=${1:-$TODAY}

echo "Rundate: $RUNDATE" 

NEWHOME=/scratch2/NCEPDEV/ocean/Deanna.Spindler

ARCHIVE=$NEWHOME/noscrub/GEFS_grib/archive
ARCDIR=$ARCHIVE/$RUNDATE
#DATAURL=ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/gens/prod
DATAURL=ftp://140.90.101.48/pub/data/nccf/com/gens/prod/gefs.${RUNDATE}
PBURL=ftp://140.90.101.48/pub/data/nccf/com/gfs/prod/gdas.${RUNDATE}
## data is in FTPPRD for 4 days including "today"

#ftp://ftpprd.ncep.noaa.gov/pub/data/nccf/com/gens/prod/gefs.20200924/12/wave/gridded/

#MAXJOBS=10

mkdir -p $ARCDIR/nc

cycles='00 06 12 18'

fcsts='f000 f024 f048 f072 f096 f120 f144 f168 f192 f216 f240 f264 f288 f312 f336 f360 f384'

params='c00 mean prob spread'

cd $ARCDIR

# process daily first
for cycle in $cycles; do
  for fcst in $fcsts; do
    for param in $params; do
	  file="gefs.wave.t${cycle}z.${param}.global.0p25.${fcst}.grib2"
	  if [[ ! -a $ARCDIR/$file ]]; then
	    wget $DATAURL/${cycle}/wave/gridded/${file}
		#wget $PBURL/${cycle}/atmos/gdas.t${cycle}z.prepbufr.nr
	  fi
    done
  done  
done

# remove old archives 
#echo 'Cleaning up archives'
#cd $ARCHIVE
#olddir=$(date --date="-60 days" "+%Y%m%d")
#for dir in 20*; do
#  if (( $dir < $olddir )); then
#    rm -rf $ARCHIVE/${dir}
#  fi
#done

exit
