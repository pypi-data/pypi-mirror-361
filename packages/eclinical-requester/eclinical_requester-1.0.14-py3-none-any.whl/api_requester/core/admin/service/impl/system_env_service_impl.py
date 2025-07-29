# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 4/29/2024 2:41 PM
@Description: Description
@File: system_env_service_impl.py
"""
from loguru import logger

from api_requester.core.common.service.system_env_service import CommonSystemEnvService
from api_requester.http.token_manager import apply_token_to_headers


class CommonSystemEnvServiceImpl(CommonSystemEnvService):
    """
    CommonSystemEnvServiceImpl
    """

    def __init__(self):
        CommonSystemEnvService.__init__(self)

    def switch_role(self, role, env=None):
        payload = self.get_current_system_env()
        if payload.get("role").get("code") == role or (env is not None and payload.get("env").get("name") == env):
            return
        items = self.sponsor_env_list()
        if not items:
            return
        for item in items:
            if item.get("defaultEnv"):
                pass
            if env is None and item.get("defaultEnv") or item.get("name") == env:
                onboard_role_list = item.get("onboardRoleList")
                onboard_role = next((role_dto for role_dto in onboard_role_list if role_dto.get("name") == role), None)
                if onboard_role:
                    self.switch_env(env_id=item.get("id"), role_id=onboard_role.get("id"))
                    apply_token_to_headers(self)
                    logger.info(f"The user switches the {role} role successfully.")
                    return
