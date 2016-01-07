# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import logging.config

from redis import StrictRedis
import webassets
import webassets.filter
import csscompressor

this_dir = os.path.abspath(os.path.dirname(__file__))

class BasicConfig(object):
    REALM = 'Zone vesperal.org'
    SECRET_KEY = "ZjNzLW9EYmZhVUxRPkVrcE5KTVdicmkxNUZfMFZRQnlxLUxEak04RGFDMD0="
    SESSION_COOKIE_NAME = "quiet_reading_ssid"
    SESSION_COOKIE_HTTPONLY = True
    WTF_CSRF_ENABLED = True
    WTF_I18N_ENABLED = True
    EXECUTE_ENV = None
    APPLICATION_ROOT = "/quiet-reading"

    REDIS_SERVER = "127.0.0.1"
    REDIS_PORT = 6379
    REDIS_DB = 0
    REDIS_PREFIX = "quiet_"

    LOGGING_FILENAME = '/tmp/quiet-reading.log'
    LOGGING_LEVEL = 'INFO'
    DISABLE_EXISTING_LOGGERS = True

    @classmethod
    def setup_redis(cls, app):
        app.redis_conn = StrictRedis(host=cls.REDIS_SERVER, port=cls.REDIS_PORT, db=cls.REDIS_DB)
        app.redis_conn.ping()

    @classmethod
    def setup_logging(cls):
        logconf = {
            'version': 1,
            'disable_existing_loggers': cls.DISABLE_EXISTING_LOGGERS,
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
                    'filename': cls.LOGGING_FILENAME,
                    'encoding': 'utf-8'
                }
            },
            'loggers': {
                'manager': {
                    'handlers': ['console', 'f'],
                    'level': cls.LOGGING_LEVEL
                }
            },
            'root': {
                'handlers': [],
                'level': 'INFO'
            }
        }
        logging.config.dictConfig(logconf)

    @classmethod
    def init_app(cls, app):
        cls.setup_logging()
        cls.WTF_CSRF_SECRET_KEY = cls.SECRET_KEY
        app.config.from_object(cls)
        cls.setup_redis(app)
        cls.init_assets_env(app)
        cls.init_assets_bundles(app)

    @classmethod
    def init_assets_env(cls, app):
        webassets.filter.register_filter(CSSCompressor)
        app.assets = webassets.Environment(directory=os.path.join(this_dir, 'static'), url='static')
        app.assets.url_expire = True
        app.assets.manifest = 'cache'
        app.assets.cache = True
        app.assets.versions = 'hash'
        app.assets.config['PYSCSS_DEBUG_INFO'] = False
        app.assets.config['PYSCSS_STYLE'] = 'compact'

    @classmethod
    def init_assets_bundles(cls, app):

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

        app.assets.register('js_bundle', js_bundle)
        app.assets.register('css_bundle', css_bundle)


class DevConfig(BasicConfig):
    EXECUTE_ENV = "DEV"
    DEBUG = True
    SERVER_NAME = "127.0.0.1:8080"
    PREFERRED_URL_SCHEME = 'http'

    CHERRY = {
        'socket_host': b'127.0.0.1',
        'socket_port': 8080,
        'socket_timeout': 20,
        'queue_size': 20,
        'n_threads': 20,
        'autoreload': True,
        'print_logs': True
    }

    LOGGING_FILENAME = '/tmp/quiet-reading.log'
    LOGGING_LEVEL = 'DEBUG'
    DISABLE_EXISTING_LOGGERS = False

    @classmethod
    def init_assets_env(cls, app):
        BasicConfig.init_assets_env(app)
        app.assets.auto_build = True
        app.assets.debug = False


class ProdConfig(BasicConfig):
    EXECUTE_ENV = "PROD"
    DEBUG = False
    SERVER_NAME = "www.vesperal.org"
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    CHERRY = {
        'socket_host': b'127.0.0.1',
        'socket_port': 8080,
        'socket_timeout': 20,
        'queue_size': 20,
        'n_threads': 20,
        'autoreload': False,
        'print_logs': False
    }

    LOGGING_FILENAME = '/tmp/quiet-reading.log'
    LOGGING_LEVEL = 'INFO'
    DISABLE_EXISTING_LOGGERS = True

    @classmethod
    def init_assets_env(cls, app):
        BasicConfig.init_assets_env(app)
        app.assets.auto_build = False
        app.assets.debug = False

config = ProdConfig() if os.environ.get('QUIET_READING_ENV', None) == "PROD" else DevConfig()


class CSSCompressor(webassets.filter.Filter):
    name = 'csscompressor'

    def output(self, _in, out, **kw):
        out.write(csscompressor.compress(_in.read()))
