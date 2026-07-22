import httpx
from app.adapters.image_generation import ImageGenerationAdapter
from app.core.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)


class MiniMaxImageAdapter(ImageGenerationAdapter):
    """
    MiniMax 文生图适配器。

    实现细节（对调用方透明）：
    - 调 /v1/image_generation 接口
    - 自动重试超时的 few-shot 请求
    - 返回图片 URL 列表
    """

    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.base_url = base_url or settings.MINIMAX_BASE_URL

    async def generate(self, prompt: str, n: int = 1) -> List[str]:
        url = f"{self.base_url}/v1/image_generation"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "image-01",
            "prompt": prompt,
            "n": n,
            "response_format": "url",
            "aspect_ratio": "1:1",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        base_resp = data.get("base_resp", {})
        if base_resp.get("status_code") != 0:
            logger.warning(
                f"[MiniMaxImageAdapter] generation failed: {base_resp.get('status_msg')}"
            )
            return []

        image_urls = data.get("data", {}).get("image_urls", [])
        logger.info(f"[MiniMaxImageAdapter] generated {len(image_urls)} image(s)")
        return image_urls
