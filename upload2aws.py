#!/usr/bin/python

# this source is part of my Hackster.io project:  https://www.hackster.io/mariocannistra/radio-astronomy-with-rtl-sdr-raspberrypi-and-amazon-aws-iot-45b617

# use this program to test the AWS S3 connection using the test-chart.png file

import boto
from boto.s3.key import Key
import boto.s3.connection
import radioConfig
import sys
from datetime import datetime
import ntpath

def push_picture_to_s3(id):
	# id should have the folder name as YYYYMMDD/filename.ext

    BUCKET_NAME = 'jupiter-spectrograms'
    AWS_ACCESS_KEY_ID = radioConfig.AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = radioConfig.AWS_SECRET_ACCESS_KEY

    # connect to the bucket
    conn = boto.s3.connect_to_region('eu-central-1',
       aws_access_key_id=AWS_ACCESS_KEY_ID,
       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
       is_secure=True,               # uncommmnt if you are not using ssl
       calling_format = boto.s3.connection.OrdinaryCallingFormat(),
       )

    #print(conn)

    keyname = '%s/%s' % ( radioConfig.scanTarget, id )
    #print(keyname)

    #fn = '%s.png' % id
    fn = id
    #print(fn)

    bucket = conn.get_bucket(BUCKET_NAME)
    #print(bucket)

    #print "uploading file"
    key = bucket.new_key(keyname)
    key.set_contents_from_filename(fn)
    print('  file uploaded to aws s3')

    print("  setting acl to public read")
    key.set_acl('public-read')

    # we need to make it public so it can be accessed publicly
    # using a URL like http://s3.amazonaws.com/bucket_name/key
    print("  making key public")
    key.make_public()

push_picture_to_s3(sys.argv[1])
