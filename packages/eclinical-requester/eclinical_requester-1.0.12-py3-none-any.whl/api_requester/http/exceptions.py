# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 8/5/2024 4:35 PM
@Description: Description
@File: exceptions.py
"""
from urllib.parse import urlparse

from requests import Response


class ApiResponseException(Exception):
    def __init__(self, response: Response, message=None, exception=None, request_payload=None):
        self.status_code = response.status_code
        self.api = urlparse(response.url).path
        self.method = response.request.method
        self.message = message
        self.exception = exception
        self.request_payload = request_payload
        self.proc_code = None
        content_type = response.headers.get("content-type")
        if not content_type:
            ...
        elif "application/json" in content_type:
            self.proc_code = response.json().get("procCode")
            self.message = response.json().get("message") or message
            self.exception = response.json().get("exception") or exception
        else:
            self.message = "\n".join([message, response.text])  if message else response.text

    def __str__(self):
        messages = [
            "\nRequest response exception:",
            "Status code: {0}".format(self.status_code),
            "URL: {0} {1}".format(self.method, self.api),
        ]
        if self.request_payload:
            if isinstance(self.request_payload, dict):
                payload = "\n".join(["{0}: {1}".format(k, v) for k, v in self.request_payload.items()])
            else:
                payload = str(self.request_payload)
            messages.append("Request payload: {0}".format(payload))
        if self.proc_code:
            messages.append("Proc code: {0}".format(self.proc_code))
        if self.message:
            messages.append("Message: {0}".format(self.message))
        if self.exception:
            messages.append("Exception: {0}".format(self.exception))
        return "\n".join(messages)


class ApiValidationError(ApiResponseException):
    """自定义异常类，用于验证接口失败时引发错误"""

    def __init__(self, response: Response, message=None, exception=None, request_payload=None):
        super().__init__(response, message, exception, request_payload)


class DatabaseValidationError(Exception):
    """自定义异常类，用于数据库验证失败时引发错误"""

    def __init__(self, message):
        super().__init__(message)


class FileValidationError(Exception):
    """自定义异常类，用于文件验证失败时引发错误"""

    def __init__(self, message):
        super().__init__(message)
