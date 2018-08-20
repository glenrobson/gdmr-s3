#!/bin/bash

echo "Running nginx on port 80: http://localhost"
docker build --rm -t nginx-s3:latest . && docker run --rm --name nginx-s3 -p 80:80 -v $1:/usr/share/nginx/html:ro nginx-s3:latest
