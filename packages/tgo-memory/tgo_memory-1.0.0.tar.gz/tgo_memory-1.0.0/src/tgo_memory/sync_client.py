"""
TGO-Memory 同步客户端

提供同步版本的 TGO-Memory 客户端，基于异步客户端实现。
"""

import asyncio
from typing import Dict, List, Any, Optional, Union

from .client import TgoMemory as AsyncTgoMemory
from .session import Session as AsyncSession
from .models import User, Event, ProfileConfig, ConfigResult
from .exceptions import TGOMemoryError


class Session:
    """同步会话类"""
    
    def __init__(self, async_session: AsyncSession):
        self._async_session = async_session
        self._loop = asyncio.new_event_loop()
    
    def add(self, messages: List[Dict[str, Any]]):
        """添加消息到会话"""
        return self._loop.run_until_complete(
            self._async_session.add(messages)
        )
    
    def flush(self):
        """处理会话缓冲区中的消息"""
        return self._loop.run_until_complete(
            self._async_session.flush()
        )
    
    def get_buffer_status(self):
        """获取会话缓冲区状态"""
        return self._loop.run_until_complete(
            self._async_session.get_buffer_status()
        )
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, '_loop') and self._loop:
            self._loop.close()


class TgoMemory:
    """
    TGO-Memory 同步客户端
    
    提供与 TGO-Memory 服务交互的同步接口。
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
        初始化 TGO-Memory 同步客户端
        
        Args:
            project_url: TGO-Memory 服务的 URL
            api_key: API 密钥
            timeout: 请求超时时间（秒）
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
            debug: 启用调试模式
        """
        self._async_client = AsyncTgoMemory(
            project_url=project_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
            retry_delay=retry_delay,
            debug=debug
        )
        self._loop = asyncio.new_event_loop()
    
    def ping(self) -> bool:
        """测试连接"""
        return self._loop.run_until_complete(
            self._async_client.ping()
        )
    
    def set_user(
        self,
        user_id: str,
        profiles: Dict[str, Dict[str, Any]]
    ) -> User:
        """创建或更新用户"""
        return self._loop.run_until_complete(
            self._async_client.set_user(user_id, profiles)
        )
    
    def get_profile(
        self,
        user_id: str,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """获取用户档案记忆"""
        return self._loop.run_until_complete(
            self._async_client.get_profile(user_id, categories, fields)
        )
    
    def delete_profile_data(
        self,
        user_id: str,
        categories: Optional[List[str]] = None,
        fields: Optional[List[str]] = None
    ) -> bool:
        """删除用户档案数据"""
        return self._loop.run_until_complete(
            self._async_client.delete_profile_data(user_id, categories, fields)
        )
    
    def get_session(
        self,
        session_id: str,
        session_type: str = "personal"
    ) -> Session:
        """获取会话对象"""
        async_session = self._async_client.get_session(session_id, session_type)
        return Session(async_session)
    
    def get_context(
        self,
        user_id: str,
        config: Optional[Dict[str, Any]] = None
    ) -> str:
        """获取用户上下文"""
        return self._loop.run_until_complete(
            self._async_client.get_context(user_id, config)
        )
    
    def update_profile_config(self, config: Dict[str, Any]) -> ConfigResult:
        """更新档案记忆配置"""
        return self._loop.run_until_complete(
            self._async_client.update_profile_config(config)
        )
    
    def get_profile_config(self) -> ProfileConfig:
        """获取档案记忆配置"""
        return self._loop.run_until_complete(
            self._async_client.get_profile_config()
        )
    
    def create_event_record(
        self,
        user_id: str,
        category: str,
        event_data: Dict[str, Any],
        confidence: float = 1.0,
        source: str = "user_input",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """创建事件记录"""
        return self._loop.run_until_complete(
            self._async_client.create_event_record(
                user_id, category, event_data, confidence, source, metadata
            )
        )
    
    def get_events(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        categories: Optional[List[str]] = None,
        importance: Optional[str] = None
    ) -> List[Event]:
        """获取用户事件记录"""
        return self._loop.run_until_complete(
            self._async_client.get_events(
                user_id, start_date, end_date, categories, importance
            )
        )
    
    def get_event(self, event_id: str) -> Event:
        """获取特定事件详情"""
        return self._loop.run_until_complete(
            self._async_client.get_event(event_id)
        )
    
    def update_event_record(
        self,
        event_id: str,
        event_data: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Event:
        """更新事件记录"""
        return self._loop.run_until_complete(
            self._async_client.update_event_record(event_id, event_data, metadata)
        )
    
    def delete_event_record(self, event_id: str) -> bool:
        """删除事件记录"""
        return self._loop.run_until_complete(
            self._async_client.delete_event_record(event_id)
        )
    
    def close(self):
        """关闭客户端连接"""
        self._loop.run_until_complete(self._async_client.close())
        self._loop.close()
    
    def __enter__(self):
        """同步上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """同步上下文管理器出口"""
        self.close()
    
    def __del__(self):
        """清理资源"""
        if hasattr(self, '_loop') and self._loop:
            try:
                self.close()
            except:
                pass
