import base64
import io
from PIL import ImageGrab


class ScreenshotManager:
    """截图管理器（无日志依赖）"""

    def capture_screen(self) -> str:
        """截屏并返回 JPEG Base64 字符串；失败返回 None"""
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format="JPEG", quality=85)
            return base64.b64encode(buffer.getvalue()).decode("utf-8")
        except Exception as e:
            print(f"错误: 截图失败: {e}")
            return None