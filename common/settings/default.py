class DefaultConfig(object):
    # 日志
    LOGGING_LEVEL = 'DEBUG'
    LOGGING_FILE_DIR = '/home/python/logs'
    LOGGING_FILE_MAX_BYTES = 300 * 1024 * 1024
    LOGGING_FILE_BACKUP = 10

    # JWT
    JWT_SECRET = 'TPmi4aLWRbyVq8zu9v82dWYW17/z+UvRnYTt4P6fAXA'
    JWT_EXPIRY_HOURS = 2
    JWT_REFRESH_DAYS = 14

    # rpc
    class RPC:
        RECOMMEND = '172.17.0.11:8010'
        # CHATBOT = '172.17.0.11:9999'

    RABBITMQ = 'amqp://admin:admin@81.68.197.3:5672/my_vhost'

    # flask-sqlalchemy使用的参数
    # SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1/toutiao'  # 数据库
    SQLALCHEMY_BINDS = {
        'bj-m1': 'mysql://root:123456@81.68.197.3:3307/toutiao',
        'bj-s1': 'mysql://root:123456@81.68.197.3:3308/toutiao',
        'masters': ['bj-m1'],
        'slaves': ['bj-s1'],
        'default': 'bj-m1'
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 追踪数据的修改信号
    SQLALCHEMY_ECHO = False  # SQLAlchemy 会记录所有 发给 stderr 的语句，这对调试有用

    # redis 哨兵
    REDIS_SENTINELS = [
        ('172.17.0.11', '26380'),
        ('172.17.0.11', '26381'),
        ('172.17.0.11', '26382'),
    ]
    REDIS_SENTINEL_SERVICE_NAME = 'mymaster'

    # redis 集群
    REDIS_CLUSTER = [
        {'host': '172.17.0.11', 'port': '7000'},
        {'host': '172.17.0.11', 'port': '7001'},
        {'host': '172.17.0.11', 'port': '7002'},
    ]

    # ES
    ES = [
        '172.17.0.11:9200'
    ]

    # # 限流服务redis
    # # RATELIMIT_STORAGE_URL = 'redis://127.0.0.1:6379/0'
    # RATELIMIT_STORAGE_URL = 'redis+sentinel://172.17.0.11:26380,127.0.0.1:26381,172.17.0.11:26382/mymaster'
    # RATELIMIT_STRATEGY = 'moving-window'
    # # RATELIMIT_DEFAULT = ['200/hour;1000/day']

    QINIU_ACCESS_KEY = 'b4hkdEqyufbchlsAj0Xm17MptIo9pBLxkd83pB3p'
    QINIU_SECRET_KEY = 'umDHZLmgiG7PC6exJmdKw6V4ITf2yDXzqH8x0i0w'
    QINIU_BUCKET_NAME = 'toutiao-app'
    QINIU_DOMAIN = 'http://qi2xepx1u.hd-bkt.clouddn.com/'

    # Snowflake ID Worker 参数
    DATACENTER_ID = 0
    WORKER_ID = 0
    SEQUENCE = 0

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

