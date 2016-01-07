# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import current_app
from flask_restful import reqparse, inputs


def make_parser():
    parser_url = reqparse.RequestParser()
    parser_url.add_argument('target', type=inputs.url, help="Provide a URL for 'target' parameter")
    parser_url.add_argument('h', help="Provide a valid ID")
    return parser_url


def what_request_wants(req):
    best = req.accept_mimetypes.best_match(['text/html', 'application/json', 'application/pdf', 'text/plain'])
    if best == 'application/json':
        return 'html' if req.accept_mimetypes[best] == req.accept_mimetypes['text/html'] else 'json'
    if best == 'application/pdf':
        return 'html' if req.accept_mimetypes[best] == req.accept_mimetypes['text/html'] else 'pdf'
    if best == 'text/plain':
        return 'html' if req.accept_mimetypes[best] == req.accept_mimetypes['text/html'] else 'plain'
    return 'html'


def get_assets_urls():
    return {
        'js': current_app.assets['js_bundle'].urls(),
        'css': current_app.assets['css_bundle'].urls()
    }
