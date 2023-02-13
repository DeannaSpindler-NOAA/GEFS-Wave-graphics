#!/bin/ksh

if [[ -z $1 ]]; then
  echo 'No date set.  Exiting.'
  exit
fi

ARCDIR=/scratch2/NCEPDEV/stmp1/Deanna.Spindler/images/gfs-waves/GEFS/$1
REMOTE_ID=waves@emcrzdm.ncep.noaa.gov
REMOTE_DIR=/home/www/polar/waves/validation/gefsv12/images

rsync -a --rsh /usr/bin/ssh --rsync-path /usr/bin/rsync --timeout=3600 $ARCDIR ${REMOTE_ID}:$REMOTE_DIR

# do it again in case first time failed
rsync -a --rsh /usr/bin/ssh --rsync-path /usr/bin/rsync --timeout=3600 $ARCDIR ${REMOTE_ID}:$REMOTE_DIR

#rm -rf $ARCDIR

