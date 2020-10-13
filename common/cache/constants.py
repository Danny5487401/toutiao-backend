import random


# 默认用户头像
DEFAULT_USER_PROFILE_PHOTO = 'Fkj6tQi3xJwVXi1u2swCElotfdCi'  # 程序猿


class BaseCacheTTL(object):
    """
    缓存有效期
    为防止缓存雪崩，在设置缓存有效期时采用设置不同有效期的方案
    通过增加随机值实现
    """
    TTL = 0  # 由子类设置
    MAX_DELTA = 10 * 60  # 随机的增量上限

    @classmethod
    def get_val(cls):
        return cls.TTL + random.randrange(0, cls.MAX_DELTA)


class UserProfileCacheTTL(BaseCacheTTL):
    """
    用户资料数据缓存时间, 秒
    """
    TTL = 30 * 60


class UserNotExistsCacheTTL(BaseCacheTTL):
    """
    用户不存在结果缓存
    为解决缓存击穿，有效期不宜过长
    """
    TTL = 5 * 60
    MAX_DELTA = 60
