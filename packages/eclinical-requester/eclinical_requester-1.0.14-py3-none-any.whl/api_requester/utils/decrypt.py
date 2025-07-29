# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/22/2025 4:57 PM
@Description: Description
@File: decrypt.py
"""
import base64
import re

from Crypto.Cipher import AES


def decrypt(str_base64: str, is_no_padding: bool = False) -> str:
    key = b'1234567890123456'
    iv = b'1234567890123456'

    # Base64 解码
    ciphertext = base64.b64decode(str_base64)

    # 创建 AES 解密器
    mode = AES.MODE_CBC
    cipher = AES.new(key, mode, iv=iv)

    # 解密
    decrypted = cipher.decrypt(ciphertext)

    if not is_no_padding:
        # 去除 PKCS#7 padding
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]

    # 转成字符串（UTF-8 解码）
    decrypted_str = decrypted.decode('utf-8', errors='replace')

    # 替换不可见字符（与 JS 中 replace(/[\u0000-\u001F\u007F-\u009F]/g, ' ') 等效）
    cleaned_str = re.sub(r'[\x00-\x1F\x7F-\x9F]', ' ', decrypted_str)

    return cleaned_str
