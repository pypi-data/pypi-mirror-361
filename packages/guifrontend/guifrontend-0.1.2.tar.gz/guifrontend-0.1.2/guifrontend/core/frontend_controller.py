import asyncio
import yaml
from pathlib import Path
import subprocess
import uuid
import pyautogui

from .websocket_client import WebSocketClient
from .screenshot_manager import ScreenshotManager
from .action_executor import ActionExecutor

class FrontendController:
    """前端控制器 (无日志)"""
    
    def __init__(self, host: str = None, port: int = None, frontend_id: str = None, 
                 screenshot_interval: float = None, mode: str = None, config_path: str = None):
        
        if config_path:
            config = self._load_config(config_path)
            backend_config = config.get('backend', {})
            frontend_config = config.get('frontend', {})
            host = backend_config.get('host')
            port = backend_config.get('port')
            frontend_id = frontend_config.get('id')
            screenshot_interval = frontend_config.get('screenshot_interval', 3.0)
            mode = frontend_config.get('mode', 'automatic')

        # 从配置读取或生成ID
        if not frontend_id:
            frontend_id = f"frontend_{uuid.uuid4().hex[:8]}"
            print(f"前端ID未在配置中指定，已自动生成: {frontend_id}")
        self.frontend_id = frontend_id
        
        # 创建WebSocket客户端
        self.ws_client = WebSocketClient(host, port, self.frontend_id)
        
        # 检测环境信息
        self._detect_environment()
        
        # 初始化模块
        self.screenshot_manager = ScreenshotManager()
        self.action_executor = ActionExecutor()
        
        # 获取前端模式
        self.frontend_mode = mode
        
        # 注册消息处理器
        self.ws_client.register_handler('registration_success', self._handle_registration_success)
        self.ws_client.register_handler('execute_setup_commands', self._handle_execute_setup_commands)
        self.ws_client.register_handler('execute_action', self._handle_execute_action)
        self.ws_client.register_handler('task_start', self._handle_task_start)
        self.ws_client.register_handler('task_complete', self._handle_task_complete)
        self.ws_client.register_handler('task_failed', self._handle_task_failed)
        
        self.is_running = False
        self.screenshot_interval = screenshot_interval

    def _load_config(self, config_path: str) -> dict:
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            # 返回一个空的配置，让后续的默认值逻辑处理
            return {}
    
    def _detect_environment(self):
        """检测当前环境信息"""
        try:
            # 检测桌面环境
            desktop_env = subprocess.run(['echo', '$XDG_CURRENT_DESKTOP'], 
                                       capture_output=True, text=True, shell=True)
            if desktop_env.stdout.strip():
                print(f"桌面环境: {desktop_env.stdout.strip()}")
                
        except Exception as e:
            print(f"环境检测失败 (可忽略): {e}")
    
    async def start(self):
        """启动前端服务"""
        try:
            print(f"--- 前端服务启动 (ID: {self.frontend_id}, 模式: {self.frontend_mode}) ---")
            self.is_running = True
            
            # 连接后端
            if not await self.ws_client.connect():
                print("错误: 连接后端失败，程序退出。")
                return
            
            print("等待后端注册确认...")
            
            # 启动消息监听
            await self.ws_client.listen_for_messages()
            
        except Exception as e:
            print(f"错误: 前端服务发生致命异常: {e}")
        finally:
            self.is_running = False
            print("--- 前端服务已停止 ---")
    
    def _minimize_current_window(self):
        """最小化当前终端窗口"""
        try:
            print("正在执行快捷键最小化终端窗口...")
            pyautogui.hotkey('winleft', 'n')
            print("快捷键已执行。")
            return True, 1.0
        except Exception as e:
            print(f"警告: 执行最小化快捷键失败: {e}")
            print("请手动最小化终端窗口。")
            return False, 0

    async def _send_ready_signal(self):
        """向后端发送'准备就绪'信号以启动任务循环"""
        print("正在发送 'ready' 信号以启动任务循环...")
        await self.ws_client.send_json({
            "type": "request_new_task",
            "mode": self.frontend_mode
        })

    async def _handle_registration_success(self, message):
        """处理注册成功消息"""
        print(f"后端消息: {message.get('message')}")
        print("准备最小化当前终端窗口...")
        success, wait_time = self._minimize_current_window()
        
        if success:
            print(f"等待{wait_time}秒以确保UI稳定...")
            await asyncio.sleep(wait_time)
        else:
            print("自动最小化失败，等待5秒以便手动操作...")
            await asyncio.sleep(5)
        
        await self._send_ready_signal()

    async def _send_screenshot_to_backend(self):
        """捕获并发送截图到后端，用于任务步骤"""
        try:
            screenshot = self.screenshot_manager.capture_screen()
            if screenshot:
                await self.ws_client.send_screenshot(screenshot)
                return True
            else:
                print("错误: 截图捕获失败。")
                return False
        except Exception as e:
            print(f"错误: 发送截图时发生异常: {e}")
            return False

    async def _handle_execute_setup_commands(self, message):
        """处理并执行初始化指令"""
        commands = message.get('commands', [])
        print(f"收到初始化指令: {commands}")
        
        if not commands:
            print("无初始化指令，直接发送截图。")
        else:
            for cmd in commands:
                try:
                    print(f"正在执行: {cmd}")
                    # 使用 shell=True 来执行复杂的shell命令
                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    stdout, stderr = await process.communicate()
                    if process.returncode == 0:
                        print(f"指令 '{cmd}' 执行成功。")
                        if stdout: print(f"输出: {stdout.decode()}")
                    else:
                        print(f"指令 '{cmd}' 执行失败。返回码: {process.returncode}")
                        if stderr: print(f"错误信息: {stderr.decode()}")
                except Exception as e:
                    print(f"执行指令 '{cmd}' 时发生异常: {e}")
        
        print("所有初始化指令执行完毕，等待1秒...")
        await asyncio.sleep(1.0)
        
        print("正在发送'setup_complete'消息和截图...")
        screenshot = self.screenshot_manager.capture_screen()
        if screenshot:
            await self.ws_client.send_json({
                "type": "setup_complete",
                "screenshot": screenshot
            })
        else:
            print("错误: 截图失败，无法完成设置流程。")

    async def _handle_execute_action(self, message):
        """处理执行动作消息"""
        action = message.get('action', '')
        if not action:
            print("警告: 收到空的动作指令")
            return

        print(f"收到动作指令: {action}")
        success = await self.action_executor.execute_action(action)
        
        if success:
            print("动作执行成功。")
        else:
            print("错误: 动作执行失败。")
        
        print(f"等待 {self.screenshot_interval} 秒后发送截图...")
        await asyncio.sleep(self.screenshot_interval)
        await self._send_screenshot_to_backend()

    async def _handle_task_start(self, message):
        """处理任务开始消息"""
        print("-" * 20)
        print(f"任务开始: {message.get('task_instruction', '')}")
    
    async def _handle_task_complete(self, message):
        """处理任务完成消息"""
        print(f"任务已完成。观察: {message.get('observation', '')}")
        print("等待后端推送下一个任务...")
        print("-" * 20)
    
    async def _handle_task_failed(self, message):
        """处理任务失败消息"""
        print(f"任务失败: {message.get('message', '未知原因')}")
        print("等待后端推送下一个任务...")
        print("-" * 20) 