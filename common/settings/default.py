class DefaultConfig(object):
    pass

#Celery配置文件
class CeleryConfig(object):
    """
    Celery默认配置
    """
    #设置中间人 rabbitmq 指定消息队列的位置
    broker_url = 'amqp://admin:admin@81.68.197.3:5672/my_vhost'

    # task_routes = {
    #     'sms.*': {'queue': 'sms'},
    # }

