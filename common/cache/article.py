from flask_restful import fields, marshal
from flask import current_app
from models.news import Article
from sqlalchemy.orm import joinedload, load_only
from redis.exceptions import RedisError, ConnectionError
from . import constants
import json
from cache import user as cache_user
from cache import statistic as cache_statistic


class ArticleInfoCache(object):
    """
    文章基本信息缓存
    """
    article_info_fields_db = {
        'title': fields.String(attribute='title'),
        'aut_id': fields.Integer(attribute='user_id'),
        'pubdate': fields.DateTime(attribute='ctime', dt_format='iso8601'),
        'ch_id': fields.Integer(attribute='channel_id'),
        'allow_comm': fields.Integer(attribute='allow_comment'),
    }

    def __init__(self, article_id):
        self.key = 'art:{}:info'.format(article_id)
        self.article_id = article_id

    def save(self):
        """
        保存文章缓存
        """
        rc = current_app.redis_cluster

        article = Article.query.options(load_only(Article.id, Article.title, Article.user_id, Article.channel_id,
                                                  Article.cover, Article.ctime, Article.allow_comment))\
            .filter_by(id=self.article_id, status=Article.STATUS.APPROVED).first()
        if article is None:
            return

        article_formatted = marshal(article, self.article_info_fields_db)
        article_formatted['cover'] = article.cover

        # 判断是否置顶
        try:
            article_formatted['is_top'] = ChannelTopArticlesStorage(article.channel_id).exists(self.article_id)
        except RedisError as e:
            current_app.logger.error(e)
            article_formatted['is_top'] = 0

        try:
            rc.setex(self.key, constants.ArticleInfoCacheTTL.get_val(), json.dumps(article_formatted))
        except RedisError as e:
            current_app.logger.error(e)

        return article_formatted

    def _fill_fields(self, article_formatted):
        """
        补充字段
        """
        article_formatted['art_id'] = self.article_id
        # 获取作者名
        author = cache_user.UserProfileCache(article_formatted['aut_id']).get()
        article_formatted['aut_name'] = author['name']
        article_formatted['comm_count'] = cache_statistic.ArticleCommentCountStorage.get(self.article_id)
        article_formatted['like_count'] = cache_statistic.ArticleLikingCountStorage.get(self.article_id)
        article_formatted['collect_count'] = cache_statistic.ArticleCollectingCountStorage.get(self.article_id)
        return article_formatted

    def get(self):
        """
        获取文章
        :return: {}
        """
        rc = current_app.redis_cluster

        # 从缓存中查询
        try:
            article = rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            article = None

        if article:
            article_formatted = json.loads(article)
        else:
            article_formatted = self.save()

        if not article_formatted:
            return None

        article_formatted = self._fill_fields(article_formatted)
        del article_formatted['allow_comm']

        return article_formatted

    def exists(self):
        """
        判断文章是否存在
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
            article = self.save()
            if article is None:
                return False
            else:
                return True

    def determine_allow_comment(self):
        """
        判断是否允许评论
        """
        rc = current_app.redis_cluster
        try:
            ret = rc.get(self.key)
        except RedisError as e:
            current_app.logger.error(e)
            ret = None

        if ret is None:
            article_formatted = self.save()
        else:
            article_formatted = json.loads(ret)

        return article_formatted['allow_comm']

    def clear(self):
        rc = current_app.redis_cluster
        rc.delete(self.key)


class ChannelTopArticlesStorage(object):
    """
    频道置顶文章缓存
    使用redis持久保存
    """
    def __init__(self, channel_id):
        self.key = 'ch:{}:art:top'.format(channel_id)
        self.channel_id = channel_id

    def get(self):
        """
        获取指定频道的置顶文章id
        :return: [article_id, ...]
        """
        try:
            ret = current_app.redis_master.zrevrange(self.key, 0, -1)
        except ConnectionError as e:
            current_app.logger.error(e)
            ret = current_app.redis_slave.zrevrange(self.key, 0, -1)

        if not ret:
            return []
        else:
            return [int(article_id) for article_id in ret]

    def exists(self, article_id):
        """
        判断文章是否置顶
        :param article_id:
        :return:
        """
        try:
            rank = current_app.redis_master.zrank(self.key, article_id)
        except ConnectionError as e:
            current_app.logger.error(e)
            rank = current_app.redis_slave.zrank(self.key, article_id)

        return 0 if rank is None else 1