import base64
import io
from PIL import Image, ImageGrab
from utils.logger import get_logger


class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, ws_client=None):
        self.logger = get_logger("ScreenshotManager", ws_client)
    
    def capture_screen(self) -> str:
        """截取屏幕并返回base64编码"""
        try:
            screenshot = ImageGrab.grab()
            buffer = io.BytesIO()
            screenshot.save(buffer, format='JPEG', quality=85)
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            self.logger.error(f"截图失败: {e}")
            return None 