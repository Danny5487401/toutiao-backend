class DefaultConfig(object):
    # JWT
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    JWT_EXPIRY_HOURS = 2
    JWT_REFRESH_DAYS = 14

    RABBITMQ = 'amqp://admin:admin@81.68.197.3:5672/my_vhost'

    # CORS
    # TODO 调试后要修改
    CORS_ORIGINS = '*'

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

