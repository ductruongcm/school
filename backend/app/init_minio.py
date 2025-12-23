from app.extensions import minio_client
from minio.error import S3Error

BUCKET_NAME = 'bvd'

try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except S3Error as err:
    if err.code != "BucketAlreadyOwnedByYou":   
        raise