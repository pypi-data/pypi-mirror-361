# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 1/8/2025 3:04 PM
@Description: Description
@File: setup.py
"""

import setuptools
from setuptools import find_packages

from src.api_requester import __version__

version = __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="eclinical_requester",
    version=version,
    author="xiaodong.li",
    author_email="",
    description="edetek api requester",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://example.com",
    install_requires=[
        'lxml>=4.8.0',
        'requests>=2.28.2',
        'PyYAML>=6.0',
        'requests-toolbelt>=0.10.1',
        'python-dateutil>=2.9.0.post0',
        'numpy>=1.23.4',
        'pycryptodome>=3.17',
    ],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3.9",
    ],
    include_package_data=True,
    package_data={
        'api_requester.docs': ['*.yaml'],  # 列出所有需要包含的文档类型
    }
)
