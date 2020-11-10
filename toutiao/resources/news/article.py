from flask_restful import Resource, abort
from rpc import reco_pb2, reco_pb2_grpc
from flask import g, current_app
from flask_restful.reqparse import RequestParser
from flask_restful import inputs
from utils import parser
from . import constants
import time
from cache import article as cache_article
from utils.decorators import login_required, validate_token_if_using, set_db_to_write, set_db_to_read
from cache import user as cache_user
from cache import statistic as cache_statistic


class ArticleListResource(Resource):
    """
    获取推荐文章列表数据
    """
    def _feed_articles(self, channel_id, timestamp, feed_count):
        """
        获取推荐文章
        :param channel_id: 频道id
        :param feed_count: 推荐数量
        :param timestamp: 时间戳
        :return: [{article_id, trace_params}, ...], timestamp
        """
        user_request = reco_pb2.UserRequest()
        user_request.user_id = str(g.user_id) if g.user_id else 'anony'
        user_request.channel_id = channel_id
        user_request.article_num = feed_count
        user_request.time_stamp = timestamp

        stub = reco_pb2_grpc.UserRecommendStub(current_app.rpc_reco_channel)
        ret = stub.user_recommend(user_request)
        # ret -> ArticleResponse 对象
        exposure = ret.exposure
        pre_timestamp = ret.time_stamp
        recommends = ret.recommends

        return recommends, pre_timestamp

    def get(self):
        """
        获取文章列表
        """
        qs_parser = RequestParser()
        qs_parser.add_argument('channel_id', type=parser.channel_id, required=True, location='args')
        qs_parser.add_argument('timestamp', type=inputs.positive, required=True, location='args')
        args = qs_parser.parse_args()
        channel_id = args.channel_id
        timestamp = args.timestamp
        per_page = constants.DEFAULT_ARTICLE_PER_PAGE_MIN
        try:
            feed_time = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time()))
        except Exception:
            return {'message': 'timestamp param error'}, 400

        results = []

        # 获取推荐文章列表
        feeds, pre_timestamp = self._feed_articles(channel_id, timestamp, per_page)

        # 查询文章
        for feed in feeds:
            article = cache_article.ArticleInfoCache(feed.article_id).get()
            if article:
                article['pubdate'] = feed_time
                article['trace'] = {
                    'click': feed.track.click,
                    'collect': feed.track.collect,
                    'share': feed.track.share,
                    'read': feed.track.read
                }
                results.append(article)

        return {'pre_timestamp': pre_timestamp, 'results': results}


class ArticleResource(Resource):
    """
    文章
    """
    method_decorators = [validate_token_if_using]

    def get(self, article_id):
        """
        获取文章详情
        :param article_id: int 文章id
        """
        user_id = g.user_id
        # 查询文章数据
        exist = cache_article.ArticleInfoCache(article_id).exists()
        if not exist:
            abort(404, message='The article does not exist.')

        article = cache_article.ArticleDetailCache(article_id).get()

        article['is_followed'] = False
        article['attitude'] = None
        # 增加用户是否收藏了文章
        article['is_collected'] = False

        if user_id:
            # 非匿名用户添加用户的阅读历史
            try:
                cache_user.UserReadingHistoryStorage(user_id).save(article_id)
            except ConnectionError as e:
                current_app.logger.error(e)

        # 更新阅读数
        cache_statistic.ArticleReadingCountStorage.incr(article_id)
        cache_statistic.UserArticlesReadingCountStorage.incr(article['aut_id'])

        return article


