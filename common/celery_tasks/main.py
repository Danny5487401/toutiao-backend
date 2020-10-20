from celery import Celery
from settings.default import CeleryConfig

#创建实例=生产者 参数意义不大，只是标识
app = Celery('toutiao')
# 加载中间人
app.config_from_object(CeleryConfig)

# 自动注册celery任务
app.autodiscover_tasks(['celery_tasks.sms'])
