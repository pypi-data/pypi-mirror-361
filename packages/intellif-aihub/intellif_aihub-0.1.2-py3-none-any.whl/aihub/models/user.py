# !/usr/bin/env python
# -*-coding:utf-8 -*-


from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel


class UserSearchReq(BaseModel):
    page_size: int = 1000000
    page_num: int = 1
    username: str = ""
    nickname: str = ""
    email: str = ""
    user_ids: List[int] = []
    role_ids: List[int] = []
    role_names: List[str] = []
    status: int = 1


class Role(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    role_type: Optional[int] = None
    menu_ids: Optional[List[int]] = None


class UserSearchDatum(BaseModel):
    id: Optional[int] = 0
    username: Optional[str] = None
    nickname: Optional[str] = None
    email: Optional[str] = None
    status: Optional[int] = None
    created_at: Optional[int] = None
    roles: Optional[List[Role]] = None
    tags: Optional[List[int]] = None


class UserSearchListData(BaseModel):
    total: int
    page_size: int
    page_num: int
    data: List[UserSearchDatum]
