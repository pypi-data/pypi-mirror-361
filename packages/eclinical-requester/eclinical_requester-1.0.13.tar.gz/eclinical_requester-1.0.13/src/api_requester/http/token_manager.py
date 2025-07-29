# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 9/13/2024 5:45 PM
@Description: Description
@File: token_manager.py
"""
from api_requester.dto.biz_base import BizBase
from api_requester.http.sample_headers import SampleHeaders


def apply_token_to_headers(instance):
    """
     从实例的响应头中提取 token，并更新到实例的请求头中。

    :param instance: 继承自 BizBase 的实例，包含响应结果和请求头信息。
    :return: 无返回值。若存在 token，则更新实例的请求头。
    :return:
    """
    if not isinstance(instance, BizBase):
        return
    instance: BizBase
    if instance.last_result is None:
        return
    token = instance.last_result.headers.get("token")
    if token:
        headers = SampleHeaders()
        headers.add_authorization(token)
        instance.headers = headers.to_h()
