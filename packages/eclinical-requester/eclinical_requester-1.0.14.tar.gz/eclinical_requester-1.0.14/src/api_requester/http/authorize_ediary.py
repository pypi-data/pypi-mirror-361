# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 5/15/2024 2:30 PM
@Description: Description
@File: authorize_ecoa.py
"""
import time

from loguru import logger

from api_requester.core.admin.dto.subject_jwt_authentication_request import SubjectJwtAuthenticationRequest
from api_requester.core.admin.dto.user_on_board_dto import UserOnBoardDto
from api_requester.core.admin.service.subject_auth_service import AdminSubjectAuthService
from api_requester.core.common.service.subject_auth_service import CommonSubjectAuthService
from api_requester.dto.biz_base import BizBase
from api_requester.dto.user import EClinicalUser
from api_requester.http.sample_headers import SampleHeaders
from api_requester.utils.constant import AppEnum
from api_requester.utils.rsa import encrypt_password


class AuthorizeEdiary(BizBase, AdminSubjectAuthService, CommonSubjectAuthService):

    def __init__(self, user: EClinicalUser):
        BizBase.__init__(self, user)
        self.login_app = self.user.app
        self.user.app = AppEnum.ADMIN.code
        self.time_mills = time.time()
        self.user_onboard_dto = UserOnBoardDto(-1)
        AdminSubjectAuthService.__init__(self)
        CommonSubjectAuthService.__init__(self)

    def login(self):
        try:
            self._auth()
            self.user.app = self.login_app
            self._app_auth()
            logger.info("{0} logs in to {1} eDiary successfully.".format(self.user, self.login_app))
        except Exception as e:
            logger.error("{0} failed to log in to {1} eDiary.".format(self.user, self.login_app))
            raise Exception(f"Authorize Failed: {e}")

    def _auth(self):
        self.time_mills = time.time()
        encrypt_pwd = encrypt_password(self.user.password)
        jwt_authentication_request_dto = SubjectJwtAuthenticationRequest(
            self.user.username, encrypt_pwd, organizationCode=self.user.org_code or None)
        response = self.auth_subject_login(jwt_authentication_request_dto)
        if response is None:
            raise Exception(f"LoginParams failed: {response}")
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()
        return response

    def _app_auth(self):
        response = self.subject_auth_login()
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()

    def admin_auth(self):
        return self._auth()
