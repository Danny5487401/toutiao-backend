from flask_restful.reqparse import RequestParser

from cache import user as cache_user  # 为导入的模块起别名
from flask_restful import Resource

from models import db
from models.user import User
from utils.decorators import login_required
from flask import g, current_app
from utils import parser
from utils.qiniu_storage import upload_image


class CurrentUserResource(Resource):
    """
    用户自己的数据
    """
    method_decorators = [login_required]

    def get(self):
        """
        获取当前用户自己的数据
        """
        user_data = cache_user.UserProfileCache(g.user_id).get()
        user_data['id'] = g.user_id
        del user_data['mobile']
        return user_data


class PhotoResource(Resource):
    """
    用户图片资料的视图处理
    """
    method_decorators = [login_required]

    def patch(self):
        """
        修改用户的资料（修改用户头像）
        :return:
        """
        # 获取请求参数
        # 校验请求参数
        rp = RequestParser()
        rp.add_argument('photo', type=parser.image_file, required=True, location='files')
        req = rp.parse_args()

        # 业务处理
        # 上传到七牛
        # req.photo 取出了请求中的文件对象，通过read方法读取文件的二进制数据
        file_name = upload_image(req.photo.read())

        # 保存图片名（图片路径）到数据库
        # 1. 保存完整的图片路径，包含了域名，浪费空间
        # 2. 图片访问的域名实际上是可以设置的，如果修改了，数据库中如果保存了域名，数据库数据也得修改，不方便
        User.query.filter(User.id == g.user_id).update({'profile_photo': file_name})
        db.session.commit()

        # 构建返回数据
        photo_url = current_app.config['QINIU_DOMAIN'] + file_name
        return {'photo_url': photo_url}
