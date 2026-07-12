import redis.asyncio as redis
import json
from typing import Optional, Dict, List

CART_KEY_PREFIX = "cart:user:"
CART_TTL = 7 * 24 * 3600  # 7天秒数


class CartRepository:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    def _cart_key(self, user_id: int) -> str:
        return f"{CART_KEY_PREFIX}{user_id}"

    async def add_item(self, user_id: int, product_id: int, quantity: int):
        """添加商品，如果已存在则叠加数量"""
        key = self._cart_key(user_id)
        existing = await self.redis.hget(key, str(product_id))
        if existing:
            new_qty = int(existing) + quantity
        else:
            new_qty = quantity
        await self.redis.hset(key, str(product_id), str(new_qty))
        await self.redis.expire(key, CART_TTL)

    async def set_item(self, user_id: int, product_id: int, quantity: int):
        """直接设置商品数量"""
        key = self._cart_key(user_id)
        if quantity <= 0:
            await self.redis.hdel(key, str(product_id))
        else:
            await self.redis.hset(key, str(product_id), str(quantity))
            await self.redis.expire(key, CART_TTL)

    async def remove_item(self, user_id: int, product_id: int):
        key = self._cart_key(user_id)
        await self.redis.hdel(key, str(product_id))

    async def get_cart(self, user_id: int) -> Dict[str, str]:
        """获取购物车所有商品和数量"""
        key = self._cart_key(user_id)
        cart = await self.redis.hgetall(key)
        # async redis 返回 bytes，转成 str
        return {k: v for k, v in cart.items()}

    async def clear_cart(self, user_id: int):
        key = self._cart_key(user_id)
        await self.redis.delete(key)
