# vim: set fileencoding=utf-8 :

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from io import BytesIO
import pickle
from time import time
from hashlib import md5

from flask.ext.session import FileSystemSessionInterface
from werkzeug.contrib.cache import BaseCache
from future.builtins import str as str_unicode


def make_utf8(x):
    return x.encode('utf-8') if isinstance(x, str_unicode) else x


def get_idx(key):
    return make_utf8(md5(make_utf8(key)).hexdigest())


class LmdbCache(BaseCache):
    def __init__(self, lmdb_env, lmdb_db=None, threshold=500, default_timeout=300):
        BaseCache.__init__(self, default_timeout)
        self._threshold = threshold
        self.lmdb_env = lmdb_env
        self.lmdb_db = lmdb_db

    def _prune(self, parent_txn=None):
        with self.lmdb_env.begin(write=True, db=self.lmdb_db, parent=parent_txn) as txn:
            how_many_entries = len(list(txn.cursor().iternext(keys=True, values=False)))
            if how_many_entries > self._threshold:
                now = time()
                idx = 0
                to_remove = []
                for key, value in txn.cursor().iternext(keys=True, values=True):
                    value_f = BytesIO(value)
                    expires = pickle.load(value_f)
                    remove = (expires != 0 and expires <= now) or idx % 3 == 0
                    if remove:
                        to_remove.append(key)
                    idx += 1
                [txn.delete(key) for key in to_remove]

    def clear(self):
        with self.lmdb_env.begin(write=True, db=self.lmdb_db) as txn:
            txn.drop(delete=False)

    def get(self, key):
        try:
            idx = get_idx(key)
            with self.lmdb_env.begin(db=self.lmdb_db) as txn:
                value = txn.get(idx)
            if value is None:
                return None
            value_f = BytesIO(value)
            pickle_time = pickle.load(value_f)
            if pickle_time == 0 or pickle_time >= time():
                return pickle.load(value_f)
            else:
                with self.lmdb_env.begin(db=self.lmdb_db, write=True) as txn:
                    txn.delete(idx)
                    return None
        except pickle.PickleError:
            return None

    def add(self, key, value, timeout=None):
        idx = get_idx(key)
        with self.lmdb_env.begin(db=self.lmdb_db, write=True) as txn:
            value = txn.get(idx)
            if value is not None:
                return self.set(key, value, timeout, txn)
            return False

    def set(self, key, value, timeout=None, parent_txn=None):
        with self.lmdb_env.begin(db=self.lmdb_db, write=True, parent=parent_txn) as txn:
            self._prune(txn)
            if timeout is None:
                timeout = int(time() + self.default_timeout)
            elif timeout != 0:
                timeout = int(time() + timeout)
            idx = get_idx(key)
            value_f = BytesIO()
            pickle.dump(timeout, value_f, 1)
            pickle.dump(value, value_f, pickle.HIGHEST_PROTOCOL)
            txn.put(idx, value_f.getvalue())
            return True

    def delete(self, key):
        with self.lmdb_env.begin(db=self.lmdb_db, write=True) as txn:
            return txn.delete(get_idx(key))

    def has(self, key):
        try:
            idx = get_idx(key)
            with self.lmdb_env.begin(db=self.lmdb_db) as txn:
                value = txn.get(idx)
            if value is None:
                return False
            value_f = BytesIO(value)
            pickle_time = pickle.load(value_f)
            if pickle_time == 0 or pickle_time >= time():
                return True
            else:
                with self.lmdb_env.begin(db=self.lmdb_db, write=True) as txn:
                    txn.delete(idx)
                    return False
        except pickle.PickleError:
            return False



class LmdbSessionInterface(FileSystemSessionInterface):
    def __init__(self, lmdb_env, threshold=50000, use_signer=True, permanent=True, lmdb_db=None):
        self.cache = LmdbCache(lmdb_env, lmdb_db, threshold=threshold)
        self.key_prefix = ''
        self.use_signer = use_signer
        self.permanent = permanent
