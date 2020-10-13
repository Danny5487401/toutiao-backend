from cache import user as cache_user  # 为导入的模块起别名
from flask_restful import Resource
from utils.decorators import login_required
from flask import g, current_app


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
