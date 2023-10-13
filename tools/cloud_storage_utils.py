import os
from google.cloud import storage


# Initialize a client
client = storage.Client()

# upload to google cloud storage
def upload_to_cloud(local_file_paths, bucket_name:str='luto_tif', destination_path:str=''):
    # Access the bucket
    bucket = client.bucket(bucket_name)

    # Upload local files to the bucket
    for local_file in local_file_paths:
        blob = bucket.blob(destination_path + os.path.basename(local_file))
        blob.upload_from_filename(local_file)

    print(f'Local files copied to bucket: {bucket_name}/{destination_path}')

# set public access to the files in the bucket
def set_public_access(bucket_name:str='luto_tif'):
    # Access the bucket
    bucket = client.bucket(bucket_name)

    # Set public access to the bucket
    bucket.make_public(recursive=True)
    print(f'Public access granted to bucket: {bucket_name}')