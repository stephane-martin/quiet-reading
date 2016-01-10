# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from flask import make_response, request, render_template, redirect, url_for
from flask_restful import Resource
from flask.ext.login import login_user, logout_user

import authomatic.adapters

from .. import my_auth
from ..user import User


userid_attr = {
    'github': 'login',
    'reddit': 'name',
    'linkedin': 'id'
}


class OauthLogin(Resource):
    def _do(self, provider_name):
        response = make_response()
        result = my_auth.login(authomatic.adapters.WerkzeugAdapter(request, response), provider_name)
        if result:
            if result.user:
                result.user.update()
                my_user = User("{}-{}".format(provider_name, result.user.data[userid_attr[provider_name]]))
                login_user(my_user, remember=True)
                print(result.user.data)
                return redirect(url_for('index'))
            return make_response(
                render_template('a_login.html', result=result), 200, {'Content-Type': 'text/html; charset=utf-8'}
            )
        return response

    def get(self, provider_name=None):
        if provider_name is None:
            return make_response(
                render_template('a_index.html'), 200, {'Content-Type': 'text/html; charset=utf-8'}
            )
        return self._do(provider_name)

    def post(self, provider_name=None):
        if provider_name is None:
            return redirect(url_for('index'))
        return self._do(provider_name)


class Logout(Resource):
    def get(self):
        return self._do()

    def post(self):
        return self._do()

    def _do(self):
        logout_user()
        return redirect(url_for('index'))
