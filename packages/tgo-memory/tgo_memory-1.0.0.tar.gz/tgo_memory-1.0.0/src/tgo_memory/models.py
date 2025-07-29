"""
TGO-Memory SDK 数据模型

定义 SDK 中使用的数据模型和响应对象。
"""

from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class User:
    """用户模型"""

    user_id: str
    profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """从字典创建用户对象"""
        return cls(
            user_id=data["user_id"],
            profiles=data.get("profiles", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "profiles": self.profiles,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class Event:
    """事件模型"""

    event_id: str
    user_id: str
    category: str
    event_data: Dict[str, Any]
    confidence: float = 1.0
    source: str = "user_input"
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Event":
        """从字典创建事件对象"""
        return cls(
            event_id=data["event_id"],
            user_id=data["user_id"],
            category=data["category"],
            event_data=data["event_data"],
            confidence=data.get("confidence", 1.0),
            source=data.get("source", "user_input"),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "event_id": self.event_id,
            "user_id": self.user_id,
            "category": self.category,
            "event_data": self.event_data,
            "confidence": self.confidence,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class AddResult:
    """添加消息结果"""

    session_id: str
    session_type: str
    added_messages: int
    message_ids: List[str] = field(default_factory=list)
    timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AddResult":
        """从字典创建结果对象"""
        return cls(
            session_id=data["session_id"],
            session_type=data["session_type"],
            added_messages=data["added_messages"],
            message_ids=data.get("message_ids", []),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "added_messages": self.added_messages,
            "message_ids": self.message_ids,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


@dataclass
class FlushResult:
    """处理缓冲区结果"""

    session_id: str
    session_type: str  # 后端现在返回 session_type 字段
    processed_messages: int
    profile_memories_count: int = 0
    event_memories_count: int = 0
    status: str = "success"
    processed_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FlushResult":
        """从字典创建结果对象"""
        return cls(
            session_id=data["session_id"],
            session_type=data["session_type"],  # 使用 session_type 字段
            processed_messages=data["processed_messages"],
            profile_memories_count=data.get("profile_memories_count", 0),
            event_memories_count=data.get("event_memories_count", 0),
            status=data.get("status", "success"),
            processed_at=datetime.fromisoformat(data["processed_at"]) if data.get("processed_at") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "processed_messages": self.processed_messages,
            "profile_memories_count": self.profile_memories_count,
            "event_memories_count": self.event_memories_count,
            "status": self.status,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class BufferStatus:
    """缓冲区状态"""

    session_id: str
    session_type: str
    pending_messages: int = 0
    last_flush_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BufferStatus":
        """从字典创建缓冲区状态对象"""
        return cls(
            session_id=data["session_id"],
            session_type=data["session_type"],
            pending_messages=data.get("pending_messages", 0),
            last_flush_at=datetime.fromisoformat(data["last_flush_at"]) if data.get("last_flush_at") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "pending_messages": self.pending_messages,
            "last_flush_at": self.last_flush_at.isoformat() if self.last_flush_at else None
        }


@dataclass
class ProfileConfig:
    """档案记忆配置"""

    profiles: Dict[str, Dict[str, Dict[str, Union[bool, str]]]] = field(default_factory=dict)
    last_updated: Optional[datetime] = None
    version: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProfileConfig":
        """从字典创建配置对象"""
        return cls(
            profiles=data.get("profiles", {}),
            last_updated=datetime.fromisoformat(data["last_updated"]) if data.get("last_updated") else None,
            version=data.get("version")
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "profiles": self.profiles,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
            "version": self.version
        }


@dataclass
class ConfigResult:
    """配置更新结果"""

    status: str = "success"
    message: str = "配置更新成功"
    config_version: Optional[str] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ConfigResult":
        """从字典创建配置结果对象"""
        return cls(
            status=data.get("status", "success"),
            message=data.get("message", "配置更新成功"),
            config_version=data.get("config_version"),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "status": self.status,
            "message": self.message,
            "config_version": self.config_version,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


@dataclass
class Message:
    """消息模型"""

    role: str  # "user", "assistant", "system"
    content: str
    user_id: Optional[str] = None  # 群组会话中的用户消息需要此字段
    timestamp: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Message":
        """从字典创建消息对象"""
        return cls(
            role=data["role"],
            content=data["content"],
            user_id=data.get("user_id"),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else None
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "role": self.role,
            "content": self.content
        }
        if self.user_id:
            result["user_id"] = self.user_id
        if self.timestamp:
            result["timestamp"] = self.timestamp.isoformat()
        return result


@dataclass
class ContextConfig:
    """上下文配置"""

    max_length: int = 2000
    categories: Optional[List[str]] = None
    priority: str = "recent"  # "recent", "important", "balanced"
    include_profile: bool = True
    include_events: bool = True
    time_range: Optional[Dict[str, int]] = None  # {"days": 30}

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "max_length": self.max_length,
            "priority": self.priority,
            "include_profile": self.include_profile,
            "include_events": self.include_events
        }
        if self.categories:
            result["categories"] = self.categories
        if self.time_range:
            result["time_range"] = self.time_range
        return result
