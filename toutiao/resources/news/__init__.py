from flask import Blueprint
from flask_restful import Api
from utils.output import output_json

from . import article, channel, collection
news_bp = Blueprint('news', __name__)
news_api = Api(news_bp, catch_all_404s=True)
news_api.representation('application/json')(output_json)

news_api.add_resource(article.ArticleListResource, '/v1_0/articles',
                      endpoint='Articles')

news_api.add_resource(article.ArticleResource, '/v1_0/articles/<int(min=1):article_id>',
                      endpoint='Article')

news_api.add_resource(channel.ChannelListResource, '/v1_0/channels',
                      endpoint='Channels')

# 收藏文章
news_api.add_resource(collection.CollectionListResource, '/v1_0/article/collections',
                      endpoint='ArticleCollections')

# 取消收藏文章
news_api.add_resource(collection.CollectionResource, '/v1_0/article/collections/<int(min=1):target>',
                      endpoint='ArticleCollection')


