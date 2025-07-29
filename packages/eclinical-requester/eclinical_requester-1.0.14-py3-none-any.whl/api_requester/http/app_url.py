# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/24/2023 3:48 PM
@Description: Description
@File: app_url.py
"""
from api_requester.http.gateway import Gateway
from api_requester.utils.constant import AppEnum


class AppUrl(object):
    def __init__(self, app, test_env):
        self.app = app
        self.test_env = test_env

    def _app_url(self, api, app, external=False, **kwargs):
        return Gateway(self.test_env).url(app, api, external).format(**kwargs)

    def app_url(self, api, **kwargs):
        return self._app_url(api, self.app, **kwargs)

    def portal_url(self, api, **kwargs):
        return self._app_url(api, AppEnum.ADMIN.code, **kwargs)

    def external_url(self, api, **kwargs):
        return self._app_url(api, self.app, True, **kwargs)

    def which_url(self, app):
        return self.portal_url if app == AppEnum.ADMIN.code else self.app_url
