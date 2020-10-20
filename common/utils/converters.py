<<<<<<< HEAD
from werkzeug.routing import BaseConverter


class MobileConverter(BaseConverter):
    """
    手机号格式
    """
    regex = r'1[3-9]\d{9}'


def register_converters(app):
    """
    向Flask app中注册转换器
    :param app: Flask app对象
    :return:
    """
    app.url_map.converters['mobile'] = MobileConverter
=======
from werkzeug.routing import BaseConverter


class MobileConverter(BaseConverter):
    """
    手机号格式
    """
    regex = r'1[3-9]\d{9}'


def register_converters(app):
    """
    向Flask app中注册转换器
    :param app: Flask app对象
    :return:
    """
    app.url_map.converters['mobile'] = MobileConverter
>>>>>>> e834388b2bd5275608c69e52dec55b044d66af04
