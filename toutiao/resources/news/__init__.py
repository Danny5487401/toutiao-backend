from flask import Blueprint
from flask_restful import Api

from . import article
news_bp = Blueprint('news', __name__)
news_api = Api(news_bp, catch_all_404s=True)

news_api.add_resource(article.ArticleListResource, '/v1_0/articles',
                      endpoint='Articles')

