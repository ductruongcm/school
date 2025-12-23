from minio.error import S3Error
from .extensions import minio_client, BUCKET_NAME

try:
    if not minio_client.bucket_exists(BUCKET_NAME):
        minio_client.make_bucket(BUCKET_NAME)
except S3Error as err:
    if err.code != "BucketAlreadyOwnedByYou":   
        raise