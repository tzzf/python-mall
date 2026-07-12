from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_current_v1_user
from app.service.pay_service import PayService
from app.service.order_service import OrderService
from app.repository.order_repo import OrderRepository
from app.repository.product_repo import ProductRepository
from app.repository.cart_repo import CartRepository
from app.core.database import get_db
from app.schemas.pay import PayRequest, PayResponse, PayCallbackRequest
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/pay", tags=["用户端-支付"])


def get_pay_service(db: AsyncSession = Depends(get_db)):
    order_repo = OrderRepository(db)
    product_repo = ProductRepository(db)
    cart_repo = CartRepository(db)
    order_service = OrderService(db, order_repo, product_repo, cart_repo)
    return PayService(order_service)

@router.post("/callback")
async def pay_callback(
    callback: PayCallbackRequest,
    current_user=Depends(get_current_v1_user),
    svc: PayService = Depends(get_pay_service),
):
    """
    支付回调（模拟）
    前端模拟支付成功后调用此接口
    """
    try:
        result = await svc.pay_callback(
            user_id=current_user.id,
            order_id=callback.order_id,
            pay_status=callback.pay_status,
            transaction_id=callback.transaction_id,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{order_id}", response_model=PayResponse)
async def create_pay(
    order_id: int,
    current_user=Depends(get_current_v1_user),
    svc: PayService = Depends(get_pay_service),
):
    """
    发起支付
    返回模拟支付链接
    """
    try:
        result = await svc.create_pay(current_user.id, order_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


