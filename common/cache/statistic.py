from flask import current_app
from sqlalchemy import func
from redis.exceptions import RedisError, ConnectionError

from models.news import Article, Attitude
from models.user import Relation
from models import db


class CountStorageBase(object):
    """
    统计数量存储的父类
    """
    key = ''

    @classmethod
    def get(cls, user_id):
        # 查询redis记录
        # 如果redis存在记录
        # 返回
        # 如果redis不存在记录，则返回0，表示用户没有发表过文章
        try:
            count = current_app.redis_master.zscore(cls.key, user_id)
        except ConnectionError as e:
            current_app.logger.error(e)
            count = current_app.redis_slave.zscore(cls.key, user_id)

        if count is None:
            return 0
        else:
            return int(count)

    @classmethod
    def incr(cls, user_id, increment=1):
        try:
            current_app.redis_master.zincrby(cls.key, user_id, increment)
        except ConnectionError as e:
            current_app.logger.error(e)
            raise e

    @classmethod
    def reset(cls, db_query_ret):
        """
        由定时任务调用的重置数据方法
        :return:
        """
        # 设置redis的存储记录
        pl = current_app.redis_master.pipeline()
        pl.delete(cls.key)

        # ret -> [
        # ( 1, 46141),
        # (2, 46357 ),
        # (3 ,46187)
        # ]

        # zadd(key, score1, val1, score2, val2, ...)
        # 方式一
        # for user_id, count in db_query_ret:
        #     pl.zadd(cls.key, count, user_id)

        # 方式二
        redis_data = []
        for user_id, count in db_query_ret:
            redis_data.append(count)
            redis_data.append(user_id)

        # redis_data = [count1, user_id1, count2, user_id2, ..]
        pl.zadd(cls.key, *redis_data)
        # pl.zadd(cls.key, count1, user_id1, count2, user_id2, ..]

        pl.execute()


class UserArticlesCountStorage(CountStorageBase):
    """
    用户文章数量
    """
    key = 'count:user:arts'

    @staticmethod
    def db_query():
        return db.session.query(Article.user_id, func.count(Article.id))\
            .filter(Article.status == Article.STATUS.APPROVED)\
            .group_by(Article.user_id).all()


class UserFollowingsCountStorage(CountStorageBase):
    """
    用户关注数量
    """
    key = 'count:user:followings'

    @staticmethod
    def db_query():
        return db.session.query(Relation.user_id, func.count(Relation.target_user_id)) \
            .filter(Relation.relation == Relation.RELATION.FOLLOW)\
            .group_by(Relation.user_id).all()


class UserFollowersCountStorage(CountStorageBase):
    """
    用户粉丝数量
    """
    key = 'count:user:followers'

    @staticmethod
    def db_query():
        ret = db.session.query(Relation.target_user_id, func.count(Relation.user_id)) \
            .filter(Relation.relation == Relation.RELATION.FOLLOW) \
            .group_by(Relation.target_user_id).all()
        return ret


class UserLikedCountStorage(CountStorageBase):
    """
    用户被赞数量
    """
    key = 'count:user:liked'

    @staticmethod
    def db_query():
        ret = db.session.query(Article.user_id, func.count(Attitude.id)).join(Attitude.article) \
            .filter(Attitude.attitude == Attitude.ATTITUDE.LIKING) \
            .group_by(Article.user_id).all()
        return ret


class ArticleCollectingCountStorage(CountStorageBase):
    """
    文章收藏数量
    """
    key = 'count:art:collecting'

    @staticmethod
    def db_query():
        ret = db.session.query(Collection.article_id, func.count(Collection.article_id)) \
            .filter(Collection.is_deleted == 0).group_by(Collection.article_id).all()
        return ret


class ArticleLikingCountStorage(CountStorageBase):
    """
    文章点赞数据
    """
    key = 'count:art:liking'

    @staticmethod
    def db_query():
        ret = db.session.query(Attitude.article_id, func.count(Collection.article_id)) \
            .filter(Attitude.attitude == Attitude.ATTITUDE.LIKING).group_by(Collection.article_id).all()
        return ret


class ArticleCommentCountStorage(CountStorageBase):
    """
    文章评论数量
    """
    key = 'count:art:comm'

    @staticmethod
    def db_query():
        ret = db.session.query(Comment.article_id, func.count(Comment.id)) \
            .filter(Comment.status == Comment.STATUS.APPROVED).group_by(Comment.article_id).all()
        return ret

