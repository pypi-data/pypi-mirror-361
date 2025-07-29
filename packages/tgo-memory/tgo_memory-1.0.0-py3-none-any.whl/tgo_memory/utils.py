"""
TGO-Memory SDK 工具函数

提供 SDK 中使用的工具函数和验证逻辑。
"""

import re
import json
from typing import List, Dict, Any, Optional, Union
from .exceptions import ValidationError


def validate_user_id(user_id: str) -> None:
    """
    验证用户 ID 格式

    Args:
        user_id: 用户 ID

    Raises:
        ValidationError: 用户 ID 格式不正确
    """
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("user_id 必须是非空字符串")

    if len(user_id) > 255:
        raise ValidationError("user_id 长度不能超过 255 个字符")

    # 检查是否包含非法字符
    if not re.match(r'^[a-zA-Z0-9_\-\.]+$', user_id):
        raise ValidationError("user_id 只能包含字母、数字、下划线、连字符和点号")


def validate_profiles(profiles: Dict[str, Dict[str, Any]]) -> None:
    """
    验证档案数据格式

    Args:
        profiles: 档案数据字典，格式为 {"category": {"field": "value"}}

    Raises:
        ValidationError: 档案数据格式不正确
    """
    if not isinstance(profiles, dict):
        raise ValidationError("profiles 必须是字典类型")

    for category_name, fields in profiles.items():
        if not isinstance(category_name, str) or not category_name.strip():
            raise ValidationError("类别名称必须是非空字符串")

        if not isinstance(fields, dict):
            raise ValidationError(f"类别 '{category_name}' 的字段必须是字典类型")

        # 验证字段
        for field_name, field_value in fields.items():
            if not isinstance(field_name, str) or not field_name.strip():
                raise ValidationError(f"类别 '{category_name}' 的字段名称必须是非空字符串")


def validate_session_type(session_type: str) -> None:
    """
    验证会话类型

    Args:
        session_type: 会话类型

    Raises:
        ValidationError: 会话类型不正确
    """
    valid_types = ["personal", "group"]
    if session_type not in valid_types:
        raise ValidationError(f"session_type 必须是 {valid_types} 中的一个")


def validate_message_role(role: str) -> None:
    """
    验证消息角色

    Args:
        role: 消息角色

    Raises:
        ValidationError: 消息角色不正确
    """
    valid_roles = ["user", "assistant", "system"]
    if role not in valid_roles:
        raise ValidationError(f"消息 role 必须是 {valid_roles} 中的一个")


def validate_messages(messages: List[Dict[str, Any]], session_type: str = "personal") -> None:
    """
    验证消息列表格式

    Args:
        messages: 消息列表
        session_type: 会话类型

    Raises:
        ValidationError: 消息格式不正确
    """
    if not messages or not isinstance(messages, list):
        raise ValidationError("messages 必须是非空列表")

    for i, message in enumerate(messages):
        if not isinstance(message, dict):
            raise ValidationError(f"消息 {i} 必须是字典类型")

        # 检查必需字段
        if "role" not in message:
            raise ValidationError(f"消息 {i} 缺少 'role' 字段")

        if "content" not in message:
            raise ValidationError(f"消息 {i} 缺少 'content' 字段")

        # 验证 role 字段
        validate_message_role(message["role"])

        # 验证 content 字段
        if not isinstance(message["content"], str) or not message["content"].strip():
            raise ValidationError(f"消息 {i} 的 content 必须是非空字符串")

        # 群组会话的特殊验证
        if session_type == "group" and message["role"] == "user":
            if "user_id" not in message:
                raise ValidationError(f"群组会话的用户消息 {i} 必须包含 'user_id' 字段")

            if not isinstance(message["user_id"], str) or not message["user_id"].strip():
                raise ValidationError(f"消息 {i} 的 user_id 必须是非空字符串")


def validate_event_data(event_data: Dict[str, Any]) -> None:
    """
    验证事件数据格式

    Args:
        event_data: 事件数据

    Raises:
        ValidationError: 事件数据格式不正确
    """
    if not isinstance(event_data, dict):
        raise ValidationError("event_data 必须是字典类型")

    # 检查必需字段
    required_fields = ["title", "description"]
    for field in required_fields:
        if field not in event_data:
            raise ValidationError(f"event_data 缺少必需字段: {field}")

        if not isinstance(event_data[field], str) or not event_data[field].strip():
            raise ValidationError(f"event_data.{field} 必须是非空字符串")


def validate_categories_list(categories: Optional[List[str]]) -> None:
    """
    验证类别列表

    Args:
        categories: 类别列表

    Raises:
        ValidationError: 类别列表格式不正确
    """
    if categories is not None:
        if not isinstance(categories, list):
            raise ValidationError("categories 必须是列表类型")

        for i, category in enumerate(categories):
            if not isinstance(category, str) or not category.strip():
                raise ValidationError(f"categories[{i}] 必须是非空字符串")


def validate_fields_list(fields: Optional[List[str]]) -> None:
    """
    验证字段列表

    Args:
        fields: 字段列表，格式为 ["category.field"]

    Raises:
        ValidationError: 字段列表格式不正确
    """
    if fields is not None:
        if not isinstance(fields, list):
            raise ValidationError("fields 必须是列表类型")

        for i, field in enumerate(fields):
            if not isinstance(field, str) or not field.strip():
                raise ValidationError(f"fields[{i}] 必须是非空字符串")

            # 验证字段格式 (category.field)
            if "." not in field:
                raise ValidationError(f"fields[{i}] 必须是 'category.field' 格式")


def format_api_error(status_code: int, response_data: Dict[str, Any]) -> str:
    """
    格式化 API 错误信息

    Args:
        status_code: HTTP 状态码
        response_data: 响应数据

    Returns:
        str: 格式化的错误信息
    """
    error_message = response_data.get("detail", "未知错误")
    error_code = response_data.get("error_code", "UNKNOWN_ERROR")

    return f"[{status_code}] {error_code}: {error_message}"


def build_query_params(params: Dict[str, Any]) -> Dict[str, str]:
    """
    构建查询参数

    Args:
        params: 参数字典

    Returns:
        Dict[str, str]: 查询参数字典
    """
    query_params = {}

    for key, value in params.items():
        if value is not None:
            if isinstance(value, (list, dict)):
                query_params[key] = json.dumps(value)
            else:
                query_params[key] = str(value)

    return query_params
