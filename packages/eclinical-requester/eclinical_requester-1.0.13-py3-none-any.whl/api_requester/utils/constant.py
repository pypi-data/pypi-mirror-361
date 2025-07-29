# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 3/18/2024 4:59 PM
@Description: Description
@File: constant.py
"""
from enum import Enum, unique, auto


@unique
class AppEnum(Enum):

    def __init__(self, system_id, code, description):
        self.id = system_id
        self.code = code
        self.description = description

    ADMIN = (1, "admin", "ADMIN")
    CTMS = (2, "ctms", "CTMS")
    ETMF = (3, "etmf", "eTMF")
    DESIGN = (4, "design", "DESIGN")
    EDC = (5, "edc", "EDC")
    IWRS = (6, "iwrs", "IWRS")
    E_CONSENT = (7, "econsent", "eConsent")
    PV = (8, "pv", "PV")
    CODING = (10, "coding", "CODING")
    IMAGING = (11, "imaging", "Eclinical IMAGING System")
    CMD = (12, "cmd", "Eclinical CMD System")
    IRC = (13, "irc", "Eclinical IRC System")


class UserType(Enum):

    def __init__(self, code, type_name):
        self.code = code
        self.type_name = type_name

    user = (1, "User")
    account = (2, "Account")


@unique
class AppEnvEnum(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    DEV = ("dev", "DEV")
    UAT = ("uat", "UAT")
    PROD = ("prod", "PROD")


@unique
class BizSqlType(Enum):

    def __init__(self, code, description):
        self.code = code
        self.description = description

    INITIAL = (1, "initial")
    INCREMENTAL = (2, "incremental")


class TestEnvType(str):
    local = "local"
    us_dev = "us.dev"
    us_demo = "us.demo"


@unique
class TestEnv(Enum):

    def __init__(self, code, ttype):
        self.code = code
        self.ttype = ttype

    us_dev = ("us.dev", TestEnvType.us_dev)
    us_demo = ("us.demo", TestEnvType.us_demo)
    dev03 = ("dev03", TestEnvType.local)
    dev04 = ("dev04", TestEnvType.local)
    dev01 = ("dev01", TestEnvType.local)
    dev02 = ("dev02", TestEnvType.local)
    test01 = ("test01", TestEnvType.local)

    @classmethod
    def from_code(cls, code):
        for member in cls:
            if member.code == code:
                return member
        return None

    def __str__(self):
        return self.code


@unique
class RoleEnum(Enum):

    def __init__(self, code, ttype=None):
        self.code = code
        self.ttype = ttype

    DM = ("DM",)
    CRC = ("CRC",)
    CRA = ("CRA",)


@unique
class EdcAppType(Enum):
    EDIARY = auto()
    ECOA = auto()
