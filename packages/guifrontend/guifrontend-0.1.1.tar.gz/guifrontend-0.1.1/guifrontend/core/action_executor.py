import asyncio
import pyautogui


class ActionExecutor:
    """动作执行器 (无日志)"""
    
    def __init__(self):
        pyautogui.FAILSAFE = False
        pyautogui.PAUSE = 0.5
    
    async def execute_action(self, pyautogui_code: str) -> bool:
        """执行PyAutoGUI代码"""
        if not pyautogui_code:
            return False
        
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self._execute_code, pyautogui_code)
            print(f"动作执行完成: {pyautogui_code}")
            return True
        except Exception as e:
            print(f"错误: 动作执行失败: {e} (代码: {pyautogui_code})")
            return False
    
    def _execute_code(self, code: str):
        """执行代码"""
        exec(code, {"pyautogui": pyautogui, "time": __import__('time')})