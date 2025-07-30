class RagflowError(Exception):
    """
    Ragflow-toolkit 所有异常的基类。
    Attributes:
        message (str): 错误信息。
        code (Any): 错误码。
        response (Any): 原始响应。
    """
    def __init__(self, message=None, code=None, response=None):
        self.message = message or "An error occurred in ragflow-toolkit."
        self.code = code
        self.response = response
        super().__init__(self.message)

class NetworkError(RagflowError):
    """网络相关异常。"""
    pass

class AuthError(RagflowError):
    """认证/授权相关异常。"""
    pass

class NotFoundError(RagflowError):
    """资源未找到异常。"""
    pass

class BadRequestError(RagflowError):
    """请求参数错误异常。"""
    pass

class ServerError(RagflowError):
    """服务端错误异常。"""
    pass

class SDKError(RagflowError):
    """SDK 内部错误/未知错误。"""
    pass 