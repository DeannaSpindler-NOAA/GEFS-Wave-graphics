#!/bin/ksh
# 
# run as: get_hpss_prod.sh 20220218 20220219
#
# get any missing GEFS-Wave files from HPSS
# and put them on /scratch2/NCEPDEV/stmp1/Deanna.Spindler/hpss

NEWHOME='/gpfs/dell2/emc/verification/noscrub/Deanna.Spindler'
WORKDIR='/scratch2/NCEPDEV/stmp1/Deanna.Spindler/hpss'
hpsstar='/scratch2/NCEPDEV/ocean/Deanna.Spindler/save/bin/hpsstar'

module purge
module load intel/19.0.5.281 impi/2022.1.2 gnu/9.2.0 netcdf/4.7.2
module load hpss/hpss

modID='gefswave'

#theDate=20220218??
#endDate=2022??????  real-time run
theDate=$1
endDate=${2:-$theDate}

maxtasks=5

cycles='00 06 12 18'
#cycles='06'

fcsts='f000 f024 f048 f072 f096 f120 f144 f168 f192 f216 f240 f264 f288 f312 f336 f360 f384'
#fcsts='f000'

echo "starting at `date`"
cd ${WORKDIR}
while (( $theDate <= $endDate )); do
  echo "running get_hpss_prod for ${theDate}"
  yy=`date --date=$theDate "+%Y"`
  yymm=`date --date=$theDate "+%Y%m"`  
  # begin hpss extraction
  for cyc in $cycles; do
    echo 'processing' $cyc
	filedir=${theDate}/${cyc}
	mkdir -p ${theDate}
	hpss_dir=/NCEPPROD/2year/hpssprod/runhistory/rh${yy}/${yymm}/${theDate}
	hpss_file=com_gefs_v12.2_gefs.${theDate}_${cyc}.wave_gridded.tar
	for fcst in $fcsts; do
	  file1=gefs.wave.t${cyc}z.c00.global.0p25.${fcst}.grib2
	  file2=gefs.wave.t${cyc}z.mean.global.0p25.${fcst}.grib2
	  file3=gefs.wave.t${cyc}z.prob.global.0p25.${fcst}.grib2
	  file4=gefs.wave.t${cyc}z.spread.global.0p25.${fcst}.grib2
	  $hpsstar getnostage $hpss_dir/$hpss_file ./wave/gridded/$file1 &
	  $hpsstar getnostage $hpss_dir/$hpss_file ./wave/gridded/$file2 &
	  $hpsstar getnostage $hpss_dir/$hpss_file ./wave/gridded/$file3 &
	  $hpsstar getnostage $hpss_dir/$hpss_file ./wave/gridded/$file4 &
	  wait
	  mv wave/gridded/$file1 $theDate/.
	  mv wave/gridded/$file2 $theDate/.
	  mv wave/gridded/$file3 $theDate/.
	  mv wave/gridded/$file4 $theDate/.
	done
  done
  rm -rf $workdir/gfs.${theDate}
  theDate=$(date --date="$theDate + 1 day" '+%Y%m%d')
done

echo "get_hpss_prod finished on `date`"
exit

