from flask import Flask
from flask_cors import CORS
from redis.exceptions import RedisError
import grpc
from elasticsearch5 import Elasticsearch


def create_flask_app(config, enable_config_file=False):
    """
    创建Flask应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: Flask应用
    """
    app = Flask(__name__)
    app.config.from_object(config)
    if enable_config_file:
        from utils import constants
        app.config.from_envvar(constants.GLOBAL_SETTING_ENV_NAME, silent=True)

    return app


def create_app(config, enable_config_file=False):
    """
    创建应用
    :param config: 配置信息对象
    :param enable_config_file: 是否允许运行环境中的配置文件覆盖已加载的配置信息
    :return: 应用
    """
    app = create_flask_app(config, enable_config_file)

    # 创建Snowflake ID worker
    from utils.snowflake.id_worker import IdWorker
    app.id_worker = IdWorker(app.config['DATACENTER_ID'],
                             app.config['WORKER_ID'],
                             app.config['SEQUENCE'])


    # 跨域
    CORS(app)

    # 添加请求钩子
    from utils.middlewares import jwt_authentication
    app.before_request(jwt_authentication)

    # 注册用户模块蓝图
    from .resources.user import user_bp
    app.register_blueprint(user_bp)

    # 注册新闻模块蓝图
    from .resources.news import news_bp
    app.register_blueprint(news_bp)

    # 搜索
    from .resources.search import search_bp
    app.register_blueprint(search_bp)

    # 限流器
    from utils.limiter import limiter as lmt
    lmt.init_app(app)

    # 配置日志
    from utils.logging import create_logger
    create_logger(app)

    # 注册url转换器
    from utils.converters import register_converters
    register_converters(app)

    # MySQL数据库连接初始化
    from models import db

    db.init_app(app)

    # 哨兵配置
    from redis.sentinel import Sentinel
    _sentinel = Sentinel(app.config['REDIS_SENTINELS'])
    app.redis_master = _sentinel.master_for(app.config['REDIS_SENTINEL_SERVICE_NAME'])
    app.redis_slave = _sentinel.slave_for(app.config['REDIS_SENTINEL_SERVICE_NAME'])

    # 集群配置
    from rediscluster import StrictRedisCluster
    app.redis_cluster = StrictRedisCluster(startup_nodes=app.config['REDIS_CLUSTER'])

    # rpc
    app.rpc_reco_channel = grpc.insecure_channel(app.config['RPC'].RECOMMEND)
    app.rpc_reco = app.rpc_reco_channel

    # Elasticsearch
    app.es = Elasticsearch(
        app.config['ES'],
        # sniff before doing anything
        sniff_on_start=True,
        # refresh nodes after a node fails to respond
        sniff_on_connection_fail=True,
        # and also every 60 seconds
        sniffer_timeout=60
    )

    return app
