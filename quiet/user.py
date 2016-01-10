# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask.ext.login import UserMixin
from . import login_manager


class User(UserMixin):
    def __init__(self, id):
        self.id = id


def load_user(user_id):
    return User(user_id)
