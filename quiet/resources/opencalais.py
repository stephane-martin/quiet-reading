# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import json

from flask import request, make_response, render_template, current_app
from flask_restful import Resource
import requests
import jmespath

from . import make_calais_parser, what_request_wants, get_assets_urls
from ..article import Article

OC_URL = 'https://api.thomsonreuters.com/permid/calais'
OC_ENTIES = 'values(@)[?_typeGroup==`entities`].{t:_type, group:_typeGroup, name:name}'
OC_SOCIAL = 'values(@)[?_typeGroup==`socialTag`].name'
OC_TOPICS = 'values(@)[?_typeGroup==`topics`].name'

OC_ENTIES = jmespath.compile(OC_ENTIES)
OC_SOCIAL = jmespath.compile(OC_SOCIAL)
OC_TOPICS = jmespath.compile(OC_TOPICS)


class OpenCalais(Resource):
    def _do(self):
        article_cache = current_app.article_cache
        args = make_calais_parser().parse_args()
        t = what_request_wants(request)
        if (not args.target) and (not args.text):
            if t == 'html':
                tpl = render_template('calais.html', assets=get_assets_urls(), calais_results=None)
                return make_response(tpl, 200, {'Content-Type': 'text/html; charset=utf-8'})
            return "provide either 'target' or 'text'", 400
        article = None
        if args.target:
            try:
                article = Article.fetch(url=args.get('target', ''), article_cache=article_cache)
            except requests.RequestException as ex:
                return str(ex), 500
            article.to_cache(article_cache)
            args.text = article.text

        if not args.text:
            return "text is empty", 400

        headers = {
            'Content-Type': 'text/raw',
            'omitOutputtingOriginalText': 'true',
            'outputFormat': 'application/json',
            'x-ag-access-token': current_app.config['OPENCALAIS_API_KEY'],
            'x-calais-contentClass': 'news',
        }

        try:
            resp = requests.post(OC_URL, data=args.text.encode('utf-8'), headers=headers)
            resp.raise_for_status()
        except requests.RequestException as ex:
            return str(ex), 500

        d = json.loads(resp.content.decode('utf-8').replace('\u2019', "'"))
        d = _parse_calais_resp(d)
        d['title'] = article.title if article else ''
        d['url'] = article.url if article else ''

        if t == "json":
            return d
        elif t == "pdf":
            pass
        elif t == "plain":
            pass
        else:
            tpl = render_template(
                'calais.html', assets=get_assets_urls(), calais_results=d
            )
            return make_response(tpl, 200, {'Content-Type': 'text/html; charset=utf-8'})

    def get(self):
        return self._do()

    def post(self):
        return self._do()


def _parse_calais_resp(d):
    dict_entities, list_social, list_topics = OC_ENTIES.search(d), OC_SOCIAL.search(d), OC_TOPICS.search(d)
    res = {
        'entities': {},
        'social_tags': list_social,
        'topics': list_topics
    }

    types = set(obj['t'] for obj in dict_entities)
    for t in types:
        res['entities'][t] = [obj['name'] for obj in dict_entities if obj['t'] == t]

    return res
