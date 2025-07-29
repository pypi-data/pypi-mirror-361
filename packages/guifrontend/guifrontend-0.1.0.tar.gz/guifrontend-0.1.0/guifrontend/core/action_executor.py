import asyncio
import pyautogui
from utils.logger import get_logger


class ActionExecutor:
    """动作执行器"""
    
    def __init__(self, ws_client=None):
        self.logger = get_logger("ActionExecutor", ws_client)
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.5
    
    async def execute_action(self, pyautogui_code: str) -> bool:
        """执行PyAutoGUI代码"""
        if not pyautogui_code:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._execute_code, pyautogui_code)
            self.logger.info("代码执行完成", {"code": pyautogui_code})
            return True
        except Exception as e:
            self.logger.error(f"执行失败: {e}", {"code": pyautogui_code})
            return False
    
    def _execute_code(self, code: str):
        """执行代码"""
        exec(code, {"pyautogui": pyautogui, "time": __import__('time')}) 