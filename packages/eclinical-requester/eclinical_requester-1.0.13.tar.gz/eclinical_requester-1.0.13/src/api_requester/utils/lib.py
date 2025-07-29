# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/18/2024 4:59 PM
@Description: Description
@File: lib.py
"""
import os
from typing import Any, List, Dict, Optional

import numpy as np
from dateutil import parser

from api_requester.utils.json_utils import are_json_equal


def is_na_no(sth) -> bool:
    """
    NaN、None或者空字符串返回True，其他情况返回False
    """
    if sth == 0:
        return False
    if not sth:
        return True
    if isinstance(sth, float):
        if np.isnan(sth):
            return True
    return False


def check_file_path():
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            _path = func(*args, **kwargs)
            return (_path and os.path.exists(_path)) and _path or None

        return __inner__

    return __wrapper__


def param_is_digit(param):
    return (type(param) is str and param.isdigit()) or type(param) is int


def get_class_attr_values(obj: object):
    result = list()
    for var_name, var_value in vars(obj).items():
        if not var_name.startswith('__') and not callable(var_value):
            result.append(var_value)
    return result


def split_list(lst, n):
    """将一组数字拆分成n个组，形成一个列表"""
    quotient = len(lst) // n
    remainder = len(lst) % n
    result = []
    start = 0
    for i in range(n):
        if i < remainder:
            end = start + quotient + 1
        else:
            end = start + quotient
        result.append(lst[start:end])
        start = end
    return result


def _get_val_from_list(items: list, k1, v1, k2, compare_json=False):
    """
    Traverse each item in the list, and obtain the value of k2 through
    the actual value of k1 and the expected value v1.
    :param items: List of dictionaries to search within.
    :param k1: The key to look up in each dictionary.
    :param v1: The value to match with the dictionary's value for the given key.
    :param k2: The key whose value should be returned if a match is found.
    :return: The value associated with k2 if a match is found, otherwise None.
    """
    if items and isinstance(items, list):
        for item in items:
            item_value = item.get(k1)
            if compare_json:
                if are_json_equal(v1, item_value):
                    return item.get(k2)
            if item_value == v1:
                return item.get(k2)
    return None


def get_key_from_dict(items: dict, k, v):
    if items and isinstance(items, dict):
        for key, value in items.items():
            if value.get(k) == v:
                return key
    return None


def _get_val_from_dict(items: dict, k1, k2):
    """
    Traverse each item in the dictionary and find the value of k2 in the value of k1.
    @param items:
    @param k1: A key in items.
    @param k2:
    @return: None, val
    """
    if items and isinstance(items, dict):
        for key, value in items.items():
            if key == k1:
                return value.get(k2)
    return None


def _find_and_validate_single_item(items, k1, v1, compare_json=False, validate=True):
    """
    Traverse each item in the list, and return the item through the actual value of k1 and the expected value v1.
    :param items: List of dictionaries to search within.
    :param k1: The key to look up in each dictionary.
    :param v1: The value to match with the dictionary's value for the given key.
    :param compare_json: If True, compare the value to the JSON representation of the item. Default is False.
    :param validate: If True, validates that exactly one item matches the criteria.
                     If False, returns all matched items without validation.
    :return: A single matching item if validate is True and exactly one match is found;
             otherwise, returns the list of matched items or None if no match is found.
    :raises ValueError: If validate is True and multiple items match the criteria.
    """
    matched_items = list()
    if items and isinstance(items, list):
        for item in items:
            item_value = item.get(k1)
            if compare_json:
                if are_json_equal(v1, item_value):
                    matched_items.append(item)
                    continue
            if v1 == item_value:
                matched_items.append(item)
    if not validate:
        return matched_items
    if len(matched_items) == 1:
        return matched_items[0]
    elif len(matched_items) == 0:
        return None
    else:
        raise ValueError("Multiple items match the criteria.")


def _get_first_item_from_list(items, k1=None, v1=None, sort_by=None):
    """
    @param items:
    @param k1:
    @param v1:
    @return: None, item
    """
    if items and isinstance(items, list):
        if sort_by is not None:
            items = sorted(items, key=lambda x: format_value(x[sort_by]), reverse=True)
        for item in items:
            if v1 is None or k1 is None:
                return item
            if v1 == item.get(k1):
                return item
    return None


def _get_last_item_from_list(items, k1=None, v1=None, sort_by=None):
    if items and isinstance(items, list):
        # 先排序，如果提供了排序键
        if sort_by is not None:
            items = sorted(items, key=lambda x: format_value(x.get(sort_by)),
                           reverse=True if sort_by.startswith('-') else False)

        # 遍历列表，找到最后一个符合条件的项
        last_item = None
        for item in items:
            if v1 is None or k1 is None or v1 == item.get(k1):
                last_item = item
        return last_item
    return None


def is_included(items, k, v):
    """
    Traverse each item in the list to determine whether the value of k is consistent with the actual value v.
    @param items:
    @param v:
    @param k:
    @return: True or False.
    """
    if items and isinstance(items, list):
        for i in items:
            if i.get(k, None) == v:
                return True
    return False


def apply_is_included(key="name"):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            items = func(*args, **kwargs)
            return is_included(items, key, kwargs.get("name"))

        return __inner__

    return __wrapper__


def get_val_from_list(k1="name", k2="id", v1=None, compare_json=False):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            v = kwargs.get("name") if v1 is None else v1
            return _get_val_from_list(res, k1, v, k2, compare_json)

        return __inner__

    return __wrapper__


def get_item_from_list(k1="name", compare_json=False):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            return _find_and_validate_single_item(res, k1, kwargs.get("name"), compare_json)

        return __inner__

    return __wrapper__


def get_first_item_from_list(k1=None, sort_by=None):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            return _get_first_item_from_list(res, k1, kwargs.get("name"), sort_by)

        return __inner__

    return __wrapper__


def get_first_val_from_list(extract_key, k1=None, sort_by=None):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            item = _get_first_item_from_list(res, k1, kwargs.get("name"), sort_by)
            return item.get(extract_key)

        return __inner__

    return __wrapper__


def get_last_val_from_list(extract_key, k1=None, sort_by=None):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            item = _get_last_item_from_list(res, k1, kwargs.get("name"), sort_by)
            return item.get(extract_key)

        return __inner__

    return __wrapper__


def get_val_from_dict(k2):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            res = func(*args, **kwargs)
            return _get_val_from_dict(res, kwargs.get("key"), k2)

        return __inner__

    return __wrapper__


def get_value_from_nested_dict_by_list(data, path):
    """
    从嵌套的字典中按路径获取值

    参数:
    data (dict):
    path (list): 包含键的列表，表示路径

    返回:
    获取到的值，如果路径无效则返回 None
    """
    if not path:
        return data
    if not data:
        return data
    key = path[0]
    if key in data:
        return get_value_from_nested_dict_by_list(data[key], path[1:])
    else:
        return None


def get_value_from_nested_dict(data, path):
    path_list = path.split(".")
    return get_value_from_nested_dict_by_list(data, path_list)


def mkdirs(func):
    def __wrapper__(*args, **kwargs):
        dir_path = func(*args, **kwargs)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
        return dir_path

    return __wrapper__


def truncate_string(s, max_length):
    if type(s) is str and type(max_length) is int:
        return s[:max_length if max_length < len(s) else len(s)]
    return s


def handle_construction(construction_func, error_message):
    """
    处理 YAML 标签构建的异常。
    """
    try:
        return construction_func()
    except Exception as e:
        print("{0}: {1}".format(error_message, e))
        return str()


def is_datetime_string(date_str):
    try:
        parser.parse(date_str)
        return True
    except (ValueError, TypeError):
        return False


def format_value(value):
    if value is None:
        raise Exception("None value exists.")
    if isinstance(value, int):
        return value
    elif isinstance(value, str):
        if is_datetime_string(value):
            return parser.parse(value)
        else:
            return value


def retrieve_item_by_key_value(items, key, value, compare_json=False, validate=True):
    """
    Retrieve a single item from a list of dictionaries based on a key-value match.

    :param items: List of dictionaries to search within.
    :param key: The key to look up in each dictionary.
    :param value: The value to match with the dictionary's value for the given key.
    :param compare_json: If True, compare the value to the JSON representation of the item. Default is False.
    :param validate: If True, validates that exactly one item matches the criteria.
                     If False, returns all matched items without validation.
    :return: The matching item or None if no match is found. Raises an exception if multiple matches are found.
    :raises ValueError: If multiple items match the criteria.
    """
    return _find_and_validate_single_item(items, key, value, compare_json, validate)


def are_none_or_empty(*values: Any) -> bool:
    """
    检查多个值是否都为 None 或空字符串。

    :param values: 需要检查的值。
    :return: 如果所有值都是 None 或空字符串，返回 True；否则返回 False。
    """
    processed_values = []
    for value in values:
        if isinstance(value, str):
            processed_values.append(value.strip())
        elif value is None:
            processed_values.append(value)
        else:
            return False
    return all(value in (None, "") for value in processed_values)


def first_unassociated_perms(trees, key):
    """
    遍历树，返回第一分支为key=false的从根节点到子节点id的列表，并保留所有key=true的数据。

    :param trees: 树列表
    :param key: 属性名称
    :return: 包含ID的列表
    """
    flag = "__false_value_flag__"

    def traverse(node, paths, results):
        if paths is None:
            paths = []
        if node.get("id") is not None:
            paths.append(node["id"])
        for child in node.get("children", []):
            traverse(child, paths.copy(), results)
        else:
            if node.get(key, True):
                results.extend(paths)
            elif flag in results:
                results.extend(paths)
                results.remove(flag)

    all_results = [flag]
    for tree in trees:
        traverse(tree, [], all_results)
    return list(set(all_results))


def apply_first_unassociated_perms(key):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            trees = func(*args, **kwargs)
            return first_unassociated_perms(trees, key)

        return __inner__

    return __wrapper__


def extract_values(records: List[Dict], key: Optional[str] = None, first_value: bool = False) -> List[Any]:
    """
    从字典列表中提取每个字典的指定键的值，或者根据参数返回第一个值。

    该方法假设列表中的每个字典都包含至少一个键值对。
    如果 `first_value` 为 True，则返回每个字典的第一个值；
    如果提供了 `key`，则返回每个字典中对应键的值；
    如果既未提供 `key` 也未设置 `first_value` 为 True，则返回空列表。
    
    :param records: 一个字典列表，每个字典至少包含一个键值对。
    :param key: （可选）指定键来提取对应的值。如果未提供且 `first_value` 为 False，则返回空列表。
    :param first_value: （可选）是否返回每个字典的第一个值。如果为 True，将忽略 `key` 参数。
    :return: 包含提取值的列表。
    """
    if first_value:
        return [next(iter(record.values())) for record in records]
    elif key:
        return [record.get(key) for record in records]
    else:
        return []


def apply_extract_values(key=None, first_value=False):
    def __wrapper__(func):
        def __inner__(*args, **kwargs):
            records = func(*args, **kwargs)
            return extract_values(records, key, first_value)

        return __inner__

    return __wrapper__
