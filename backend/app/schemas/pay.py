from pydantic import BaseModel
from typing import Optional

class PayRequest(BaseModel):
    """发起支付"""
    order_id: int


class PayResponse(BaseModel):
    """返回支付信息"""
    order_id: int
    pay_url: str          # 模拟支付链接
    qr_code: str           # 模拟二维码内容
    amount: str


class PayCallbackRequest(BaseModel):
    """支付回调"""
    order_id: int
    pay_status: str        # "success" | "failed"
    transaction_id: Optional[str] = None


class PayCallbackResponse(BaseModel):
    """回调响应"""
    code: int
    message: str
