# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 7/24/2023 3:48 PM
@Description: Description
@File: authorize.py
"""
import time

from loguru import logger

from api_requester.core.admin.dto.cross_user_user_on_board_dto import CrossUserUserOnBoardDto
from api_requester.core.admin.dto.jwt_authentication_request import JwtAuthenticationRequest
from api_requester.core.admin.dto.user_on_board_dto import UserOnBoardDto
from api_requester.core.admin.service.auth_service import AdminAuthService
from api_requester.core.admin.service.impl.system_env_service_impl import CommonSystemEnvServiceImpl
from api_requester.core.admin.service.impl.user_on_board_application_service_impl import \
    AdminUserOnBoardApplicationServiceImpl
from api_requester.dto.biz_base import BizBase
from api_requester.dto.user import EClinicalUser
from api_requester.http.sample_headers import SampleHeaders
from api_requester.utils.constant import AppEnum, UserType
from api_requester.utils.rsa import encrypt_password


class Authorize(BizBase, AdminAuthService, AdminUserOnBoardApplicationServiceImpl, CommonSystemEnvServiceImpl):

    def __init__(self, user: EClinicalUser):
        BizBase.__init__(self)
        self.user = user
        self.login_app = self.user.app
        self.user.app = AppEnum.ADMIN.code
        self.time_mills = time.time()
        self.user_onboard_dto = UserOnBoardDto(-1)
        AdminAuthService.__init__(self)
        AdminUserOnBoardApplicationServiceImpl.__init__(self)
        CommonSystemEnvServiceImpl.__init__(self)

    def login(self):
        if self.login_app == AppEnum.CODING.code:
            login_app_tip = "{0}({1})".format(self.login_app,
                                              self.user.company_level_login is True and "admin" or "study")
        else:
            login_app_tip = self.login_app
        try:
            user_type = self._auth()
            if user_type == UserType.account.type_name:
                return
            company_id = None
            if self.user.company:
                company_id = self.set_work_for_company_id()
            if self.login_app != AppEnum.ADMIN.code:
                self._user_onboard(company_id)
                self.user.app = self.login_app
                self._app_auth()
                if self.user.role is not None:
                    self.switch_role(self.user.role)
            else:
                self._entry_portal(company_id)
            logger.info("The user({0}) logs in to {1} successfully.".format(self.user, login_app_tip))
        except Exception as e:
            tip = "The user({0}) failed to log in to {1}.".format(self.user, login_app_tip)
            logger.error(tip)
            raise Exception(f"{tip} Authorize Failed: {e}")

    def _auth(self):
        self.time_mills = time.time()
        encrypt_pwd = encrypt_password(self.user.password)
        jwt_authentication_request_dto = JwtAuthenticationRequest(self.user.username, encrypt_pwd)
        response = self.create_authentication_token(jwt_authentication_request_dto)
        if response is None:
            raise Exception(f"LoginParams failed: {response}")
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()
        return response.get("type")

    def _user_onboard(self, company_id):
        user_onboard_dto = UserOnBoardDto(-1)
        user_onboard_dto.workForCompanyId = company_id
        self._build_user_onboard_dto(user_onboard_dto)
        self.user_onboard_dto = user_onboard_dto
        response = self.on_board(user_onboard_dto)
        token = response.get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()

    def _build_user_onboard_dto(self, dto: UserOnBoardDto):
        onboard_system_list = self.get_user_onboard_application_list(dto.workForCompanyId)
        if not onboard_system_list:
            raise Exception("Failed to obtain onboardSystemList info.")
        for onboard_system in onboard_system_list:
            if onboard_system.get("systemName").lower() == self.login_app:
                dto.applicationId = onboard_system.get("systemId")
                self._handle_onboard_envs(onboard_system, dto)
                if self.user.company_level_login is True:
                    dto.companyLevelLogin = True
                    continue
                onboard_sponsor_list = onboard_system.get("onboardSponsorList")
                if not onboard_sponsor_list:
                    continue
                for onboard_sponsor in onboard_sponsor_list:
                    if onboard_sponsor.get("name") == self.user.sponsor:
                        dto.sponsorId = onboard_sponsor.get("sponsorId")
                        self._handle_onboard_envs(onboard_sponsor, dto)
                        onboard_study_list = onboard_sponsor.get("onboardStudyList")
                        if not onboard_study_list:
                            continue
                        for onboard_study in onboard_study_list:
                            if onboard_study.get("studyName") == self.user.study:
                                dto.studyId = onboard_study.get("studyId")
                                self._handle_onboard_envs(onboard_study, dto)
        self._assert(self.login_app, dto.applicationId, "app")
        if self.login_app in [AppEnum.EDC.code, AppEnum.DESIGN.code, AppEnum.IWRS.code, AppEnum.CODING.code]:
            if dto.companyLevelLogin is False:
                self._assert(self.user.study, dto.studyId, "study")
            else:
                self._assert(self.user.company, dto.workForCompanyId, "company")
        elif self.login_app != AppEnum.ADMIN.code:
            self._assert(self.user.sponsor, dto.sponsorId, "sponsor")
        self._assert(self.user.app_env, dto.envId, "app env")

    @staticmethod
    def _assert(attr, att_id, k):
        assert (not attr) or (False if att_id is None else True), f"Failed to obtain {k} id. {k}::{attr}."

    def _handle_onboard_envs(self, onboard_infos, dto: UserOnBoardDto):
        onboard_envs = onboard_infos.get("onboardEnvs") or list()
        for onboardEnv in onboard_envs:
            if onboardEnv.get("name") == self.user.app_env:
                dto.envId = onboardEnv.get("id")

    def set_work_for_company_id(self):
        company_id = self.get_company_id(name=self.user.company)
        if self.user.company and not company_id:
            raise Exception("The company {0} was not found.".format(self.user.company))
        return company_id

    def _app_auth(self):
        response = self.create_authentication_token()
        if response.get("jwtAuthenticationResponse") is None:
            token = response.get("token")
        else:
            token = response.get("jwtAuthenticationResponse").get("token")
        self.headers = SampleHeaders().add_authorization(token).to_h()
        self.time_mills = time.time()

    def _entry_portal(self, company_id):
        response = self.login_portal(CrossUserUserOnBoardDto(companyId=company_id))
        try:
            token = response.get("token")
            self.headers = SampleHeaders().add_authorization(token).to_h()
        except BaseException as e:
            print(e)
