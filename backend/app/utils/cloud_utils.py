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

def download_folder(prefix: str = ''):
    objects = minio_client.list_objects(bucket_name = BUCKET_NAME,
                                        prefix = prefix,
                                        recursive = True)
    objs = list(objects)
    file = []
    path = set()
    for i in objs:
        folder = i.object_name.split('/')[1]
        filename = i.object_name.split('/')[2]
        path.add(folder)
        file.append({'filename': filename,
                'file_size': i.size,
                'last_modified': i.last_modified.isoformat()})
    return file, path

def cloud_download(class_room, file_name):
    url = minio_client.presigned_get_object(bucket_name = BUCKET_NAME,
                                            object_name = f'{class_room}/{file_name}',
                                            expires = timedelta(minutes = 15),
                                            response_headers = {'response-content-disposition': f'attachment; filename="{file_name}"'}) 
                                            #Để download và gọn ở frontend chỉ cần click vào url là lụm phải thêm câu thần chú trên
    return url

def cloud_delete(class_room, file_name):
    url = minio_client.remove_object(bucket_name = BUCKET_NAME,
                                     object_name = f'{class_room}/{file_name}')
    return url