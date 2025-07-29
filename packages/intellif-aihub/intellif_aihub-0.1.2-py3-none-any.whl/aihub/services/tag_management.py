# !/usr/bin/env python
# -*-coding:utf-8 -*-
from __future__ import annotations

import httpx

from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.tag_management import *

_BASE = "/tag-resource-management/api/v1"


class TagManagementService:
    def __init__(self, http: httpx.Client):
        self._project = _Project(http)

    def select_projects(self) -> List[Project]:
        return self._project.select_projects()

    @property
    def project(self) -> _Project:
        return self._project


class _Project:
    def __init__(self, http: httpx.Client):
        self._http = http

    def select_projects(self) -> List[Project]:
        resp = self._http.get(f"{_BASE}/select-projects")
        wrapper = APIWrapper[ProjectListData].model_validate(resp.json())
        if wrapper.code != 0:
            raise APIError(f"backend code {wrapper.code}: {wrapper.msg}")
        return wrapper.data.data
