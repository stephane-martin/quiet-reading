# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from os.path import join, dirname, abspath
import logging.config

import flask
from flask.ext.login import LoginManager
from authomatic import Authomatic
import webassets
import webassets.filter
import csscompressor
import lmdb
from future.builtins import str as str_unicode

from .config import QuietConfig
from .lmdbcache import LmdbCache
from .lmdbcache import LmdbSessionInterface


def make_utf8(x):
    return x.encode('utf-8') if isinstance(x, str_unicode) else x


class QuietReadingFlask(flask.Flask):
    def __init__(self):
        super(QuietReadingFlask, self).__init__('quiet', static_url_path='/static', static_folder='static', template_folder='templates')
        self.assets = None

        self.lmdb_image_cache = None
        self.images_files_db = None
        self.images_index_db = None

        self.lmdb_cache_env = None
        self.article_cache = None

    def load_config(self, config_class):
        self.config.from_object(config_class())

    def setup_lmdb(self):
        self.lmdb_image_cache = lmdb.Environment(
            path=self.config['IMAGE_STORE_ROOT'],
            map_size=self.config['IMAGE_STORE_MAX_SIZE'],
            subdir=True,
            readonly=False,
            metasync=True,
            sync=True,
            map_async=False,
            create=True,
            readahead=False,
            writemap=False,
            meminit=True,
            max_dbs=4,
            lock=True,
            max_spare_txns=self.config['WAITRESS']['N_THREADS']
        )
        self.images_files_db = self.lmdb_image_cache.open_db(key=b"images_files")
        self.images_index_db = self.lmdb_image_cache.open_db(key=b"images_index")

        self.lmdb_cache_env = lmdb.Environment(
            path=self.config['CACHE_ROOT'],
            map_size=self.config['CACHE_MAX_SIZE'],
            subdir=True,
            readonly=False,
            metasync=True,
            sync=True,
            map_async=False,
            create=True,
            readahead=False,
            writemap=False,
            meminit=True,
            max_dbs=4,
            lock=True,
            max_spare_txns=self.config['WAITRESS']['N_THREADS']
        )

        lmdb_article_cache_db = self.lmdb_cache_env.open_db(key=b"article_cache")
        self.article_cache = LmdbCache(
            lmdb_env=self.lmdb_cache_env, lmdb_db=lmdb_article_cache_db, threshold=self.config['ARTICLE_CACHE_MAX_FILES'],
            default_timeout=3600
        )

        http_session_db = self.lmdb_cache_env.open_db(key=b"http_session")
        self.session_interface = LmdbSessionInterface(
            self.lmdb_cache_env, lmdb_db=http_session_db, threshold=self.config['SESSION_MAX_ITEMS']
        )

    def dealloc(self):
        if self.lmdb_image_cache:
            self.lmdb_image_cache.close()
        if self.lmdb_cache_env:
            self.lmdb_cache_env.close()

    def setup_assets(self):
        webassets.filter.register_filter(CSSCompressor)
        this_dir = abspath(dirname(__file__))
        self.assets = webassets.Environment(directory=join(this_dir, 'static'), url='static')
        self.assets.url_expire = True
        self.assets.manifest = 'cache'
        self.assets.cache = True
        self.assets.versions = 'hash'
        self.assets.config['PYSCSS_DEBUG_INFO'] = False
        self.assets.config['PYSCSS_STYLE'] = 'compact'
        self.assets.debug = False
        self.assets.auto_build = bool(self.config['DEBUG'])

        js_bundle = webassets.Bundle(
            'js/jquery.js', 'js/jquery.validate.js', 'js/additional-methods.js', 'js/bootstrap.js', 'js/ui.js',
            output='js/bundle.js', filters='jsmin'
        )

        scss_bundle = webassets.Bundle(
            'scss/article.scss', 'scss/ui.scss', filters='pyscss'
        )

        css_bundle = webassets.Bundle(
            'css/bootstrap.css', 'css/bootstrap-theme.css', scss_bundle,
            output="css/bundle.css", filters='csscompressor'
        )

        self.assets.register('js_bundle', js_bundle)
        self.assets.register('css_bundle', css_bundle)

    def setup_logging(self):
        logconf = {
            'version': 1,
            'disable_existing_loggers': self.config['DISABLE_EXISTING_LOGGERS'],
            'formatters': {
                'fileformat': {
                    'format': '%(asctime)s --- %(name)s --- %(process)d --- %(levelname)s --- %(message)s'
                },
                'consoleformat': {
                    'format': '%(levelname)s --- %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'level': 'DEBUG',
                    'class': 'logging.StreamHandler',
                    'formatter': 'consoleformat'
                },
                'f': {
                    'level': 'DEBUG',
                    'class': 'logging.FileHandler',
                    'formatter': 'fileformat',
                    'filename': self.config['LOGGING_FILENAME'],
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                'manager': {
                    'handlers': ['console', 'f'],
                    'level': self.config['LOGGING_LEVEL']
                }
            },
            'root': {
                'handlers': [],
                'level': 'INFO'
            }
        }
        logging.config.dictConfig(logconf)

    def setup_login_manager(self):
        login_manager.init_app(self)
        my_auth.config = self.config['AUTH_CONFIG']
        my_auth.secret = make_utf8(self.config['SECRET_KEY'])
        my_auth.debug = self.config['DEBUG']

    def setup(self):
        self.setup_logging()
        self.setup_lmdb()
        self.setup_assets()
        self.setup_login_manager()


class CSSCompressor(webassets.filter.Filter):
    name = 'csscompressor'

    def output(self, _in, out, **kw):
        out.write(csscompressor.compress(_in.read()))

application = QuietReadingFlask()
login_manager = LoginManager()
my_auth = Authomatic({}, '')


