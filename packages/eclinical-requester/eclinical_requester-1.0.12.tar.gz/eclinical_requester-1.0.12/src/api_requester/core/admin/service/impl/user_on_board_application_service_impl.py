# !/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@Author: xiaodong.li
@Time: 2024/03/19 13:55
@Description: Description
@File: user_on_board_application_service_impl.py
"""
from api_requester.core.admin.service.user_on_board_application_service import AdminUserOnBoardApplicationService
from api_requester.utils.lib import get_val_from_list


class AdminUserOnBoardApplicationServiceImpl(AdminUserOnBoardApplicationService):
    """
    AdminUserOnBoardApplicationServiceImpl
    """

    def __init__(self):
        AdminUserOnBoardApplicationService.__init__(self)

    @get_val_from_list()
    def get_company_id(self, name=None):
        return self.get_company_list()
