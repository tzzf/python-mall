"""
ProductImageModule — Deep Module for async product image generation.

接口（唯一公开方法）：
    trigger_or_skip(product_id) -> None

设计原则：
- 幂等：已有 image 则跳过
- 下载到本地再存路径，绕过第三方 URL 有效期限制
- 调用方只传 product_id，不感知生成/下载/存储细节
- 失败打印日志，不抛异常，不阻塞调度器
"""

import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.adapters.image_generation import ImageGenerationAdapter
from app.adapters.image_generation_minimax import MiniMaxImageAdapter
from app.adapters.image_storage import LocalStorageAdapter
from app.core.config import settings
from app.repository.product_repo import ProductRepository

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)

class ProductImageModule:
    """
    异步生成产品图片的 Deep Module。

    实现细节（对调用方透明）：
    - 自动选择 adapter（MiniMax / Fake）
    - 构建英文 prompt（产品名 + 描述）
    - 幂等：已有图片不重复生成
    - 下载图片到本地，存相对路径到 DB
    - 更新失败只打日志
    """

    def __init__(
        self,
        adapter: ImageGenerationAdapter | None = None,
        storage: LocalStorageAdapter | None = None,
    ):
        # 不再在构造时传入 db，trigger_or_skip 内部自己创建 session
        self._adapter = adapter or MiniMaxImageAdapter()
        self._storage = storage or LocalStorageAdapter()

    async def trigger_or_skip(self, product_id: int) -> None:
        """
        触发图片生成（如果该产品还没有图片的话）。

        幂等：调用多次和调用一次效果相同。
        失败安全：只记录错误，不向调用方抛异常。

        注意：内部自己创建 db session，不依赖调用方传入的 session。
        这是为了支持 asyncio.create_task 后台调用——调用方的 session
        可能在任务执行前就已经关闭了。
        """
        from app.core.database import AsyncSessionLocal

        async with AsyncSessionLocal() as db:
            repo = ProductRepository(db)

            product = await repo.get_by_id(product_id)
            if not product:
                logger.warning(
                    f"[ProductImageModule] product {product_id} not found, skipping"
                )
                return

            if product.image:
                logger.info(
                    f"[ProductImageModule] product {product_id} already has image, skipping"
                )
                return

            prompt = self._build_prompt(product.name, product.description or "")
            logger.info(
                f"[ProductImageModule] generating image for product {product_id}: {prompt[:60]}"
            )

            try:
                urls = await self._adapter.generate(prompt, n=1)
            except Exception as e:
                logger.error(
                    f"[ProductImageModule] image generation failed for product {product_id}: {e}",
                    exc_info=True,
                )
                return

            if not urls:
                logger.error(
                    f"[ProductImageModule] no image URLs returned for product {product_id}"
                )
                return

            # 下载到本地，绕过第三方 URL 有效期限制
            try:
                local_path = await self._storage.download_and_save(urls[0], product_id)
                await repo.update_image(product_id, local_path)
                logger.info(
                    f"[ProductImageModule] image saved for product {product_id}: {local_path}"
                )
            except Exception as e:
                logger.error(
                    f"[ProductImageModule] failed to download/save image for product {product_id}: {e}",
                    exc_info=True,
                )

    @staticmethod
    def _build_prompt(name: str, description: str) -> str:
        """
        构建英文 prompt，驱动图片生成。

        策略：产品名居前，描述补充细节，结尾固定风格引导词。
        """
        parts = [f"Product name: {name}"]
        if description:
            # 取前 200 字符，避免 prompt 过长（MiniMax 上限 1500 字符）
            parts.append(f"Description: {description[:200]}")
        parts.append(
            "Professional product photography, clean white background, "
            "high detail, commercial quality"
        )
        return " | ".join(parts)
