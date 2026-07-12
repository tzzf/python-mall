from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.product_repo import ProductRepository, CategoryRepository
from app.schemas.product import ProductCreate, ProductUpdate, CategoryUpdate
from app.models.product import Product, Category
from typing import Optional, List

class ProductService:
    def __init__(self, db: AsyncSession):
        self.repo = ProductRepository(db)

    async def get_product(self, product_id: int) -> Optional[Product]:
        return await self.repo.get_by_id(product_id)

    async def list_products(self, skip: int = 0, limit: int = 100):
        data = await self.repo.get_list(skip=skip, limit=limit)
        total = await self.repo.get_spu_count()
        return {
            "data": data,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    async def create_product(self, product_in: ProductCreate) -> Product:
        return await self.repo.create(product_in)

    async def update_product(self, product_id: int, product_in: ProductUpdate) -> Product:
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError("商品不存在")
        return await self.repo.update(product, product_in)

    async def delete_product(self, product_id: int):
        product = await self.repo.get_by_id(product_id)
        if not product:
            raise ValueError("商品不存在")
        await self.repo.delete(product)


class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = CategoryRepository(db)

    async def get_category(self, category_id: int) -> Optional[Category]:
        return await self.repo.get_by_id(category_id)

    async def list_categories(self) -> List[Category]:
        return await self.repo.get_all()

    async def create_category(self, category_in) -> Category:
        return await self.repo.create(category_in)
    
    async def update_category(self, category_id: int, category_in: CategoryUpdate) -> Category:
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("分类不存在")
        kwargs = category_in.model_dump(exclude_unset=True)
        data = await self.repo.update(category_id, **kwargs)
        await self.db.commit()
        return data


    async def delete_category(self, category_id: int):
        category = await self.repo.get_by_id(category_id)
        if not category:
            raise ValueError("分类不存在")
        await self.repo.delete(category_id)
