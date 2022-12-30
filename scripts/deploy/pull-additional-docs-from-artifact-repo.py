import sys, json, os, boto3, botocore
from botocore.exceptions import ClientError
from datetime import datetime, timedelta
from dateutil.relativedelta import *

print("getting REG_ARTIFACT_REPO_BUCKET env var...")
repo_bucket_name = os.getenv('REG_ARTIFACT_REPO_BUCKET')

## TODO: generate providers.yaml file

#
# S3 setup and functions
#

s3_client = boto3.client('s3')

#
# main routine
#        

print("getting REG_TARGET_BRAMCH env var...")
target_branch = os.getenv('REG_TARGET_BRAMCH')

print("getting REG_MAX_VERSIONS env var...")
max_versions = os.getenv('REG_MAX_VERSIONS')

print("getting REG_MAX_AGE_MONTHS env var...")
max_age_months = os.getenv('REG_MAX_AGE_MONTHS')

print("getting PROVIDERS env var...")
providers = json.loads(os.getenv('PROVIDERS'))

#
# get list of updated providers in this build (names only)
#
updated_providers = []
print("getting updated providers...")
for provider in providers:
    updated_providers.append(provider['provider'])

#
# pull additional docs from artifact repo needed for deployment
#
for provider in updated_providers:
    local_objects = os.listdir("%s/%s/%s" % (os.getenv('REG_WEBSITE_DIR'), os.getenv('REG_PROVIDER_PATH'), provider))
    
    local_objects_with_path = []
    for obj in local_objects:
        local_objects_with_path.append("%s/%s/%s" % (os.getenv('REG_PROVIDER_PATH'), provider, obj))
    
    print("local objects:")
    print(local_objects_with_path)

    print("getting list of objects in the %s bucket..." % (repo_bucket_name))
    s3_objects = []
    for obj in s3_client.list_objects_v2(
        Bucket=repo_bucket_name,
        Prefix=os.getenv('REG_PROVIDER_PATH')
        # Delimiter='string',
        # StartAfter='string'
        )['Contents']:
        if obj['Key'] != "%s/" % (os.getenv('REG_PROVIDER_PATH')):
            s3_objects.append(obj['Key'])

    print("remote objects:")
    print(s3_objects)    

local_objects_set = set(local_objects_with_path)
s3_objects_set = set(s3_objects)

req_files = list(s3_objects_set.difference(local_objects_set))

if target_branch == 'main':
    # filter out files that have -dev in the name
    req_files = [x for x in req_files if '-dev' not in x]

print("additional files needed to pull: %s" %(str(req_files)))

for req_file in req_files:
    print("pulling %s from artifact repo..." % (req_file))
    s3_client.download_file(repo_bucket_name, req_file, "%s/%s" % (os.getenv('REG_WEBSITE_DIR'), os.getenv('REG_PROVIDER_PATH')))

#
# generate providers.yaml file
#

print("generating providers.yaml file...")
# providers_yaml = open("%s/%s/providers.yaml" % (os.getenv('REG_WEBSITE_DIR'), os.getenv('REG_PROVIDER_PATH')), "w")


