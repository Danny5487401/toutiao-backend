from flask import current_app, g
from redis.exceptions import RedisError, ConnectionError
from models.user import User, Relation, UserProfile
from sqlalchemy.orm import load_only
from . import constants
import json
from cache import statistic as cache_statistic
from sqlalchemy.exc import SQLAlchemyError, DatabaseError
import time


class UserProfileCache(object):
    """
    用户信息缓存
    """
    def __init__(self, user_id):
        self.key = 'user:{}:profile'.format(user_id)
        self.user_id = user_id

    def save(self, user=None, force=False):
        """
        设置用户数据缓存
        """
        rc = current_app.redis_cluster

        # 判断缓存是否存在
        if force:
            exists = False
        else:
            try:
                ret = rc.get(self.key)
            except RedisError as e:
                current_app.logger.error(e)
                exists = False
            else:
                if ret == b'-1':
                    exists = False
                else:
                    exists = True

        if not exists:
            # This user cache data did not exist previously.
            if user is None:
                user = User.query.options(load_only(User.name,
                                                    User.mobile,
                                                    User.profile_photo,
                                                    User.is_media,
                                                    User.introduction,
                                                    User.certificate)) \
                    .filter_by(id=self.user_id).first()

            if user is None:
                return None

            user_data = {
                'mobile': user.mobile,
                'name': user.name,
                'photo': user.profile_photo or '',
                'is_media': user.is_media,
                'intro': user.introduction or '',
                'certi': user.certificate or '',
            }

            try:
                rc.setex(self.key, constants.UserProfileCacheTTL.get_val(), json.dumps(user_data))
            except RedisError as e:
                current_app.logger.error(e)
            return user_data

    def get(self):
        """
        获取用户数据
        :return:
        """
        rc = current_app.redis_cluster

        try:
            ret = rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            ret = None
        if ret:
            # hit cache
            user_data = json.loads(ret)
        else:
            user_data = self.save(force=True)

        user_data = self._fill_fields(user_data)

        if not user_data['photo']:
            user_data['photo'] = constants.DEFAULT_USER_PROFILE_PHOTO
        user_data['photo'] = current_app.config['QINIU_DOMAIN'] + user_data['photo']
        return user_data

    def _fill_fields(self, user_data):
        """
        补充字段
        """
        user_data['art_count'] = cache_statistic.UserArticlesCountStorage.get(self.user_id)
        user_data['follow_count'] = cache_statistic.UserFollowingsCountStorage.get(self.user_id)
        user_data['fans_count'] = cache_statistic.UserFollowersCountStorage.get(self.user_id)
        user_data['like_count'] = cache_statistic.UserLikedCountStorage.get(self.user_id)
        return user_data

    def clear(self):
        """
        清除
        """
        try:
            current_app.redis_cluster.delete(self.key)
        except RedisError as e:
            current_app.logger.error(e)

    def exists(self):
        """
        判断用户是否存在
        :return: bool
        """
        rc = current_app.redis_cluster

        # 此处可使用的键有三种选择 user:{}:profile 或 user:{}:status 或 新建
        # status主要为当前登录用户，而profile不仅仅是登录用户，覆盖范围更大，所以使用profile
        try:
            ret = rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            ret = None

        if ret is not None:
            return False if ret == b'-1' else True
        else:
            # 缓存中未查到
            user_data = self.save(force=True)
            if user_data is None:
                try:
                    rc.setex(self.key, constants.UserNotExistsCacheTTL.get_val(), -1)
                except RedisError as e:
                    current_app.logger.error(e)
                return False
            else:
                return True


class UserStatusCache(object):
    """
    用户状态缓存
    """
    def __init__(self, user_id):
        self.key = 'user:{}:status'.format(user_id)
        self.user_id = user_id

    def save(self, status):
        """
        设置用户状态缓存
        :param status:
        """
        try:
            current_app.redis_cluster.setex(self.key, constants.UserStatusCacheTTL.get_val(), status)
        except RedisError as e:
            current_app.logger.error(e)

    def get(self):
        """
        获取用户状态
        :return:
        """
        rc = current_app.redis_cluster

        try:
            status = rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            status = None

        if status is not None:
            return status
        else:
            user = User.query.options(load_only(User.status)).filter_by(id=self.user_id).first()
            if user:
                self.save(user.status)
                return user.status
            else:
                return False


class UserSearchingHistoryStorage(object):
    """
    用户搜索历史
    """
    def __init__(self, user_id):
        self.key = 'user:{}:his:searching'.format(user_id)
        self.user_id = user_id

    def save(self, keyword):
        """
        保存用户搜索历史
        :param keyword: 关键词
        :return:
        """
        pl = current_app.redis_master.pipeline()
        pl.zadd(self.key, time.time(), keyword)
        pl.zremrangebyrank(self.key, 0, -1*(constants.SEARCHING_HISTORY_COUNT_PER_USER+1))
        pl.execute()

    def get(self):
        """
        获取搜索历史
        """
        try:
            keywords = current_app.redis_master.zrevrange(self.key, 0, -1)
        except ConnectionError as e:
            current_app.logger.error(e)
            keywords = current_app.redis_slave.zrevrange(self.key, 0, -1)

        keywords = [keyword.decode() for keyword in keywords]
        return keywords

    def clear(self):
        """
        清除
        """
        current_app.redis_master.delete(self.key)


class UserReadingHistoryStorage(object):
    """
    用户阅读历史
    """
    def __init__(self, user_id):
        self.key = 'user:{}:his:reading'.format(user_id)
        self.user_id = user_id

    def save(self, article_id):
        """
        保存用户阅读历史
        :param article_id: 文章id
        :return:
        """
        try:
            pl = current_app.redis_master.pipeline()
            pl.zadd(self.key, time.time(), article_id)
            pl.zremrangebyrank(self.key, 0, -1*(constants.READING_HISTORY_COUNT_PER_USER+1))
            pl.execute()
        except RedisError as e:
            current_app.logger.error(e)

    def get(self, page, per_page):
        """
        获取阅读历史
        """
        r = current_app.redis_master
        try:
            total_count = r.zcard(self.key)
        except ConnectionError as e:
            r = current_app.redis_slave
            total_count = r.zcard(self.key)

        article_ids = []
        if total_count > 0 and (page - 1) * per_page < total_count:
            try:
                article_ids = r.zrevrange(self.key, (page - 1) * per_page, page * per_page - 1)
            except ConnectionError as e:
                current_app.logger.error(e)
                article_ids = current_app.redis_slave.zrevrange(self.key, (page - 1) * per_page, page * per_page - 1)

        return total_count, article_ids
