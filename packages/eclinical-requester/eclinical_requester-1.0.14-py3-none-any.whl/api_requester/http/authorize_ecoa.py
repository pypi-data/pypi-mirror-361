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

from api_requester.core.admin.dto.ecoa_onboard_request_dto import EcoaOnboardRequestDto
from api_requester.core.admin.dto.jwt_authentication_request import JwtAuthenticationRequest
from api_requester.core.admin.dto.user_on_board_dto import UserOnBoardDto
from api_requester.core.admin.service.ecoa_auth_service import AdminEcoaAuthService
from api_requester.core.common.service.ecoa_auth_service import CommonEcoaAuthService
from api_requester.dto.biz_base import BizBase
from api_requester.dto.user import EClinicalUser
from api_requester.http.sample_headers import SampleHeaders
from api_requester.utils.constant import AppEnum
from api_requester.utils.rsa import encrypt_password


class AuthorizeEcoa(BizBase, AdminEcoaAuthService, CommonEcoaAuthService):

    def __init__(self, user: EClinicalUser):
        BizBase.__init__(self, user)
        self.login_app = self.user.app
        self.user.app = AppEnum.ADMIN.code
        self.time_mills = time.time()
        self.user_onboard_dto = UserOnBoardDto(-1)
        AdminEcoaAuthService.__init__(self)
        CommonEcoaAuthService.__init__(self)

    def login(self):
        try:
            self._auth()
            self._onboard()
            self.user.app = self.login_app
            self._app_auth()
            logger.info("{0} logs in to {1} eCOA successfully.".format(self.user, self.login_app))
        except Exception as e:
            logger.error("{0} failed to log in to {1} eCOA.".format(self.user, self.login_app))
            raise Exception(f"Authorize Failed: {e}")

    def _auth(self):
        self.time_mills = time.time()
        encrypt_pwd = encrypt_password(self.user.password)
        jwt_authentication_request_dto = JwtAuthenticationRequest(self.user.username, encrypt_pwd)
        response = self.auth_ecoa_login(jwt_authentication_request_dto)
        if response is None:
            raise Exception(f"LoginParams failed: {response}")
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()
        return response

    def _onboard(self):
        payload = self.ecoa_study_list()
        dto = EcoaOnboardRequestDto()
        for sponsor_dto in payload:
            dto.sponsorId = sponsor_dto["sponsorId"]
            dto.envId = sponsor_dto["envId"]
            self.user.sponsor = sponsor_dto["sponsorName"]
            self.user.app_env = sponsor_dto["envName"]
            for study_dto in sponsor_dto["ecoaStudyList"]:
                if sponsor_dto["envId"] == study_dto["envId"]:
                    dto.studyId = study_dto["studyId"]
                    self.user.study = study_dto["studyName"]
                break
            break
        self.user_onboard_dto.studyId = dto.studyId
        self.user_onboard_dto.sponsorId = dto.sponsorId
        self.user_onboard_dto.envId = dto.envId
        response = self.onboard(dto)
        token = response.get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()

    def _app_auth(self):
        response = self.create_authentication_token()
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()

    def admin_auth(self):
        return self._auth()
