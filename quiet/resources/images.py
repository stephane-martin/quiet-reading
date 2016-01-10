# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from io import BytesIO
from flask import current_app, send_file
from flask_restful import Resource

from ..imagestore import ImageStore

class Images(Resource):
    def get(self, h=None):
        if h is None:
            return "Bad request, man", 400
        image = ImageStore(current_app).get(h=h)
        if image is None:
            return "Image not found", 404
        return send_file(BytesIO(image.content), mimetype=image.content_type, add_etags=False, cache_timeout=3600)
