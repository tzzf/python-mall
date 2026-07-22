"""
LocalStorageAdapter — 将远程图片下载并持久化到本地文件系统。

Adapter 角色：对调用方屏蔽"下载 + 写文件 + 路径拼接"的细节。
"""

import httpx
import uuid
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class LocalStorageAdapter:
    """
    把远程图片 URL 下载到本地 static/images/ 目录。

    实现细节：
    - 生成 UUID 文件名，保证不冲突
    - 按产品 ID 创建子目录（便于后续清理/CDN）
    - 返回本地访问路径（相对 URL，非绝对路径）
    """

    def __init__(self, base_dir: str | None = None):
        """
        Args:
            base_dir: 图片存储根目录，默认 static/images/
        """
        self.base_dir = Path(base_dir or self._default_base_dir())

    def _default_base_dir(self) -> str:
        # 相对于 backend/app 的 static/images/
        return str(Path(__file__).parent.parent / "static" / "images")

    async def download_and_save(self, remote_url: str, product_id: int) -> str:
        """
        下载远程图片并保存到本地。

        Args:
            remote_url: MiniMax 返回的临时 URL
            product_id: 用于创建子目录

        Returns:
            本地相对路径，如 "images/products/123/abc-def.jpg"
        """
        product_dir = self.base_dir / "products" / str(product_id)
        product_dir.mkdir(parents=True, exist_ok=True)

        # 下载图片，确定扩展名
        ext = self._guess_ext(remote_url) or "jpg"
        filename = f"{uuid.uuid4().hex}.{ext}"
        file_path = product_dir / filename

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(remote_url)
            resp.raise_for_status()
            content = resp.content

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(
            f"[LocalStorageAdapter] saved image for product {product_id}: {file_path}"
        )

        # 返回相对路径，方便前端拼 BASE_URL 访问
        return f"images/products/{product_id}/{filename}"

    @staticmethod
    def _guess_ext(url: str) -> str | None:
        path = url.split("?")[0]
        _, ext = os.path.splitext(path)
        return ext.lstrip(".").lower() or None
