#!/bin/bash

outputdir=$2
cat $1 |while read line; 
do
    if [ ! -f $outputdir/$line ]; then 
        aws s3 cp s3://mousebrainatlas-rawdata/CSHL_data/MD594/$line $outputdir; 
    else
        echo "Already downloaded $outputdir/$line"
    fi 
done
