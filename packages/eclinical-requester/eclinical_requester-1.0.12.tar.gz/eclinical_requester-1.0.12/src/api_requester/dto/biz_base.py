# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 6/12/2024 2:20 PM
@Description: Description
@File: biz_base.py
"""
import time
from abc import abstractmethod, ABC
from typing import Optional

from requests import Response

from api_requester.dto.user import EClinicalUser


class BizBase(ABC):

    def __init__(self, user=None, headers=None, last_result=None, refresh_content_type=True):
        self.user: Optional[EClinicalUser] = user
        self.headers: dict = headers or dict()
        self.last_kwargs: dict = dict()
        self.last_result: Optional[Response] = last_result
        self.time_mills = time.time()
        self.refresh_content_type: bool = refresh_content_type
        self.raises_exception: bool = True
        self.allure_attach: bool = False

    @abstractmethod
    def login(self): ...
