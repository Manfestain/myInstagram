# _*_ coding:utf-8 _*_

from qiniu import Auth, put_data, etag, urlsafe_base64_encode, put_file
import qiniu.config
from nowstagram import app

# 配置
access_key = app.config['QINIU_ACCESS_KEY']
secret_key = app.config['QINIU_SECRET_KEY']
q = Auth(access_key, secret_key)
bucket_name = app.config['QINIU_BUCKET_NAME']
domain_prefix = app.config['QINIU_DOMAIN']

# 上传文件并返回url，如果上传失败则返回None
def qiniu_upload_file(source_file, save_file_name):
    token = q.upload_token(bucket_name, save_file_name)
    ret, info = put_data(token, save_file_name, source_file.stream)
    #ret, info = put_file(token, save_file_name, source_file)

    if info.status_code == 200:
        return domain_prefix + save_file_name
    return None
