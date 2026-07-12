import json
from fastapi import Request
from fastapi.responses import JSONResponse

def wrap_error_response(status_code: int, message: str, error_type: str = "error") -> dict:
    """统一错误响应格式"""
    return {
        "code": status_code,
        "message": message,
        "type": error_type,
    }


async def add_code_wrapper(request: Request, call_next):
    response = await call_next(request)

    if not request.url.path.startswith("/api"):
        return response
    
    safe_headers = {k: v for k, v in response.headers.items()
                        if k.lower() not in ("content-length", "content-encoding")}

    # 非 2xx 响应：包装成统一错误格式
    if not (200 <= response.status_code < 300):
        try:
            resp_body = [section async for section in response.body_iterator]
            body_bytes = b"".join(resp_body)
            body_str = body_bytes.decode()

            if body_str:
                data = json.loads(body_str)
                # 如果已经是标准格式直接返回
                if isinstance(data, dict) and "code" in data:
                    return JSONResponse(
                        content=data,
                        status_code=response.status_code,
                        headers=safe_headers
                    )
                # 否则包装错误信息
                return JSONResponse(
                    content=wrap_error_response(response.status_code, data.get("detail", str(data))),
                    status_code=response.status_code,
                    headers=safe_headers
                )
        except Exception:
            return JSONResponse(
                content=wrap_error_response(response.status_code, "服务器内部错误"),
                status_code=response.status_code,
                headers=safe_headers
            )
        

    # 2xx 响应：包装成统一成功格式
    try:
        resp_body = [section async for section in response.body_iterator]
        body_bytes = b"".join(resp_body)
        body_str = body_bytes.decode()

        if not body_str:
            return JSONResponse(content='', status_code=response.status_code, headers=safe_headers)

        data = json.loads(body_str)

        # access_token 代表是login接口返回
        if isinstance(data, dict) and "access_token" in data:
            return JSONResponse(content=data, status_code=response.status_code, headers=safe_headers)

        wrapped = {"code": 200, "data": data, "message": "success"}
        return JSONResponse(content=wrapped, status_code=response.status_code, headers=safe_headers)
    except Exception:
        return JSONResponse(
            content=wrap_error_response(response.status_code, "服务器内部错误"),
            status_code=response.status_code,
            headers=safe_headers
        )
