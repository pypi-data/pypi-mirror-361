# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/24/2023 3:48 PM
@Description: Description
@File: sample_headers.py
"""


class SampleHeaders(object):
    def __init__(self, headers=None):
        self.headers = {"Content-Type": "application/json", "Connection": "close"} if headers is None else headers

    def add_header(self, **kwargs):
        self.headers.update(kwargs)
        return self

    def to_h(self):
        return self.headers

    def add_authorization(self, token):
        return self.add_header(Authorization=token)

    def add_content_type(self, content_type):
        return self.add_header(**{"Content-Type": content_type})
