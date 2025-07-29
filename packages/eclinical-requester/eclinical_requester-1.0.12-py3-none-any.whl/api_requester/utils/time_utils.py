# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/18/2024 4:59 PM
@Description: Description
@File: time_utils.py
"""

import datetime
import time


def now(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def now_yyyy_mm_dd(timestamp):
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))


def now_utc(timestamp):
    return datetime.datetime.utcfromtimestamp(timestamp)


def now_for_file(timestamp):
    return time.strftime("%Y-%m-%d %H-%M-%S", time.localtime(timestamp))
