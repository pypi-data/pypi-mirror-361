"""
TGO-Memory Python SDK

TGO-Memory 的 Python 客户端 SDK，提供简洁而强大的 API 接口
用于与 TGO-Memory 服务进行交互。

主要功能：
- 用户档案记忆管理（创建、更新、删除用户档案）
- 用户事件记忆管理（创建、获取、更新、删除事件记录）
- 会话管理（个人聊天、群组聊天）
- 消息处理（添加消息、处理缓冲区）
- 配置管理（档案记忆配置）
- 智能上下文生成（获取用户上下文）

使用示例：
    ```python
    from tgo_memory import TgoMemory

    # 初始化客户端
    client = TgoMemory(
        project_url="https://memory.tgo.ai",
        api_key="your-api-key"
    )

    # 测试连接
    if await client.ping():
        print("✅ 连接成功！")

    # 创建或更新用户
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

    # 获取个人聊天会话
    session = client.get_session(
        session_id=user_id,  # 个人聊天使用用户 ID
        session_type="personal"
    )

    # 添加对话消息
    await session.add([
        {"role": "user", "content": "你好，我是李小明，今年28岁，在北京做软件工程师"},
        {"role": "assistant", "content": "你好李小明！很高兴认识你。作为软件工程师，你主要使用什么技术栈呢？"},
        {"role": "user", "content": "我主要做Python开发，最近在学习机器学习。我住在朝阳区，平时喜欢打篮球"},
        {"role": "assistant", "content": "很棒！Python在机器学习领域确实很受欢迎。朝阳区有很多不错的篮球场，你经常去哪里打球？"}
    ])

    # 处理记忆（让 TGO-Memory 分析对话并提取记忆）
    await session.flush()

    # 获取用户上下文（用于 AI 对话）
    context = await client.get_context(user_id=user_id)
    print(f"上下文内容: {context}")
    ```
"""

__version__ = "1.0.0"
__author__ = "TGO-Memory Team"
__email__ = "team@tgo.ai"

from .client import TgoMemory
from .sync_client import TgoMemory as SyncTgoMemory
from .session import Session
from .exceptions import (
    TGOMemoryError,
    AuthenticationError,
    ValidationError,
    NetworkError,
    ServerError,
    SessionError,
    MemoryError
)
from .models import (
    User,
    Event,
    AddResult,
    FlushResult,
    BufferStatus,
    ProfileConfig,
    ConfigResult,
    ContextConfig,
    Message
)

__all__ = [
    # 版本信息
    "__version__",
    "__author__", 
    "__email__",
    
    # 主要类
    "TgoMemory",
    "SyncTgoMemory",
    "Session",
    
    # 异常类
    "TGOMemoryError",
    "AuthenticationError",
    "ValidationError",
    "NetworkError",
    "ServerError",
    "SessionError",
    "MemoryError",

    # 数据模型
    "User",
    "Event",
    "AddResult",
    "FlushResult",
    "BufferStatus",
    "ProfileConfig",
    "ConfigResult",
    "ContextConfig",
    "Message"
]
