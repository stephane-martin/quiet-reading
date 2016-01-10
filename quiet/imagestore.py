# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import collections
import json

import flask
import requests
import spooky
from future.builtins import str as str_unicode

from concurrent.futures import ThreadPoolExecutor

stack = flask._app_ctx_stack


def url2hash(url):
    return b'%x' % spooky.hash128(make_utf8(url))


def make_utf8(x):
    return x.encode('utf-8') if isinstance(x, str_unicode) else x


class Image(collections.namedtuple("Image", ['url', 'final_url', 'content', 'content_length', 'content_type'])):
    def to_json(self):
        return json.dumps({
            'Content-Length': self.content_length,
            'Content-Type': self.content_type,
            'final_url': self.final_url,
            'url': self.url
        })

    @classmethod
    def fetch(cls, url):
        try:
            resp = requests.get(url)
            resp.raise_for_status()
        except requests.RequestException as ex:
            raise ValueError("fetching the image failed with '{}'".format(str(ex)))
        if 'image' not in resp.headers.get('Content-Type'):
            raise ValueError("Content-type for the URL was not about an image")
        return Image(
            url=url,
            final_url=resp.url,
            content=resp.content,
            content_length=resp.headers.get('Content-Length', -1),
            content_type=resp.headers['Content-Type']
        )

    @property
    def hash(self):
        return url2hash(self.url)


def dl(url):
    try:
        return url, Image.fetch(url)
    except ValueError:
        return url, None


class ImageStore(object):
    def __init__(self, current_app):
        self.current_app = current_app
        self.lmdb = current_app.lmdb_image_cache
        self.images_index_db = current_app.images_index_db
        self.images_files_db = current_app.images_files_db

    def endpoint(self, h):
        if stack.top is None:
            with self.current_app.app_context():
                return flask.url_for("images", h=h, _external=True)
        else:
            return flask.url_for("images", h=h, _external=True)

    def get(self, url=None, h=None):
        if url is None and h is None:
            return
        h = url2hash(url) if not h else make_utf8(h)
        with self.lmdb.begin(db=self.images_index_db) as txn:
            idx = txn.get(h)
        if idx is None:
            return
        metadata = json.loads(idx)
        with self.lmdb.begin(db=self.images_files_db) as txn2:
            content = txn2.get(h)
        if content is None:
            return
        return Image(
            url=url,
            final_url=metadata['final_url'],
            content=content,
            content_length=metadata['Content-Length'],
            content_type=metadata['Content-Type']
        )

    def add(self, url):
        with self.lmdb.begin(db=self.images_index_db, write=True) as txn:
            h = url2hash(url)
            if txn.get(h) is not None:
                return self.endpoint(h)
            try:
                image = Image.fetch(url)
            except ValueError:
                return None
            txn.put(h, image.to_json())
            with self.lmdb.begin(db=self.images_files_db, write=True, parent=txn) as txn2:
                txn2.put(h, image.content)
            return self.endpoint(h)

    def add_many(self, urls):

        with self.lmdb.begin(db=self.images_index_db, write=True) as txn:
            if len(urls) == 0:
                return {}
            urls = set(urls)
            already_exists = [(url, txn.get(url2hash(url)) is not None) for url in urls]
            existing_urls = set([url for (url, boolean) in already_exists if boolean])
            urls_to_upload = urls.difference(existing_urls)
            if len(urls_to_upload) == 0:
                return {url: self.endpoint(url2hash(url)) for url in urls}

            with ThreadPoolExecutor(max_workers=len(urls)) as exe:
                list_of_images = list(exe.map(dl, urls))

            downloaded_imgs = [image for (url, image) in list_of_images if image is not None]
            failed_uploads = [url for (url, image) in list_of_images if image is None]

            for image in downloaded_imgs:
                h = image.hash
                txn.put(h, image.to_json())
                with self.lmdb.begin(db=self.images_files_db, write=True, parent=txn) as txn2:
                    txn2.put(h, image.content)
            results = {image.url: self.endpoint(image.hash) for image in downloaded_imgs}
            results.update({url: None for url in failed_uploads})
            results.update({url: self.endpoint(url2hash(url)) for url in existing_urls})
            return results

    def keys(self):
        pass

    def delete(self, url=None, h=None):
        if url is None and h is None:
            return
        with self.lmdb.begin(db=self.images_index_db, write=True) as txn:
            h = url2hash(url) if not h else make_utf8(h)
            txn.pop(h)
            with self.lmdb.begin(db=self.images_files_db, write=True, parent=txn) as txn2:
                txn2.pop(h)
                return True

    def __contains__(self, url=None, h=None):
        if url is None and h is None:
            return False
        h = url2hash(url) if not h else make_utf8(h)
        with self.lmdb.begin(db=self.images_index_db) as txn:
            return txn.get(h) is not None
