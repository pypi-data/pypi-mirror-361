# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 12/30/2024 3:55 PM
@Description: Description
@File: placeholder_replacer.py
"""
import re


class PlaceholderReplacer:
    def __init__(self, replacements=None):
        self.replacements = replacements or dict()

    def add_replacement(self, placeholder, value):
        self.replacements[placeholder] = value

    def replace(self, text):
        for placeholder, value in self.replacements.items():
            text = re.sub(rf"\{{\s*{re.escape(placeholder)}\s*\}}", str(value), text)
        return text
