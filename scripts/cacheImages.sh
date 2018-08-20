#!/bin/bash

imgdir=storage/gdmrdigital/iiif-images
find $imgdir  -name "*.jp2" |while read line
do
    imgpath=`echo $line | sed "s|$imgdir/||g"|sed 's|/|%2f|g'`
    curl "http://iiif.gdmrdigital.com/image/iiif/2/$imgpath/info.json" > /dev/null
done
