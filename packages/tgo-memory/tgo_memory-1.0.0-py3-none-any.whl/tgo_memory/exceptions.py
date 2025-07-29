"""
TGO-Memory SDK 异常定义

定义 SDK 中使用的各种异常类型。
"""


class TGOMemoryError(Exception):
    """TGO-Memory SDK 基础异常类"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(TGOMemoryError):
    """认证失败异常"""

    def __init__(self, message: str = "认证失败"):
        super().__init__(message, "AUTH_ERROR")


class ValidationError(TGOMemoryError):
    """参数验证失败异常"""

    def __init__(self, message: str = "参数验证失败"):
        super().__init__(message, "VALIDATION_ERROR")


class NetworkError(TGOMemoryError):
    """网络请求异常"""

    def __init__(self, message: str = "网络请求失败"):
        super().__init__(message, "NETWORK_ERROR")


class ServerError(TGOMemoryError):
    """服务器错误异常"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(message, "SERVER_ERROR")


class NotFoundError(TGOMemoryError):
    """资源不存在异常"""

    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(message, "NOT_FOUND")


class RateLimitError(TGOMemoryError):
    """请求频率限制异常"""

    def __init__(self, message: str = "请求频率超过限制"):
        super().__init__(message, "RATE_LIMIT")


class ConfigurationError(TGOMemoryError):
    """配置错误异常"""

    def __init__(self, message: str = "配置错误"):
        super().__init__(message, "CONFIG_ERROR")


class SessionError(TGOMemoryError):
    """会话操作异常"""

    def __init__(self, message: str = "会话操作失败"):
        super().__init__(message, "SESSION_ERROR")


class MemoryError(TGOMemoryError):
    """记忆操作异常"""

    def __init__(self, message: str = "记忆操作失败"):
        super().__init__(message, "MEMORY_ERROR")
