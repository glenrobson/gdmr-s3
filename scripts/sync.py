#!/usr/local/bin/python3

import os
import sys
import boto3
import configparser
import configargparse
import datetime
import json
import magic
from pytz import timezone
from dateutil.tz import tzlocal
from tzlocal import get_localzone

localtimezone = get_localzone()
mime = magic.Magic(mime=True)

def isIgnore(name):
    if name == '.DS_Store':
        return True
    else:
        return False

def listfiles(dir, prefix):
    files = {}
    for file in os.listdir(dir):
        if os.path.isdir(os.path.join(dir,file)):
            files = {**listfiles(os.path.join(dir,file), prefix), **files}
        else:
            if not isIgnore(file):
                filepath = os.path.join(dir, file)
                filedata = {}
                filedata['path'] = filepath
                filedata['id'] = filedata["path"].replace(prefix + '/', '')
                filedata['lastmod'] = localtimezone.localize(datetime.datetime.fromtimestamp(os.stat(filepath).st_mtime))
                filedata['mime-type'] = mime.from_file(filepath)
                if file.endswith('.json'):
                    filedata['mime-type'] = 'application/json'
                elif file.endswith('.css'):
                    filedata['mime-type'] = 'text/css'
                elif file.endswith('.js'):
                    filedata['mime-type'] = 'application/javascript'
                elif file.endswith('.woff2'):
                    filedata['mime-type'] = 'font/woff2'

                files[filedata['id']] = filedata
    return files
def putfile(s3, bucket, localfile, remote):
    s3.put_object(Bucket=bucket,ACL='public-read',Body=open(localfile['path'], 'rb'),Key=remote, ContentType=localfile['mime-type'], ContentDisposition='inline')

def deletefile(s3, bucket, key):
    s3.delete_object(Bucket=bucket,Key=key)

if __name__ == "__main__":
    parser = configargparse.ArgParser(description='Create a manifest from a directory of images.', default_config_files=['config/sync.config'])
    parser.add('--root-dir',nargs=1,  help='Location to sync')
    parser.add('--check-mime',nargs=1, help='Check mime matches local')
    # test program with out making changes
    simulate=False
    options = parser.parse_args()
    print(options)
    root = options.root_dir[0]
    if options.check_mime:
        checkmime = True
    else:
        checkmime = False
    # top level is aws account
    for account in os.listdir(root):
        print ('Connecting to s3 account: "%s"' % account)
        account = os.path.join(root,account)

        config = configparser.ConfigParser()
        config.read(os.path.join(account,'.aws-credentials.ini'))
        section='credentials'
        s3client = boto3.client('s3',aws_access_key_id=config.get(section,'aws_access_key_id'), aws_secret_access_key=config.get(section,'aws_secret_access_key'), region_name=config.get(section,'region_name'))
        localcontents = {}
        for bucket in os.listdir(account):
            if os.path.isdir(os.path.join(account, bucket)):
                print ('Syncing with bucket: "%s"' % bucket)
                localcontents = listfiles(os.path.join(account, bucket), os.path.join(account, bucket))
                #print(json.dumps(localcontents, indent=4))
                bucketcontents = s3client.list_objects_v2(Bucket=bucket)
                bucketdict = {}
                for s3fileinfo in bucketcontents["Contents"]:
                    if s3fileinfo["Key"][-1] != '/':
                        bucketdict[s3fileinfo["Key"]] = s3fileinfo

                for key in localcontents:
                    localfile = localcontents[key]
                    if key in bucketdict:
                        # file exists on s3 check lastmod
                        if localfile["lastmod"] > bucketdict[key]["LastModified"]:
                            print ("UPDATE %s (local:%s, remote:%s)" % (key,localfile["lastmod"],bucketdict[key]["LastModified"]))
                            if not simulate:
                                putfile(s3client,bucket,localfile,key)
                        else:
                            if checkmime:
                                filemd = s3client.head_object(Bucket=bucket, Key=key)
                                if filemd["ContentType"] != localfile['mime-type']:
                                    print ("UPDATE %s (local mime:%s, remote mime:%s)" % (key,localfile['mime-type'],filemd["ContentType"]))
                                    putfile(s3client,bucket,localfile,key)
                            #    else:
                            #        print ('Checking %s mime type - MATCHES' % key)
                        del bucketdict[key]
                    else:
                        print ("ADD %s" % key)
                        if not simulate:
                            putfile(s3client,bucket,localfile,key)
                for key in bucketdict:
                    print ("DELETE %s" % key)
                    if not simulate:
                        deletefile(s3client,bucket,key)
    # second level is bucket
    # thrid level is content
