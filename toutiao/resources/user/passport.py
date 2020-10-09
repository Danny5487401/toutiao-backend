from flask_restful import Resource
from utils.limiter import limiter as lmt
from flask_limiter.util import get_remote_address
import random
from flask import request,current_app
from . import constants
from celery_tasks.sms.tasks import send_sms_code
from datetime import datetime, timedelta


class SMSVerificationCodeResource(Resource):
    """
    短信验证码
    """
    error_message = 'Too many requests.'

    decorators = [
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_MOBILE,
                  key_func=lambda: request.view_args['mobile'],
                  error_message=error_message),
        lmt.limit(constants.LIMIT_SMS_VERIFICATION_CODE_BY_IP,
                  key_func=get_remote_address,
                  error_message=error_message)
    ]

    def get(self, mobile):
        code = '{:0>6d}'.format(random.randint(0, 999999))
        # current_app.redis_master.setex('app:code:{}'.format(mobile), constants.SMS_VERIFICATION_CODE_EXPIRES, code)
        send_sms_code.delay(mobile, code)
        return {'mobile': mobile}

class AuthorizationResource(Resource):
    def _generate_tokens(self, user_id, refresh=True):
        """
        生成token 和refresh_token
        :param user_id: 用户id
        :return: token, refresh_token
        """
        # 颁发JWT
        secret = current_app.config['JWT_SECRET']
        # 生成调用token， refresh_token
        expiry = datetime.utcnow() + timedelta(hours=current_app.config['JWT_EXPIRY_HOURS'])

        token = generate_jwt({'user_id': user_id}, expiry, secret)

        if refresh:
            exipry = datetime.utcnow() + timedelta(days=current_app.config['JWT_REFRESH_DAYS'])
            refresh_token = generate_jwt({'user_id': user_id, 'is_refresh': True}, exipry, secret)
        else:
            refresh_token = None

        return token, refresh_token