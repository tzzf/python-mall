from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Optional

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "*",
    "Access-Control-Allow-Headers": "*",
}

class APIException(HTTPException):
    """统一异常基类"""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[int] = None,
        error_type: str = "api_error",
    ):
        self.code = code or status_code
        self.error_type = error_type
        super().__init__(
            status_code=status_code,
            detail={
                "code": self.code,
                "message": message,
                "type": self.error_type,
            },
        )


class TokenException(APIException):
    """Token 认证异常"""

    def __init__(self, message: str = "无效的 Token"):
        super().__init__(
            status_code=401,
            message=message,
            error_type="auth_error",
        )


class PermissionException(APIException):
    """权限不足"""

    def __init__(self, message: str = "权限不足"):
        super().__init__(
            status_code=403,
            message=message,
            error_type="permission_error",
        )


class NotFoundException(APIException):
    """资源不存在"""

    def __init__(self, message: str = "资源不存在"):
        super().__init__(
            status_code=404,
            message=message,
            error_type="not_found",
        )


class ValidationException(APIException):
    """参数校验失败"""

    def __init__(self, message: str = "参数错误"):
        super().__init__(
            status_code=422,
            message=message,
            error_type="validation_error",
        )


class ServerException(APIException):
    """服务端异常"""

    def __init__(self, message: str = "服务器内部错误"):
        super().__init__(
            status_code=500,
            message=message,
            code=500,
            error_type="server_error",
        )


async def api_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """全局异常处理器：统一格式所有 HTTPException"""
    detail = exc.detail if isinstance(exc.detail, dict) else {"message": str(exc.detail)}

    # 如果已经是标准格式直接返回
    if "code" in detail and "message" in detail:
        return JSONResponse(
            content=detail,
            status_code=exc.status_code,
            headers=CORS_HEADERS,
        )

    # 否则包装成标准格式
    return JSONResponse(
        content={
            "code": exc.status_code,
            "message": detail.get("message", str(detail)),
            "type": "http_error",
        },
        status_code=exc.status_code,
        headers=CORS_HEADERS,
    )

async def api_other_exception_handler(_request: Request, exc: Exception) -> JSONResponse:

    # 否则包装成标准格式
    return JSONResponse(
        content={
            "code": 500,
            "message": "服务器内部错误",
            "type": "Internal_server_error",
        },
        status_code=500,
        headers=CORS_HEADERS,
    )
