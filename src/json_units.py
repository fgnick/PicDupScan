#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ===============================================================================================
import json

class JsonUtils:

    @staticmethod
    def parse_json(data: str):
        if not isinstance(data, str):
            raise TypeError("JSON data must be a string")

        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError("Invalid JSON string") from e

    @staticmethod
    def is_valid_json(data: str) -> bool:
        if data is None or not isinstance(data, str):
            return False
        try:
            json.loads(data)
            return True
        except json.JSONDecodeError:
            return False