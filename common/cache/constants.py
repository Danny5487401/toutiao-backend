import random


# 默认用户头像
DEFAULT_USER_PROFILE_PHOTO = 'avator.png'  # 背景图

# 阅读历史每人保存数目
READING_HISTORY_COUNT_PER_USER = 100

# 全部频道缓存有效期，秒
ALL_CHANNELS_CACHE_TTL = 24 * 60 * 60

# 默认用户频道缓存有效期，秒
DEFAULT_USER_CHANNELS_CACHE_TTL = 24 * 60 * 60

# 用户搜索历史每人保存数目
SEARCHING_HISTORY_COUNT_PER_USER = 4

# 允许更新关注缓存的TTL限制，秒
ALLOW_UPDATE_FOLLOW_CACHE_TTL_LIMIT = 5


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


class UserStatusCacheTTL(BaseCacheTTL):
    """
    用户状态缓存时间，秒
    """
    TTL = 60 * 60


class UserChannelsCacheTTL(BaseCacheTTL):
    """
    用户频道缓存时间，秒
    """
    TTL = 60 * 60


class ArticleInfoCacheTTL(BaseCacheTTL):
    """
    文章信息缓存时间，秒
    """
    TTL = 30 * 60


class ArticleDetailCacheTTL(BaseCacheTTL):
    """
    文章详细内容缓存时间，秒
    """
    TTL = 60 * 60


class UserFollowingsCacheTTL(BaseCacheTTL):
    """
    用户关注列表缓存时间，秒
    """
    TTL = 30 * 60

class UserRelationshipNotExistsCacheTTL(BaseCacheTTL):
    """
    用户关系不存在数据缓存时间，秒
    """
    TTL = 5 * 60
    MAX_DELTA = 60

class UserArticleCollectionsCacheTTL(BaseCacheTTL):
    """
    用户文章收藏缓存时间，秒
    """
    TTL = 10 * 60
    MAX_DELTA = 2 * 60

