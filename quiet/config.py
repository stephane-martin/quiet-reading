# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
from os.path import join, exists, abspath, expanduser
from datetime import timedelta

from future.builtins import str as str_unicode
import pytoml as toml
import authomatic
import authomatic.providers.oauth2


this_dir = os.path.abspath(os.path.dirname(__file__))
CONFIG_FILE_PATH_ENVVAR = 'QUIET_READING_CONFIG_PATH'


class QuietConfig(object):
    SECRET_KEY = ""
    USE_X_SENDFILE = False
    SESSION_COOKIE_NAME = "quiet_reading_ssid"
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_DURATION = 2592000
    WTF_CSRF_ENABLED = True
    WTF_I18N_ENABLED = True
    EXECUTE_ENV = ""
    APPLICATION_ROOT = "/quiet-reading"

    LOGGING_FILENAME = '/tmp/quiet-reading.log'
    LOGGING_LEVEL = 'INFO'
    DISABLE_EXISTING_LOGGERS = True
    WAITRESS = {
        'SOCKET_HOST': b'127.0.0.1',
        'SOCKET_PORT': 8080,
        'SOCKET_TIMEOUT': 20,
        'N_THREADS': 20,
    }

    OPENCALAIS_API_KEY = ""
    IMAGE_STORE_ROOT = join(this_dir, 'dl_images')
    IMAGE_STORE_MAX_SIZE = 30 * 1024 * 1024 * 1024
    CACHE_ROOT = join(this_dir, 'cache')
    CACHE_MAX_SIZE = 30 * 1024 * 1024 * 1024

    AUTH_CONFIG = {}

    GITHUB = {
        'CONSUMER_KEY': '',
        'CONSUMER_SECRET': '',
        'USER_AGENT': 'quiet-reading-TEST'
    }

    REDDIT = {
        'CONSUMER_KEY': '',
        'CONSUMER_SECRET': '',
        'USER_AGENT': 'quiet-reading-TEST'
    }

    LINKEDIN = {
        'CONSUMER_KEY': '',
        'CONSUMER_SECRET': '',
    }

    def load_config_from_config_file(self):
        filepath = os.environ.get(CONFIG_FILE_PATH_ENVVAR)
        if filepath:
            if exists(filepath):
                with open(filepath, 'rb') as f:
                    self.inject_toml_conf(toml.load(f))

    def inject_toml_conf(self, toml_conf):
        for key, val in toml_conf.items():
            k = key.upper()
            if isinstance(val, dict):
                if k in ['FLASK', 'COOKIES', 'LOGGING', 'OPENCALAIS', 'IMAGES_STORE', 'LMDB_CACHE']:
                    for option_name, option_val in val.items():
                        self.__setattr__(option_name.upper(), option_val)
                else:
                    if not hasattr(self, k):
                        self.__setattr__(k, {})
                    d = self.__getattribute__(k)
                    [d.__setitem__(option_name.upper(), option_val) for (option_name, option_val) in val.items()]
            elif isinstance(val, str_unicode):
                self.__setattr__(k, val)

    def set_authomatic_providers(self):
        self.AUTH_CONFIG = {}
        if bool(self.GITHUB['CONSUMER_KEY']) and bool(self.GITHUB['CONSUMER_SECRET']):
            self.AUTH_CONFIG['github'] = {
                'class_': authomatic.providers.oauth2.GitHub,
                'scope': [],
                'id': authomatic.provider_id(),
                'access_headers': {'User-Agent': self.GITHUB['USER_AGENT']},
                'consumer_key': self.GITHUB['CONSUMER_KEY'],
                'consumer_secret': self.GITHUB['CONSUMER_SECRET']
            }

        if bool(self.REDDIT['CONSUMER_KEY']) and bool(self.REDDIT['CONSUMER_SECRET']):
            self.AUTH_CONFIG['reddit'] = {
                'class_': authomatic.providers.oauth2.Reddit,
                'scope': ['identity'],
                'id': authomatic.provider_id(),
                'access_headers': {'User-Agent': self.REDDIT['USER_AGENT']},
                'consumer_key': self.REDDIT['CONSUMER_KEY'],
                'consumer_secret': self.REDDIT['CONSUMER_SECRET']
            }

        if bool(self.LINKEDIN['CONSUMER_KEY']) and bool(self.LINKEDIN['CONSUMER_SECRET']):
            self.AUTH_CONFIG['linkedin'] = {
                'class_': authomatic.providers.oauth2.LinkedIn,
                'scope': [],
                'id': authomatic.provider_id(),
                'consumer_key': self.LINKEDIN['CONSUMER_KEY'],
                'consumer_secret': self.LINKEDIN['CONSUMER_SECRET']
            }

    def __init__(self):
        self.load_config_from_config_file()
        self.WTF_CSRF_SECRET_KEY = self.SECRET_KEY
        self.IMAGE_STORE_ROOT = abspath(expanduser(self.IMAGE_STORE_ROOT))
        self.CACHE_ROOT = abspath(expanduser(self.CACHE_ROOT))
        self.REMEMBER_COOKIE_DURATION = timedelta(seconds=self.REMEMBER_COOKIE_DURATION)
        self.set_authomatic_providers()


class ProdConfig(object):
    EXECUTE_ENV = "PROD"
    DEBUG = False
    SERVER_NAME = "www.vesperal.org"
    PREFERRED_URL_SCHEME = 'https'
    SESSION_COOKIE_SECURE = True
    WAITRESS = {
        'socket_host': b'127.0.01',
        'socket_port': 8080,
        'socket_timeout': 20,
        'n_threads': 100,
    }

    LOGGING_FILENAME = '/tmp/quiet-reading.log'
    LOGGING_LEVEL = 'INFO'
    DISABLE_EXISTING_LOGGERS = True

