# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/24/2023 3:56 PM
@Description: Description
@File: base_dto.py
"""
import mimetypes
import os
from dataclasses import dataclass, fields, Field
from typing import Dict, Any, TypeVar, Type, List, get_origin

T = TypeVar('T', bound='BaseDto')


@dataclass
class BaseDto:

    def __getattr__(self, name):
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, key, value):
        if key not in [field.name for field in fields(self)]:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")
        super().__setattr__(key, value)

    def data(self, has_none_value=True):
        tmp = dict()
        for k, v in self.__dict__.items():
            if v is None and has_none_value is False:
                continue
            tmp.update({k: v})
        return tmp

    def to_dict(self) -> Dict[str, Any]:
        data = dict()
        for f in fields(self):
            key = f.metadata.get('alias', f.name)
            value = getattr(self, f.name)
            multipart_file = f.metadata.get('multipart_file', False)
            if multipart_file:
                value = process_multipart_file(value)
            elif isinstance(value, BaseDto):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [item.to_dict() if isinstance(item, BaseDto) else item for item in value]
            elif isinstance(value, set):  # 20241104在Python的requests库中，传递JSON数据时，set类型并不是JSON可序列化的格式，
                # 因此需要将 set 转换为其他类型（如 list）才能正确发送
                value = list(value)
            if not f.metadata.get('ignore', False):
                data[key] = value
        return data

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        kwargs = dict()
        for f in fields(cls):
            key = f.metadata.get("alias", f.name)
            if key in data:
                kwargs[f.name] = convert_value(f, data[key])
        return cls(**kwargs)

    def build_multipart_fields(self, values_as_str=False, has_none=True) -> List[tuple[str, Any]]:
        data = list()
        for f in fields(self):
            key = f.metadata.get('alias', f.name)
            value = getattr(self, f.name)
            multipart_file = f.metadata.get('multipart_file', False)
            if multipart_file:
                value = process_multipart_file(value)
            if isinstance(value, BaseDto):
                value = value.to_dict()
            elif isinstance(value, list):
                value = [item.to_dict() if isinstance(item, BaseDto) else item for item in value]
            if not f.metadata.get('ignore', False):
                # if multipart_file and isinstance(value, list):
                #     data.extend((key, i) for i in value)
                # elif isinstance(value, list):
                #     for i in value:
                #         if isinstance(i, BaseDto):
                #             data.append((key, i.to_dict()))
                #         elif values_as_str and i is not None:
                #             data.append((key, str(i)))
                #         else:
                #             data.append((key, i))
                # else:
                #     if not has_none and value is None:
                #         continue
                #     data.append((key, str(value) if values_as_str and value is not None else value))
                if value and isinstance(value, (list, dict)):
                    if isinstance(value, list) and all(isinstance(i, (str, int)) for i in value):
                        data.extend([(key, str(i)) if values_as_str else (key, i) for i in value])
                    else:
                        data.extend(tuple(
                            flatten_data(value, parent_key=key, has_none=has_none,
                                         values_as_str=values_as_str).items()))
                else:
                    if not has_none and (value is None or (isinstance(value, (list, dict)) and not value)):
                        continue
                    data.append((key, str(value) if values_as_str and value is not None else value))
        return data

    @classmethod
    def has_multipart_file_field(cls) -> bool:
        for f in fields(cls):
            if f.metadata.get("multipart_file", False):
                return True
        return False


def convert_value(field: Field, value: Any) -> Any:
    origin = get_origin(field.type)
    if origin is not None:
        return value
    if isinstance(value, field.type):
        return value
    elif isinstance(value, (dict, int)) and field.type is str:
        return str(value)
    elif isinstance(value, str) and field.type is int:
        if value.isdigit():
            return int(value)
        else:
            return value
    else:
        return value


def build_file_dto(file_path):
    return os.path.basename(file_path), open(file_path, 'rb'), next(iter(mimetypes.guess_type(file_path)))


def process_multipart_file(value):
    """处理 multipart_file 类型的值"""
    if isinstance(value, str):
        if os.path.exists(value) and os.path.isfile(value):
            return build_file_dto(value)
        else:
            raise ValueError(f"无效的文件路径: {value}")
    elif isinstance(value, list):
        if all(isinstance(i, str) and os.path.exists(i) and os.path.isfile(i) for i in value):
            return [build_file_dto(i) for i in value]
        else:
            raise ValueError(f"列表中包含无效的文件路径: {value}")
    return value


def flatten_data(data, parent_key='', sep='.', values_as_str=False, has_none=True):
    items = []
    if isinstance(data, dict):
        for k, v in data.items():
            if not has_none and v is None:
                continue
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_data(v, new_key, sep=sep, values_as_str=values_as_str, has_none=has_none).items())
    elif isinstance(data, list):
        for idx, v in enumerate(data):
            if not has_none and v is None:
                continue
            new_key = f"{parent_key}[{idx}]"
            items.extend(flatten_data(v, new_key, sep=sep, values_as_str=values_as_str, has_none=has_none).items())
    else:
        if not has_none and data is None:
            return dict()
        items.append(
            (parent_key, str(data) if values_as_str and data is not None and not isinstance(data, tuple) else data))
    return dict(items)
