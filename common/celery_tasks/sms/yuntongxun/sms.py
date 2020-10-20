import json
import random


# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
from celery_tasks.main import app

_accountSid = '8aaf070872d9c1450172ea96033c0759'
# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = 'e8706a622fac479eaf5f14f1fbaf5e03'
# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8aaf070872d9c1450172ea960440075f'

from ronglian_sms_sdk import SmsSDK
class CCP(object):
    def __new__(cls, *args, **kwargs):
        """
        定义单例的初始化方法
        :return: 单例
        """
        # 判断单例是否存在：_instance属性中存储的就是单例
        if not hasattr(cls,"_instance"):
            cls._instance = super(CCP, cls).__new__(cls,*args,**kwargs)

            cls._instance.setAccount = SmsSDK(_accountSid, _accountToken, _appId)
        #返回单例
        return cls._instance

    def send_template_sms(self, tid, mobile, datas):
        """
        发送短信验证码单例方法
        :param mobile: 手机号
        :param datas: 内容数据
        :param tid: 模板ID
        :return: 成功：0 失败：-1
        """
        # tid = '1'
        # mobile = '15280751466'
        # datas = (1, 2)
        resp = self.setAccount.sendMessage(tid, mobile, datas)
        print(type(resp))
        resp_dict = json.loads(resp)
        print(resp)
        if resp_dict.get("statusCode") == '000000':
            return 0
        else:
            return -1


#未优化
# def send_message():
#     sdk = SmsSDK(accId, accToken, appId)
#     tid = '1'
#     mobile = '15280751466'
#     datas = (1, 2)
#     resp = sdk.sendMessage(tid, mobile, datas)
#     print(resp)



# from celery_tasks.sms.tasks import send_sms_code

if __name__ == '__main__':
    tid = '1'
    mobile = '15280751466'
    sms_time = 2
    sms_code =  '%06d' % random.randint(0, 999999)
    # CCP().send_template_sms(tid, mobile, (sms_code,sms_time))
    #异步发送短信验证码
    # send_sms_code.delay(mobile,sms_code)
    print("hello")
