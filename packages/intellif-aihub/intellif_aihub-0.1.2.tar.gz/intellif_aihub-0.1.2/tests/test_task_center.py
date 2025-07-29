# !/usr/bin/env python
# -*-coding:utf-8 -*-


from __future__ import annotations

import unittest

from src.aihub.client import Client

BASE_URL = "http://192.168.13.160:30021"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NTIwNDgzOTgsImlhdCI6MTc1MTQ0MzU5OCwidWlkIjoxMH0.GqFDpRQuRlNx9YdHlC6zql-8_ZtCpDV4zUFvqM5p7EE"


class TestTaskCenter(unittest.TestCase):
    def test_create_label_task(self):
        client = Client(base_url=BASE_URL, token=TOKEN)
        # task = client.task_center.create_label_task(
        #     name="test_task",
        #     dataset_version_name="re/V1",
        #     feishu_doc_name="人脸质量人脸照片分类",
        #     task_receiver_name="hyc",
        #     project_name="hycpro",
        #     label_type=LabelProjectTypeEnum.IMAGE_CLASSIFICATION,
        #     description="test_description",
        #     task_priority="low",
        #     estimated_delivery_at= "2025-08-01"
        # )
        # print(task)
        task_item = client.task_center.get(1923)
        print(task_item)
