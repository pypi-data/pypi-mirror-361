# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/18/2024 4:59 PM
@Description: Description
@File: read_file.py
"""
import json
import os

import yaml
from loguru import logger
from lxml import etree


class JSONConnector:
    def __init__(self, filepath):
        self.data = dict()
        with open(filepath, mode='r', encoding='utf-8') as f:
            self.data = json.load(f)

    @property
    def parsed_data(self):
        return self.data


class XMLConnector:
    def __init__(self, filepath):
        self.root = etree.parse(filepath).getroot()

    @property
    def parsed_root(self):
        return self.root


class MyYamlLoader(yaml.FullLoader):

    def __init__(self, stream, filepath=None):
        self.filepath = filepath and filepath or None
        super(MyYamlLoader, self).__init__(stream)


class YAMLConnector:
    def __init__(self, filepath):
        self.data = None
        with open(filepath, mode='r', encoding='utf-8') as f:
            self.data = yaml.load(f.read(), Loader=lambda s: MyYamlLoader(s, filepath))

    @property
    def parsed_data(self):
        return self.data


class SQLConnector:
    def __init__(self, filepath):
        self.data = dict()
        with open(filepath, mode='r', encoding='utf-8') as f:
            self.data = f.read()

    @property
    def parsed_data(self):
        return self.data


def connection_factory(filepath):
    if filepath.endswith('json'):
        connector = JSONConnector
    elif filepath.endswith('xml'):
        connector = XMLConnector
    elif filepath.endswith('yaml'):
        connector = YAMLConnector
    elif filepath.endswith('sql'):
        connector = SQLConnector
    else:
        raise ValueError(f'Cannot connect to {filepath}.')
    return connector(filepath)


def connect_to(filepath, ignore_error=False):
    if not os.path.exists(filepath):
        if ignore_error is False:
            raise Exception("No such file.")
        else:
            return None
    try:
        return connection_factory(filepath)
    except ValueError as ve:
        logger.error(ve)
        if ignore_error is False:
            raise Exception(ve)
        else:
            return None
