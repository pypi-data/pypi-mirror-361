import asyncio
import json
import websockets


class WebSocketClient:
    """WebSocket客户端 (无日志)"""
    
    def __init__(self, host: str, port: int, frontend_id: str):
        # 处理host中可能包含协议的情况
        if host.startswith('https://'):
            # HTTPS对应WSS协议
            clean_host = host.replace('https://', '')
            self.url = f"wss://{clean_host}:{port}/ws/{frontend_id}"
        elif host.startswith('http://'):
            # HTTP对应WS协议
            clean_host = host.replace('http://', '')
            self.url = f"ws://{clean_host}:{port}/ws/{frontend_id}"
        else:
            # 默认使用ws协议
            self.url = f"ws://{host}:{port}/ws/{frontend_id}"
        
        self.frontend_id = frontend_id
        self.websocket = None
        self.is_connected = False
        print(f"WebSocket URL: {self.url}")
        self.message_handlers = {}
    
    def register_handler(self, message_type: str, handler):
        """注册消息处理器"""
        self.message_handlers[message_type] = handler
    
    async def connect(self) -> bool:
        """连接后端"""
        try:
            self.websocket = await websockets.connect(self.url)
            self.is_connected = True
            print("WebSocket: 连接成功")
            return True
        except Exception as e:
            print(f"WebSocket: 连接失败: {e}")
            return False
    
    async def send_screenshot(self, screenshot_base64: str) -> bool:
        """发送截图"""
        if not self.is_connected:
            return False
        
        try:
            message = {"type": "screenshot", "screenshot": screenshot_base64}
            await self.websocket.send(json.dumps(message))
            return True
        except Exception:
            self.is_connected = False
            return False
    
    async def send_json(self, data: dict) -> bool:
        """发送JSON数据"""
        if not self.is_connected:
            return False
        
        try:
            await self.websocket.send(json.dumps(data))
            return True
        except Exception:
            self.is_connected = False
            return False
    
    async def listen_for_messages(self):
        """监听消息"""
        while self.is_connected and self.websocket:
            try:
                message_json = await self.websocket.recv()
                message = json.loads(message_json)
                
                message_type = message.get('type')
                if message_type in self.message_handlers:
                    handler = self.message_handlers[message_type]
                    if asyncio.iscoroutinefunction(handler):
                        await handler(message)
                    else:
                        handler(message)
            except websockets.exceptions.ConnectionClosed:
                self.is_connected = False
                break
            except Exception:
                break 