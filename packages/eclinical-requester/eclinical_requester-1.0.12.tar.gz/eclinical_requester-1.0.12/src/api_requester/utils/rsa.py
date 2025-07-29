#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: xiaodong.li
@time: 11/10/2020 3:19 PM
@desc:
"""
import base64
import time

from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto.PublicKey import RSA


def encrypt(string):
    public_key = "MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCTYnHdPs3A6JDZanoNumpZqoTam3B4yMiR" \
                 "blbaSmxGs8tW5AUEGfdevRZJn3zg/g0KETIptFXJ7oFbhYdmeo5Q8XEQnrXU1Q9GKyVZBpfJ" \
                 "ujGD7y3MaMYw29TwUdAuWDm0aWAqiwlqR2B9IWPkVBysIp2BypwfMrpe5IutObo3jQIDAQAB "
    public_key = "-----BEGIN PUBLIC KEY-----\n" + public_key + "\n-----END PUBLIC KEY-----"
    rsa_key = RSA.importKey(public_key)
    cipher = Cipher_pkcs1_v1_5.new(rsa_key)
    cipher_text = base64.b64encode(cipher.encrypt(string.encode()))
    return cipher_text.decode()


def encrypt_password(pwd):
    timestamp = int(time.time() * 1000)
    # timestamp = date_to_timestamp("2021-07-15")
    pwd_obj = dict(password=pwd, time=timestamp)
    return encrypt(repr(pwd_obj).replace("'", "\""))


def date_to_timestamp(date):
    frmt = "%Y-%m-%d"
    time_array = time.strptime(date, frmt)
    return int(time.mktime(time_array)) * 1000
