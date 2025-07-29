# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/23/2020 2:32 PM
@Description: Description
@File: path.py
"""
import os


def root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))


def project_path():
    return os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def docs_path():
    return os.path.join(project_path(), "docs")
