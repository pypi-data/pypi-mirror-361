"""
TGO-Memory Python 客户端

主要的客户端类，提供与 TGO-Memory API 交互的接口。
"""

from typing import Dict, List, Any, Optional, Union
import httpx
from urllib.parse import urljoin

from .session import Session
from .models import User, Event, ProfileConfig, ConfigResult, ContextConfig
from .exceptions import (
    TGOMemoryError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    ServerError
)
from .utils import (
    validate_user_id,
    validate_profiles,
    validate_categories_list,
    validate_fields_list,
    validate_event_data,
    format_api_error,
    build_query_params
)


class TgoMemory:
    """
    TGO-Memory 客户端
    
    提供与 TGO-Memory 服务交互的主要接口。
    """
    
    def __init__(
        self,
        project_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        debug: bool = False
    ):
        """
        初始化 TGO-Memory 客户端

        Args:
            project_url: TGO-Memory 服务的 URL
            api_key: API 密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            debug: 启用调试模式
        """
        self.project_url = project_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.debug = debug

        # 创建 HTTP 客户端
        self._http_client = httpx.AsyncClient(
            base_url=self.project_url,
            headers={
                "X-API-Key": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": f"tgo-memory-python-sdk/1.0.0"
            },
            timeout=self.timeout
        )
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def close(self):
        """关闭客户端连接"""
        if self._http_client:
            await self._http_client.aclose()
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送 HTTP 请求
        
        Args:
            method: HTTP 方法
            endpoint: API 端点
            data: 请求数据
            params: 查询参数
            
        Returns:
            Dict[str, Any]: 响应数据
            
        Raises:
            TGOMemoryError: 请求失败时抛出相应异常
        """
        url = endpoint
        
        try:
            response = await self._http_client.request(
                method=method,
                url=url,
                json=data,
                params=params
            )
            
            # 检查响应状态
            if response.status_code == 401:
                raise AuthenticationError("API 密钥无效或已过期")
            elif response.status_code == 400:
                error_detail = response.json().get("detail", "请求参数错误")
                raise ValidationError(error_detail)
            elif response.status_code >= 500:
                raise ServerError(f"服务器错误: {response.status_code}")
            elif response.status_code >= 400:
                error_detail = response.json().get("detail", "请求失败")
                raise TGOMemoryError(f"请求失败: {error_detail}")
            
            return response.json()
            
        except httpx.RequestError as e:
            raise NetworkError(f"网络请求失败: {str(e)}")
        except httpx.TimeoutException:
            raise NetworkError("请求超时")

    async def ping(self) -> bool:
        """
        测试连接

        Returns:
            bool: 连接是否成功

        Example:
            ```python
            if await client.ping():
                print("✅ 连接成功！")
            else:
                print("❌ 连接失败，请检查配置")
            ```
        """
        try:
            response = await self._make_request("GET", "/api/ping/")
            return response.get("status") == "ok"
        except Exception:
            return False

    async def set_user(
        self,
        user_id: str,
        profiles: Dict[str, Dict[str, Any]]
    ) -> User:
        """
        创建或更新用户

        使用 upsert 模式：如果用户不存在则创建，存在则更新。

        Args:
            user_id: 用户 ID（由外部系统提供）
            profiles: 用户档案数据，格式为 {"category": {"field": "value"}}

        Returns:
            User: 用户对象

        Raises:
            ValidationError: 参数验证失败
            TGOMemoryError: 操作失败

        Example:
            ```python
            user = await client.set_user(
                user_id="user_lixiaoming_001",
                profiles={
                    "basic_info": {
                        "name": "李小明",
                        "age": "28",
                        "location": "北京",
                        "occupation": "软件工程师"
                    },
                    "contact": {
                        "email": "lixiaoming@example.com",
                        "timezone": "Asia/Shanghai",
                        "language": "zh-CN"
                    }
                }
            )
            ```
        """
        # 验证参数
        validate_user_id(user_id)
        validate_profiles(profiles)

        response = await self._make_request(
            "POST",
            f"/api/profiles/{user_id}",
            data=profiles
        )
        return User.from_dict(response)

    async def get_profile(
        self,
        user_id: str,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        获取用户档案记忆

        Args:
            user_id: 用户 ID
            categories: 要获取的类别列表，可选
            fields: 要获取的字段列表（格式：category.field），可选

        Returns:
            Dict[str, Any]: 用户档案数据

        Raises:
            ValidationError: 参数验证失败
            TGOMemoryError: 操作失败

        Example:
            ```python
            # 获取完整档案
            profile = await client.get_profile(user_id="user_12345")

            # 获取特定类别
            basic_info = await client.get_profile(
                user_id="user_12345",
                categories=["basic_info"]
            )

            # 获取特定字段
            name_and_age = await client.get_profile(
                user_id="user_12345",
                fields=["basic_info.name", "basic_info.age"]
            )
            ```
        """
        validate_user_id(user_id)
        validate_categories_list(categories)
        validate_fields_list(fields)

        params = {}
        if categories:
            params["categories"] = categories
        if fields:
            params["fields"] = fields

        query_params = build_query_params(params)

        response = await self._make_request(
            "GET",
            f"/api/profiles/{user_id}",
            params=query_params
        )
        return response

    async def delete_profile_data(
        self,
        user_id: str,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> bool:
        """
        删除用户档案数据

        Args:
            user_id: 用户 ID
            categories: 要删除的类别列表，可选
            fields: 要删除的字段列表（格式：category.field），可选

        Returns:
            bool: 删除是否成功

        Raises:
            ValidationError: 参数验证失败
            TGOMemoryError: 操作失败

        Example:
            ```python
            # 删除特定类别
            await client.delete_profile_data(
                user_id="user_12345",
                categories=["interests"]
            )

            # 删除特定字段
            await client.delete_profile_data(
                user_id="user_12345",
                fields=["basic_info.age", "relationships.colleagues"]
            )
            ```
        """
        validate_user_id(user_id)
        validate_categories_list(categories)
        validate_fields_list(fields)

        data = {}
        if categories:
            data["categories"] = categories
        if fields:
            data["fields"] = fields

        await self._make_request(
            "DELETE",
            f"/api/profiles/{user_id}",
            data=data
        )
        return True

    def get_session(
        self,
        session_id: str,
        session_type: str = "personal"
    ) -> Session:
        """
        获取会话对象
        
        Args:
            session_id: 会话 ID
            session_type: 会话类型，支持 "personal" 和 "group"
            
        Returns:
            Session: 会话对象
            
        Raises:
            ValidationError: 参数验证失败
            
        Example:
            ```python
            # 个人会话
            session = client.get_session(
                session_id="user123",  # 个人会话使用用户 ID
                session_type="personal"
            )
            
            # 群组会话
            session = client.get_session(
                session_id="group456",
                session_type="group"
            )
            ```
        """
        if not session_id or not isinstance(session_id, str):
            raise ValidationError("session_id 必须是非空字符串")
        
        if session_type not in ["personal", "group"]:
            raise ValidationError("session_type 必须是 'personal' 或 'group'")
        
        return Session(
            client=self,
            session_id=session_id,
            session_type=session_type
        )
    
    async def get_context(
        self,
        user_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        获取用户上下文
        
        基于用户的记忆数据生成上下文文本。
        
        Args:
            user_id: 用户 ID
            config: 上下文配置，可选参数
            
        Returns:
            str: 生成的用户上下文
            
        Raises:
            ValidationError: 参数验证失败
            TgoMemoryError: 操作失败
            
        Example:
            ```python
            # 基础用法
            context = await client.get_context(user_id="user123")
            
            # 带配置的用法
            context = await client.get_context(
                user_id="user123",
                config={
                    "categories": ["basic_info", "preferences"],
                    "max_length": 2000,
                    "include_recent_events": True
                }
            )
            ```
        """
        validate_user_id(user_id)
        
        data = {
            "user_id": user_id
        }
        
        if config:
            data["config"] = config
        
        params = build_query_params(data) if config else {}

        response = await self._make_request(
            "GET",
            f"/api/memory/{user_id}/context",
            params=params
        )
        return response.get("context", "")

    async def update_profile_config(self, config: Dict[str, Any]) -> ConfigResult:
        """
        更新档案记忆配置

        Args:
            config: 配置数据

        Returns:
            ConfigResult: 配置更新结果

        Example:
            ```python
            config = {
                "profiles": {
                    "basic_info": {
                        "name": {"enabled": True, "priority": "high"},
                        "age": {"enabled": True, "priority": "medium"}
                    }
                }
            }
            result = await client.update_profile_config(config=config)
            ```
        """
        response = await self._make_request(
            "PUT",
            "/api/config/profile",
            data=config
        )
        return ConfigResult.from_dict(response)

    async def get_profile_config(self) -> ProfileConfig:
        """
        获取档案记忆配置

        Returns:
            ProfileConfig: 当前配置

        Example:
            ```python
            config = await client.get_profile_config()
            print("当前配置:", config.profiles)
            ```
        """
        response = await self._make_request("GET", "/api/config/profile")
        return ProfileConfig.from_dict(response)

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户档案记忆
        
        Args:
            user_id: 用户 ID
            
        Returns:
            Dict[str, Any]: 用户档案记忆数据
        """
        validate_user_id(user_id)
        
        response = await self._make_request("GET", f"/memory/profile/{user_id}")
        return response

    async def create_event_record(
        self,
        user_id: str,
        category: str,
        event_data: Dict[str, Any],
        confidence: float = 1.0,
        source: str = "user_input",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        创建事件记录

        Args:
            user_id: 用户 ID
            category: 事件类别
            event_data: 事件数据
            confidence: 置信度 (0.0-1.0)
            source: 数据源
            metadata: 元数据

        Returns:
            Event: 创建的事件对象

        Example:
            ```python
            event = await client.create_event_record(
                user_id="user_12345",
                category="professional",
                event_data={
                    "title": "升职为高级产品经理",
                    "description": "经过两年努力，升职为高级产品经理",
                    "date": "2024-01-15",
                    "importance": "high"
                },
                confidence=1.0,
                source="user_sharing"
            )
            ```
        """
        validate_user_id(user_id)
        validate_event_data(event_data)

        data = {
            "user_id": user_id,
            "category": category,
            "event_data": event_data,
            "confidence": confidence,
            "source": source,
            "metadata": metadata or {}
        }

        response = await self._make_request("POST", "/api/events", data=data)
        return Event.from_dict(response)

    async def get_events(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        categories: Optional[List[str]] = None,
        importance: Optional[str] = None
    ) -> List[Event]:
        """
        获取用户事件记录

        Args:
            user_id: 用户 ID
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            categories: 事件类别列表
            importance: 重要性级别

        Returns:
            List[Event]: 事件列表

        Example:
            ```python
            # 获取所有事件
            events = await client.get_events(user_id="user_12345")

            # 按时间范围获取
            recent_events = await client.get_events(
                user_id="user_12345",
                start_date="2024-01-01",
                end_date="2024-12-31"
            )
            ```
        """
        validate_user_id(user_id)
        validate_categories_list(categories)

        params = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if categories:
            params["categories"] = categories
        if importance:
            params["importance"] = importance

        query_params = build_query_params(params)

        response = await self._make_request(
            "GET",
            f"/api/events/{user_id}",
            params=query_params
        )

        # 后端返回的是 EventListResponse，包含 events 字段
        events_data = response.get("events", [])
        events = []

        for event_data in events_data:
            # 构造符合 Event 模型的数据结构
            event_dict = {
                "event_id": event_data.get("event_id"),
                "user_id": event_data.get("user_id"),
                "category": event_data.get("category"),
                "event_data": {
                    "title": event_data.get("title"),
                    "description": event_data.get("description"),
                    "event_date": event_data.get("event_date"),
                    "location": event_data.get("location"),
                    "importance": event_data.get("importance"),
                    "sentiment": event_data.get("sentiment")
                },
                "confidence": event_data.get("confidence", 1.0),
                "source": event_data.get("source", "unknown"),
                "metadata": event_data.get("event_metadata", {}),
                "created_at": event_data.get("created_at"),
                "updated_at": event_data.get("updated_at")
            }
            events.append(Event.from_dict(event_dict))

        return events

    async def get_event(self, event_id: str) -> Event:
        """
        获取特定事件详情

        Args:
            event_id: 事件 ID

        Returns:
            Event: 事件对象
        """
        response = await self._make_request("GET", f"/api/events/{event_id}")
        return Event.from_dict(response)

    async def update_event_record(
        self,
        event_id: str,
        event_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """
        更新事件记录

        Args:
            event_id: 事件 ID
            event_data: 更新的事件数据
            metadata: 更新的元数据

        Returns:
            Event: 更新后的事件对象
        """
        data = {}
        if event_data:
            data["event_data"] = event_data
        if metadata:
            data["metadata"] = metadata

        response = await self._make_request("PUT", f"/api/events/{event_id}", data=data)
        return Event.from_dict(response)

    async def delete_event_record(self, event_id: str) -> bool:
        """
        删除事件记录

        Args:
            event_id: 事件 ID

        Returns:
            bool: 删除是否成功
        """
        try:
            await self._make_request("DELETE", f"/api/events/{event_id}")
            return True
        except TGOMemoryError:
            return False

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索用户记忆
        
        Args:
            user_id: 用户 ID
            query: 搜索查询
            limit: 结果数量限制
            
        Returns:
            List[Dict[str, Any]]: 搜索结果
        """
        validate_user_id(user_id)
        
        if not query or not isinstance(query, str):
            raise ValidationError("query 必须是非空字符串")
        
        data = {
            "user_id": user_id,
            "query": query,
            "limit": limit
        }
        
        response = await self._make_request("POST", "/memory/search", data=data)
        return response.get("results", [])
    
    async def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 服务健康状态
        """
        return await self._make_request("GET", "/health")
