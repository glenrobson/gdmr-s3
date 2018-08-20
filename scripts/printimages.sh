#!/bin/bash

imgdir=storage/gdmrdigital/iiif-images
find $imgdir/lc/block_books/BB-AoM_595_00 -name "*.jp2" |while read line
do
    imgpath=`echo $line | sed "s|$imgdir/||g"|sed 's|/|%2f|g'`
    echo "\"http://iiif.gdmrdigital.com/image/iiif/2/$imgpath/full/,512/0/default.jpg\","
done
