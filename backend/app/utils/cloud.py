from app.extensions import minio_client
from datetime import timedelta

BUCKET_NAME = 'bvd'

if not minio_client.bucket_exists(BUCKET_NAME):
    minio_client.make_bucket(BUCKET_NAME)

def cloud_upload(class_room, folder, file_name):
    url = minio_client.presigned_put_object(bucket_name = BUCKET_NAME,
                                      object_name = f'{class_room}/{folder}/{file_name}',
                                      expires = timedelta(minutes = 15))
    return url

def cloud_download(class_room, folder, file_name):
    url = minio_client.presigned_get_object(bucket_name = BUCKET_NAME,
                                            object_name = f'{class_room}/{folder}/{file_name}',
                                            expires = timedelta(minutes = 15),
                                            response_headers = {'response-content-disposition': f'attachment; filename="{file_name}"'}) 
                                            #Để download và gọn ở frontend chỉ cần click vào url là lụm phải thêm câu thần chú trên
    return url

def cloud_delete(class_room, folder, file_name):
    url = minio_client.remove_object(bucket_name = BUCKET_NAME,
                                     object_name = f'{class_room}/{folder}/{file_name}')
    return url