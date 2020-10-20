#定义任务
from celery_tasks.sms.yuntongxun.sms import CCP
from . import constants
from celery.utils.log import get_task_logger
tid = constants.SMS_VERIFICATION_CODE_TEMPLATE_ID
from celery_tasks.main import app



sms_time = constants.SMS_CODE_EXPIRES/60


# bind：保证task对象会作为第一个参数自动传入
# name：异步任务别名
# retry_backoff：异常自动重试的时间间隔 第n次(retry_backoff×2^(n-1))s
# max_retries：异常自动重试次数的上限
logger = get_task_logger(__name__)
# import time

@app.task(bind=True, name='sms.send_verification_code', retry_backoff=3)
def send_sms_code(self,mobile,sms_code):
    """
    发送短信验证码的异步任务
    :param self:
    :param mobile: 手机号
    :param sms_code: 验证码
    :return: 成功0，失败-1
    """
    try:
        # time.sleep(300)
        send_res = CCP().send_template_sms(tid, mobile, (sms_code, sms_time))
    except Exception as e:
        logger.error('[send_sms_code] {}'.format(e))
        raise self.retry(exc=e, max_retries=3)

    return send_res