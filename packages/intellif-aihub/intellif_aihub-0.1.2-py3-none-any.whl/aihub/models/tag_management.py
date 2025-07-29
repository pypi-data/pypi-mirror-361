# !/usr/bin/env python
# -*-coding:utf-8 -*-

from __future__ import annotations

from typing import List

from pydantic import BaseModel


class Project(BaseModel):
    id: int
    name: str


class ProjectListData(BaseModel):
    data: List[Project]


class SelectProjectsResponse(BaseModel):
    data: List[Project]
