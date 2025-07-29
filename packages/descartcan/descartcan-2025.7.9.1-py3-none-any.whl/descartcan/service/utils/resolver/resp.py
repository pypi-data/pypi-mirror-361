# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# Time       ：2025/6/25 21:51
# Author     ：Maxwell
# Description：
"""

import json
import traceback
from typing import Any, Optional, Type, Union
from pydantic import BaseModel, ValidationError
from descartcan.service.utils.resolver.base import BaseResp
from descartcan.utils.log import logger


def get_data_from_text(text) -> (bool, Any):
    try:
        result = json.loads(text)
        result_code = result.get("code")
        if result_code != 200:
            return False, result.get("message")
        return True, result.get("data")
    except Exception as e:
        logger.info(f"get_data_from_text error: {traceback.format_exc()}")
        return False, None


def get_data_model_from_text(text: str, model: Optional[Type[BaseModel]] = None) -> (bool, Any):
    """
    从文本中解析JSON数据，并可选地使用模型验证数据。

    参数:
        text (str): 要解析的JSON文本
        model (Optional[Type[BaseModel]]): 可选的Pydantic模型，用于验证数据

    返回:
        tuple: (bool, Any) 第一个元素表示是否成功，第二个元素是数据或错误信息
    """
    try:
        result = json.loads(text)

        result_code = result.get("code")
        if result_code != '000000':
            return False, result.get("message")

        data = result.get("data")
        if model is not None:
            if isinstance(data, dict):
                try:
                    validated_data = model.parse_obj(data)
                    return True, validated_data
                except ValidationError as e:
                    logger.info(f"Data validation error: {e}")
                    return False, f"Data validation failed: {e}"
            elif isinstance(data, list):
                data_list = []
                for one in data:
                    try:
                        validated_data = model.parse_obj(one)
                        data_list.append(validated_data)
                    except ValidationError as e:
                        logger.info(f"Data validation error: {e}")
                return True, data_list
        return True, data

    except Exception as e:
        logger.info(f"get_data_from_text error: {traceback.format_exc()}")
        return False, None


def get_model_from_text(text: str, model: Optional[Type[BaseModel]] = None) -> (bool, Any):
    try:
        result = json.loads(text)
        result_code = result.get("code")
        if result_code != '000000':
            return False, result.get("message")

        data = result.get("data")
        if isinstance(data, list):
            try:
                validated_data = model.parse_obj(result)
                return True, validated_data
            except ValidationError as e:
                logger.info(f"Data validation error: {e}")

        if model is not None:
            try:
                validated_data = model.parse_obj(data)
                return True, validated_data
            except ValidationError as e:
                logger.info(f"Data validation error: {e}")
        return False, "data is null"

    except Exception as e:
        logger.info(f"get_data_from_text error: {traceback.format_exc()}")
        return False, None


def parse_response(
    text: str,
    model: Optional[Type[BaseModel]] = None,
    *,
    is_list: bool = False
) -> tuple[bool, Union[BaseModel, list, dict, str]]:
    """
    通用JSON响应解析器
    :param text: JSON字符串
    :param model: 目标Pydantic模型
    :param is_list: 是否强制解析为列表
    :return: (success, data_or_error_message)
    """
    try:
        raw = json.loads(text)

        # 检查业务状态码
        if raw.get("code") != "000000":
            return False, raw.get("message", "Unknown error")

        data = raw.get("data")

        # 无数据情况
        if data is None:
            return (True, [] if is_list else None) if model else (False, "Data is null")

        # 无模型时直接返回原始数据
        if model is None:
            return True, data

        # 列表数据特殊处理
        if isinstance(data, list) or is_list:
            if hasattr(model, "data") and issubclass(model, BaseResp):
                return True, model.parse_obj({**raw, "data": [model.__fields__["data"].type_.parse_obj(item) for item in data]})
            else:
                return True, [model.parse_obj(item) for item in (data if isinstance(data, list) else [data])]

        # 单对象处理
        return True, model.parse_obj(data)

    except json.JSONDecodeError:
        return False, "Invalid JSON format"
    except ValidationError as e:
        return False, f"Validation failed: {str(e)}"
    except Exception:
        return False, traceback.format_exc()