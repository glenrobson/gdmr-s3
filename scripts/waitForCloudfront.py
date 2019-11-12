#!/usr/local/bin/python3

import os
import sys
import boto3
import configparser
import configargparse
import time

def waitForInvalidation(cloudfront,distribution, invalidationId):
    status='waiting'
    pause = 10
    while status != 'Completed':
        response = cloudfront.get_invalidation(DistributionId=distribution, Id=invalidationId)

        status = response['Invalidation']['Status']
        print ("Status: {}, checking in {} seconds.".format(status,pause))
        time.sleep(10) # seconds

if __name__ == "__main__":
    invalidationid = sys.argv[1]
    config = configparser.ConfigParser()
    config.read(os.path.join('storage/gdmrdigital','.aws-credentials.ini'))

    section='credentials'
    cloudfront = boto3.client('cloudfront',aws_access_key_id=config.get(section,'aws_access_key_id'), aws_secret_access_key=config.get(section,'aws_secret_access_key'))

    waitForInvalidation(cloudfront, config.get('cloud_front', 'distribution_id'), invalidationid)

