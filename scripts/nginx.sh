#!/bin/bash

if [ $# -ne 1 ]; then
    dir="`pwd`/storage/gdmrdigital/iiif-manifests-gdmr"
else
    dir=$1
fi
echo "Running nginx on port 80: http://localhost"
docker build -t nginx-s3:latest . && docker run --rm --name nginx-s3 -p 80:80 -v $dir:/usr/share/nginx/html:ro nginx-s3:latest
