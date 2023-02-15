#!/bin/bash -l

NEWHOME=/path/to/gefs-wave

# GEFS-Wave Product Generation
${NEWHOME}/ush/ww3_graphics.sh $when 1>${NEWHOME}/logs/gefs_graphics.log 2>&1

