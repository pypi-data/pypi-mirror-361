# !/usr/bin/env python
# -*-coding:utf-8 -*-
from __future__ import annotations

import httpx

from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.user import *

_BASE = "/api/v1/search-users"


class UserService:

    def __init__(self, http: httpx.Client):
        self._user = _User(http)

    # 直接把常用方法抛到一级，调用体验简单
    def search_one(self, payload: UserSearchReq) -> int:
        return self.user.search(payload)

    # 如果想要访问子对象，也保留属性
    @property
    def user(self) -> _User:
        return self._user


class _User:
    def __init__(self, http: httpx.Client):
        self._http = http

    def search(self, payload: UserSearchReq) -> int:
        resp = self._http.post(
            f"{_BASE}",
            json=payload.model_dump(by_alias=True, exclude_none=True),
        )
        wrapper = APIWrapper[UserSearchListData].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        if wrapper.data.total == 0:
            raise APIError("no dataset found")
        for item in wrapper.data.data:
            if item.nickname == payload.nickname:
                return item.id
        else:
            raise APIError("no user found")
