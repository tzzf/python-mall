from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.models.product import Product, Category
from typing import Optional, List

class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def reduce_stock(self, product_id: int, quantity: int):
        product = await self.get_by_id(product_id)
        if product:
            product.stock -= quantity
            await self.db.commit()

    async def get_by_id(self, product_id: int) -> Optional[Product]:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await self.db.execute(
            select(Product).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_spu_count(self) -> int:
        result = await self.db.execute(
            select(func.count()).select_from(Product)
        )
        return result.scalar_one()

    async def create(self, product_in) -> Product:
        product = Product(**product_in.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, product: Product, product_in) -> Product:
        for field, value in product_in.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, product: Product):
        await self.db.delete(product)
        await self.db.commit()

    async def update_image(self, product_id: int, image_url: str) -> bool:
        """原子更新产品的 image 字段。"""
        result = await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(image=image_url)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def increase_stock(self, product_id: int, quantity: int) -> bool:
        """增加库存（还原）"""
        result = await self.db.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(stock=Product.stock + quantity)
        )
        await self.db.flush()
        return result.rowcount > 0

class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Optional[Category]:
        result = await self.db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Category]:
        result = await self.db.execute(select(Category))
        return list(result.scalars().all())

    async def create(self, category_in) -> Category:
        category = Category(**category_in.model_dump())
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)
        return category
    
    async def update(self, category_id: int, **kwargs) -> Category:
        await self.db.execute(
            update(Category).where(Category.id == category_id).values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(category_id)


    async def delete(self, category_id: int):
        await self.db.execute(
            delete(Category).where(Category.id == category_id)
        )
        await self.db.flush()


