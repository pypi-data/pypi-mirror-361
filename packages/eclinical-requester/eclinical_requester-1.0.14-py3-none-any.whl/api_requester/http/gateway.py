# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/24/2023 3:48 PM
@Description: Description
@File: gateway.py
"""
import os.path
import re
from urllib.parse import urlparse

from requests.structures import LookupDict

from api_requester.utils.constant import AppEnum
from api_requester.utils.path import docs_path
from api_requester.utils.read_file import connect_to

_api = {
    AppEnum.ADMIN.code: (AppEnum.ADMIN.code,),
    AppEnum.EDC.code: (AppEnum.EDC.code,),
    AppEnum.CTMS.code: (AppEnum.CTMS.code,),
    AppEnum.ETMF.code: (AppEnum.ETMF.code,),
    AppEnum.DESIGN.code: ('designer', AppEnum.DESIGN.code),
    AppEnum.IWRS.code: (AppEnum.IWRS.code,),
    "external": ('external',),
    AppEnum.CODING.code: (AppEnum.CODING.code,),
    AppEnum.IMAGING.code: (AppEnum.IMAGING.code,),
    AppEnum.PV.code: (AppEnum.PV.code,),
}
apis = LookupDict(name='api')


def _init():
    for app_api, apps in _api.items():
        for app in apps:
            setattr(apis, app, app_api)


_init()


class Gateway(object):
    def __init__(self, test_env):
        self.test_env = test_env
        yaml_path = os.path.join(docs_path(), "application.yaml")
        self.api_yaml = connect_to(yaml_path).data

    def _url(self, app_api, api, external=False):
        server_url = self._server_url(app_api)
        api_url = self._ex_domain(app_api, api) or self._in_domain(app_api, api, external)
        return "{0}{1}".format(server_url, api_url)

    def _server_url(self, app_api):
        server_url_mapping = self.api_yaml["serverUrl"]
        server_url = server_url_mapping.get(self.test_env)
        if server_url is not None:
            return server_url
        else:
            postfix = dict(portal_api=".admin", ctms_api=".ctms", designer_api=".designer",
                           etmf_api=".etmf", edc_api=".edc", iwrs_api=".iwrs").get(app_api)
            return server_url_mapping.get("{0}{1}".format(self.test_env, postfix))

    def _in_domain(self, app_api, api, external=False):
        domain = self.api_yaml.get(app_api).get("urlPrefix")
        api_url = self._disposed(app_api, api) or self._not_disposed(api)
        return api_url if (external and domain in api_url) else "{0}{1}".format(domain, api_url)

    def _ex_domain(self, app_api, api):
        api_url = self._disposed(app_api, api) or self._not_disposed(api)
        if "local" in self.test_env:
            return api_url
        return None

    def _disposed(self, app_api, api):
        return self.api_yaml.get(app_api).get(api)

    @staticmethod
    def _not_disposed(api):
        return api

    @staticmethod
    def get_app_api(app):
        return eval(f"apis.{app.lower()}")

    def url(self, app, api, external=False):
        # if external:  # s3前端迁移
        #     self.test_env = f"{self.test_env}.external"
        tmp_url = self._url(self.get_app_api(external is False and app or "external"), api, external)
        return self.rewrite_path(app, tmp_url)

    def netloc(self, app):
        server_url = self._server_url(self.get_app_api(app))
        return urlparse(server_url).netloc

    def rewrite_path(self, app, api):
        app_config = self.api_yaml.get(app)
        filters = app_config.get("filters")
        if filters is not None:
            for item in filters:
                if item.startswith("RewritePath="):
                    item = item.replace("RewritePath=", "")
                    rewrite_rule, target = item.split(",")
                    api = re.sub(rewrite_rule, target, api)
        return api
