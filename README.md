EDA end-to-end workflow with 

       1. boto3 for S3 operations
       2. pytest framework with plugins for mocking and reporting
       3. Also, has two data files for catalog and products data samples
       4. Can dockerized and cron on AWS lambda

 Prerequisite: check.ini with AWS credentials, region and bucket created as below
 
[DEFAULT]
region=ca-central-1

bucket=teda 

[credentials]

ack=[XXXXXXX]

sck=[XXXXXXX]