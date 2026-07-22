from abc import ABC, abstractmethod
from typing import List


class ImageGenerationAdapter(ABC):
    """
    图片生成适配器接口（Adapter at the seam）。

    实现类只需要覆盖 generate() 方法。
    调用方通过此接口注入实现，无需感知具体是 MiniMax / OpenAI / Fake。
    """

    @abstractmethod
    async def generate(self, prompt: str, n: int = 1) -> List[str]:
        """
        根据文本 prompt 生成图片。

        Args:
            prompt: 图片描述文本
            n: 生成数量，默认 1

        Returns:
            图片 URL 列表，长度为 n（如果部分失败，返回部分结果）
        """
        ...
