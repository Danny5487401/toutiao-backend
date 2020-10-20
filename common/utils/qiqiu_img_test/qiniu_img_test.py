from qiniu import Auth, put_file, etag
import qiniu.config

#需要填写你的 Access Key 和 Secret Key
access_key = 'b4hkdEqyufbchlsAj0Xm17MptIo9pBLxkd83pB3p'
secret_key = 'umDHZLmgiG7PC6exJmdKw6V4ITf2yDXzqH8x0i0w'

#构建鉴权对象
q = Auth(access_key, secret_key)

#要上传的空间
bucket_name = 'toutiao-app'

#上传后保存的文件名
key = 'avator.png'

#生成上传 Token，可以指定过期时间等
token = q.upload_token(bucket_name, key, 3600)

#要上传文件的本地路径
localfile = './avator.png'

ret, info = put_file(token, key, localfile)
print(info)
assert ret['key'] == key
assert ret['hash'] == etag(localfile)

# 打印内容
# ResponseInfo__response:<Response [200]>, exception:None, status_code:200, text_body:{"hash":"FrcrsqTNTwwkswntGqf6iWlUQSJk","key":"my-python-logo.png"}, req_id:1OMAAADIToMhZz0W, x_log:X-Log
# 地址 http://qi2xepx1u.hd-bkt.clouddn.com/my-python-logo.png