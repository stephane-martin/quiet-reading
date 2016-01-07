# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import request, make_response, render_template, current_app
from flask_restful import Resource
import requests

from ..article import Article
from . import make_parser, what_request_wants, get_assets_urls


class Cleaning(Resource):

    def _do(self):
        args = make_parser().parse_args()
        if args.target and args.h:
            return "provide 'target' OR 'h'", 400
        elif (not args.target) and (not args.h):
            return "provide either 'target' or 'h'", 400

        try:
            article = Article.fetch(url=args.get('target', ''), id=args.get('h', ''), redis_conn=current_app.redis_conn)
        except requests.RequestException as ex:
            return str(ex), 500
        else:
            article.to_redis(current_app.redis_conn)

        t = what_request_wants(request)
        if t == "json":
            return {
                'title': article.title,
                'content': article.summary,
                'url': article.url,
                'h': article.id
            }
        elif t == "pdf":
            pass
        elif t == "plain":
            pass
        else:
            article = render_template(
                'article.html', title=article.title, content=article.summary, url=article.url, assets=get_assets_urls()
            )
            return make_response(article, 200, {'mimetype': 'text/html'})

    def get(self):
        return self._do()

    def post(self):
        return self._do()
