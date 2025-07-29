"""
TGO-Memory 会话类

提供会话级别的操作，包括消息添加和处理。
"""

from typing import Dict, List, Any, TYPE_CHECKING
from .models import AddResult, FlushResult, BufferStatus
from .exceptions import ValidationError, TGOMemoryError, SessionError
from .utils import validate_messages

if TYPE_CHECKING:
    from .client import TgoMemory


class Session:
    """
    TGO-Memory 会话类
    
    提供会话级别的消息操作接口。会话是消息的容器，
    支持批量添加消息和触发记忆处理。
    """
    
    def __init__(
        self,
        client: "TgoMemory",
        session_id: str,
        session_type: str = "personal"
    ):
        """
        初始化会话对象
        
        Args:
            client: TgoMemory 客户端实例
            session_id: 会话 ID
            session_type: 会话类型 ("personal" 或 "group")
        """
        self.client = client
        self.session_id = session_id
        self.session_type = session_type
    
    async def add(self, messages: List[Dict[str, Any]]) -> AddResult:
        """
        添加消息到会话

        消息会被添加到会话的缓冲区中，等待后续处理。

        Args:
            messages: 消息列表，每个消息包含 role 和 content 字段

        Returns:
            AddResult: 添加操作的结果

        Raises:
            ValidationError: 消息格式验证失败
            TGOMemoryError: 添加操作失败

        Example:
            ```python
            # 个人聊天添加消息
            result = await session.add([
                {"role": "user", "content": "你好，我是张三"},
                {"role": "assistant", "content": "你好张三！很高兴认识你。"}
            ])

            # 群组聊天添加消息（需要指定 user_id）
            if session.session_type == "group":
                result = await session.add([
                    {
                        "role": "user",
                        "content": "大家好",
                        "user_id": "user123"
                    }
                ])
            ```
        """
        # 验证消息格式
        validate_messages(messages, self.session_type)

        # 构造符合后端 MessageAddRequest 格式的数据
        data = {
            "session_type": self.session_type,
            "messages": messages
        }

        response = await self.client._make_request(
            "POST",
            f"/api/sessions/{self.session_id}/messages",
            data=data
        )

        return AddResult.from_dict(response)
    
    async def flush(self, force: bool = False) -> FlushResult:
        """
        处理会话缓冲区中的消息

        触发记忆提取和处理流程，将缓冲区中的消息进行分析，
        提取用户档案记忆和事件记忆。

        Args:
            force: 是否强制处理（即使缓冲区未满）

        Returns:
            FlushResult: 处理操作的结果

        Raises:
            TGOMemoryError: 处理操作失败

        Example:
            ```python
            # 处理缓冲区
            result = await session.flush()

            # 强制处理
            result = await session.flush(force=True)

            print(f"处理了 {result.processed_messages} 条消息")
            print(f"提取了 {result.profile_memories_count} 个档案记忆")
            print(f"提取了 {result.event_memories_count} 个事件记忆")
            ```
        """
        params = {"session_type": self.session_type}
        data = {"force": force}

        response = await self.client._make_request(
            "POST",
            f"/api/sessions/{self.session_id}/flush",
            params=params,
            data=data
        )

        return FlushResult.from_dict(response)

    async def get_buffer_status(self) -> BufferStatus:
        """
        获取会话缓冲区状态

        Returns:
            BufferStatus: 缓冲区状态信息

        Raises:
            TGOMemoryError: 获取状态失败

        Example:
            ```python
            status = await session.get_buffer_status()
            print(f"待处理消息数: {status.pending_messages}")
            ```
        """
        params = {"session_type": self.session_type}

        response = await self.client._make_request(
            "GET",
            f"/api/sessions/{self.session_id}/status",
            params=params
        )

        return BufferStatus.from_dict(response)

    async def get_messages(
        self,
        skip: int = 0,
        limit: int = 100,
        include_buffer: bool = True
    ) -> List[Dict[str, Any]]:
        """
        获取会话中的消息
        
        Args:
            skip: 跳过的消息数量
            limit: 返回的消息数量限制
            include_buffer: 是否包含缓冲区中未处理的消息
            
        Returns:
            List[Dict[str, Any]]: 消息列表
        """
        params = {
            "skip": skip,
            "limit": limit,
            "include_buffer": include_buffer
        }
        
        response = await self.client._make_request(
            "GET",
            f"/sessions/{self.session_id}/messages",
            params=params
        )
        
        return response.get("messages", [])
    
    async def get_info(self) -> Dict[str, Any]:
        """
        获取会话信息
        
        Returns:
            Dict[str, Any]: 会话详细信息
        """
        response = await self.client._make_request(
            "GET",
            f"/sessions/{self.session_id}"
        )
        
        return response
    
    async def delete(self) -> bool:
        """
        删除会话
        
        Returns:
            bool: 删除是否成功
        """
        try:
            await self.client._make_request(
                "DELETE",
                f"/sessions/{self.session_id}"
            )
            return True
        except TGOMemoryError:
            return False
    

    
    def __repr__(self) -> str:
        return f"<Session(id={self.session_id}, type={self.session_type})>"
