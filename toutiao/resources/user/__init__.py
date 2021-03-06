from flask import Blueprint
from flask_restful import Api

from utils.output import output_json
from . import passport
from . import profile, channel, following

user_bp = Blueprint('user', __name__)
user_api = Api(user_bp)
user_api.representation('application/json')(output_json)

user_api.add_resource(passport.SMSVerificationCodeResource, '/v1_0/sms/codes/<mobile>',
                      endpoint='SMSVerificationCode')

user_api.add_resource(passport.AuthorizationResource, '/v1_0/authorizations',
                      endpoint='Authorization')

user_api.add_resource(channel.ChannelListResource, '/v1_0/user/channels',
                      endpoint='Channels')

user_api.add_resource(profile.CurrentUserResource, '/v1_0/user',
                      endpoint='CurrentUser')

user_api.add_resource(channel.ChannelResource, '/v1_0/user/channels/<int(min=1):target>',
                      endpoint='Channel')

# 关注用户
user_api.add_resource(following.FollowingListResource, '/v1_0/user/followings',
                      endpoint='Followings')

# 取消关注用户
user_api.add_resource(following.FollowingResource, '/v1_0/user/followings/<int(min=1):target>',
                      endpoint='Following')

