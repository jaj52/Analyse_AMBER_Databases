###############################################################################
#Author: Jerelle A Joseph (jaj52@cam.ac.uk)
#Assess global kinetics for DPS database
#
#Here global kinetics is computed as the distribution of the 
#number of steps (transition states) on the fastest path
#to the global minimum 
#
#This approach was outlined in: Miller, M. A.; Wales, D. J. J. Chem. Phys. 1999, 111, 6610−6616
#
# Important: 
# 1. Required files: min.data, ts.data, points.min, points.ts, 
#                    (AMBER: coords.inpcrd, coords.prmtop, min.in),
#                    (LRBs: rbodyconfig, coordsinirigid). 
#
# 2. In additional to routine keywords, must set in pathdata: 
#                    DIJKSTRA 0, CYCLES 0, DEBUG, DIRECTION BA (must be set to BA)
#
#3. Ensure that <pathsample> variabale is the path to your PATHSAMPLE executable 
###################################################################################


#!/bin/bash


pathsample="/home/jaj52/bin/PATHSAMPLE_APR_17"

############ Check for required database files 
if [ ! -f min.data -o ! -f ts.data -o ! -f points.min -o ! -f points.ts ] ; then
    echo All or one of min.data, ts.data, points.min, points.ts not found
    echo You need all of the main database files in the current working directory  
    exit 1
fi

########### Prepare min.A (global minimum) and min.B (all other minima)

lowest_e=$(sort -k1,1n min.data | head -1 | awk '{print $1}')
id_temp=$( grep -n -- "${lowest_e}" min.data | awk '{print $1}')
id=${id_temp%%:*}

if [ -f min.A  ] ; then
    mv min.A min.A.orig
fi
echo 1 > min.A
echo $id >> min.A


min_total=$(wc -l min.data | awk '{print $1}') 
B_total="$(( ${min_total} - 1 ))"

if [ -f min.B  ] ; then
    mv min.B min.B.orig
fi
echo $B_total > min.B


count=1
while [ "${count}" -le "${min_total}" ] ; do
    if [ "${count}" -eq "${id}" ] ; then
        :
    else 
        echo $count >> min.B
    fi 
    count="$(( ${count} + 1 ))"
done   

####### Run pathsample and deal with output 
$pathsample >& global_kinetics.out 
data_="num_of_steps_to_${id}.xvg"
grep 'Dijkstra> Best path for minimum' global_kinetics.out | awk '{print $14}' > $data_

######## Uncomment the line below to use g_analyze to compute distribution of steps to global minimum
######## the bw parameter can be adjusted to suit the dataset for presentation and interpretation purposes 
# g_analyze -f $data_ -dist "${data_}_dist.xvg" -notime -bw 1 -xvg none
