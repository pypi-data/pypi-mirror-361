"""
@Author: xiaodong.li
@Date: 2023-07-25 13:33:15
LastEditors: xiaodong.li
LastEditTime: 2023-07-25 13:33:15
@Description: eclinical_requests.py
"""
import copy
import os
import time
from functools import wraps

import requests
from requests import Response
from requests_toolbelt import MultipartEncoder

from api_requester.dto.base_dto import BaseDto, build_file_dto
from api_requester.dto.biz_base import BizBase
from api_requester.http.app_url import AppUrl
from api_requester.http.exceptions import ApiResponseException
from api_requester.http.sample_headers import SampleHeaders


def get(api):
    def __wrapper__(func):
        @url(api)
        @build_request_data()
        @refresh_token()
        @refresh_headers()
        @get_request()
        @http_ok
        def __inner__(instance: BizBase, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def post(api):
    def __wrapper__(func):
        @url(api)
        @build_request_data()
        @refresh_token()
        @refresh_headers()
        @post_request()
        @http_ok
        def __inner__(instance: BizBase, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def delete(api):
    def __wrapper__(func):
        @url(api)
        @build_request_data()
        @refresh_token()
        @refresh_headers()
        @delete_request()
        @http_ok
        def __inner__(instance: BizBase, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def put(api):
    def __wrapper__(func):
        @url(api)
        @build_request_data()
        @refresh_token()
        @refresh_headers()
        @put_request()
        @http_ok
        def __inner__(instance: BizBase, *args, **kwargs):
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def get_request():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            app_url = kwargs.pop("app_url")
            rsp = requests.get(app_url, **kwargs)
            kwargs.update(rsp=rsp)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def post_request():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            app_url = kwargs.pop("app_url")
            rsp = requests.post(app_url, **kwargs)
            kwargs.update(rsp=rsp)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def delete_request():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            app_url = kwargs.pop("app_url")
            rsp = requests.delete(app_url, **kwargs)
            kwargs.update(rsp=rsp)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def put_request():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            app_url = kwargs.pop("app_url")
            rsp = requests.put(app_url, **kwargs)
            kwargs.update(rsp=rsp)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def url(api):
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            url_kwargs = kwargs.pop("url_kwargs", {})
            if instance.user.external is False:
                app_url = AppUrl(instance.user.app, instance.user.test_env).which_url(
                    instance.user.app)(api, **url_kwargs)
            else:
                app_url = AppUrl(instance.user.app, instance.user.test_env).external_url(api, **url_kwargs)
            if app_url is None:
                raise Exception("The url is null.")
            kwargs.update(app_url=app_url)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def build_request_data():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            for key in ["json", "params"]:
                value = kwargs.get(key)
                if value is not None:
                    if issubclass(value.__class__, BaseDto):
                        kwargs[key] = value.to_dict()
                    elif isinstance(value, list):
                        kwargs[key] = [i.to_dict() if issubclass(i.__class__, BaseDto) else i for i in value]
                    elif isinstance(value, dict):
                        if key == "params":
                            base_dto_keys = [k for k, v in value.items() if issubclass(v.__class__, BaseDto)]
                            if len(base_dto_keys) > 0:
                                base_dto_dict = dict()
                                for k in base_dto_keys:
                                    dto_dict = value.pop(k).to_dict()
                                    if dto_dict.keys() & base_dto_dict:
                                        raise Exception("Duplicate keys found in BaseDto dictionaries")
                                    base_dto_dict.update(dto_dict)
                                if base_dto_dict.keys() & value:
                                    raise Exception("BaseDto keys overlap with non-BaseDto keys")
                                value.update(base_dto_dict)
                        else:
                            kwargs[key] = {k: v.to_dict() if issubclass(v.__class__, BaseDto) else v for k, v in
                                           value.items()}
            data = kwargs.get("data")
            if data is None and "multipart_encoder_kwargs" in kwargs:
                multipart_encoder_kwargs = kwargs.pop("multipart_encoder_kwargs")
                if multipart_encoder_kwargs is not None:
                    multipart_encoder_data = list()
                    for k, v in multipart_encoder_kwargs.items():
                        if issubclass(v.__class__, BaseDto):
                            multipart_encoder_data.extend(v.build_multipart_fields(values_as_str=True, has_none=False))
                        elif isinstance(v, list) and all(
                                isinstance(file, str) and os.path.exists(file) and os.path.isfile(file) for file in v):
                            multipart_encoder_data.extend([(k, build_file_dto(file)) for file in v])
                        elif isinstance(v, str) and os.path.exists(v) and os.path.isfile(v):
                            multipart_encoder_data.append((k, build_file_dto(v)))
                        else:
                            multipart_encoder_data.append((k, v))
                    if len(multipart_encoder_data) > 0:
                        data = MultipartEncoder(fields=multipart_encoder_data)
                kwargs.update(data=data)
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def refresh_headers():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            headers = copy.deepcopy(instance.headers)
            sh = SampleHeaders(headers)
            if instance.refresh_content_type is True:
                sh.add_content_type("application/json")
            data = kwargs.get("data")
            if isinstance(data, MultipartEncoder):
                sh.add_content_type(data.content_type)
            kwargs.update(headers=sh.to_h())
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def refresh_token():
    def __wrapper__(func):
        def __inner__(instance: BizBase, *args, **kwargs):
            instance.user.external is False and (
                    int(time.time() - instance.time_mills) < 60 * 30 - 300 or instance.login())
            return func(instance, *args, **kwargs)

        return __inner__

    return __wrapper__


def http_ok(func):
    @wraps(func)
    def _http_ok(instance: BizBase, *args, **kwargs):
        try:
            rsp: Response = kwargs.pop("rsp")
            kwargs.pop("headers")
            instance.last_kwargs = kwargs
            instance.last_result = rsp
            content_type = rsp.headers.get("content-type")
            if rsp.status_code not in [200, 201]:
                raise ApiResponseException(rsp)
            if not content_type:
                raise ApiResponseException(rsp, message="The content-type in the response header is empty.")
            if "application/json" in content_type:
                proc_code = rsp.json().get("procCode")
                if proc_code not in [200, 201]:
                    raise ApiResponseException(rsp)
                else:
                    return rsp.json().get("payload")
            elif any(item in content_type for item in ["application/octet-stream", "application/vnd.ms-excel"]):
                return rsp.content
            else:
                raise ApiResponseException(rsp, message="Please handle the {0} request.".format(content_type))
        except Exception as e:
            if instance.raises_exception is True:
                raise
            else:
                # Handle non-exception case here if necessary
                print(f"Exception caught but not re-raised: {e}")

    return _http_ok
