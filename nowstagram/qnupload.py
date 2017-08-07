# _*_ coding:utf-8 _*_

from qiniu import Auth, put_file, etag, urlsafe_base64_encode
import qiniu.config

# 我的Access Key和Secret Key
access_key = 'MfT21ftBASo_9N1dJ7d-nk--HnjKY3tjVemTH1I2'
secret_key = '6aJgMo5TbP6D5XTe9IXLMnQR3sDXJzkpi-JcfJrO'

# 构建鉴权对象
q = Auth(access_key, secret_key)

# 上传空间名称
bucket_name = 'myinstagram'

# 上传到七牛的文件名
key = 'my-first-upload.jpg'

# 生成上传Token, 3306表示指定的过期时间
token = q.upload_token(bucket_name, key, 3600)

# 要上传的文件的本地路径
localfile = 'E:/LoveWallpaper/100CANON/IMG_2101.JPG'

ret, info = put_file(token, key, localfile)
print(info)
assert ret['key'] == key
assert ret['hash'] == etag(localfile)
