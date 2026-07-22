from app.repository.cart_repo import CartRepository
from app.repository.product_repo import ProductRepository
from app.schemas.cart import CartItemAdd, CartItemUpdate, CartItemResponse, CartResponse
from typing import List, Dict

class CartService:
    def __init__(self, cart_repo: CartRepository, product_repo: ProductRepository):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    async def add_item(self, user_id: int, item_in: CartItemAdd) -> Dict:
        product = await self.product_repo.get_by_id(item_in.product_id)
        if not product:
            raise ValueError("商品不存在")
        if product.stock < item_in.quantity:
            raise ValueError("库存不足")
        await self.cart_repo.add_item(user_id, item_in.product_id, item_in.quantity)
        return {"message": "添加成功"}

    async def update_item(self, user_id: int, product_id: int, quantity: int):
        if quantity <= 0:
            await self.cart_repo.remove_item(user_id, product_id)
            return {"message": "已删除"}
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError("商品不存在")
        if product.stock < quantity:
            raise ValueError("库存不足")
        await self.cart_repo.set_item(user_id, product_id, quantity)
        return {"message": "更新成功"}

    async def remove_item(self, user_id: int, product_id: int):
        await self.cart_repo.remove_item(user_id, product_id)
        return {"message": "删除成功"}

    async def get_cart(self, user_id: int) -> CartResponse:
        cart_data = await self.cart_repo.get_cart(user_id)
        items = []
        total_count = 0
        for product_id_str, qty_str in cart_data.items():
            product_id = int(product_id_str)
            quantity = int(qty_str)
            product = await self.product_repo.get_by_id(product_id)
            items.append(CartItemResponse(
                product_id=product_id,
                quantity=quantity,
                product_name=product.name if product else "已删除",
                price=str(product.price) if product else "0",
                image=product.image if product else None,
            ))
            total_count += quantity
        return CartResponse(user_id=user_id, items=items, total_count=total_count)

    async def clear_cart(self, user_id: int):
        await self.cart_repo.clear_cart(user_id)
        return {"message": "清空成功"}
