import argparse
import asyncio
import sys
from pathlib import Path
import shutil

from .core.frontend_controller import FrontendController

async def main_async():
    """异步主函数"""
    parser = argparse.ArgumentParser(
        description='GUI-CS-Automation 前端代理',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Backend settings
    parser.add_argument('--host', type=str, default="https://u468127-bbee-6742ea39.westx.seetacloud.com", help='后端WebSocket服务器的主机名或IP地址')
    parser.add_argument('--port', type=int, default=8443, help='后端WebSocket服务器的端口')

    # Frontend settings
    parser.add_argument('--id', type=str, default="", help='向后端注册的唯一ID。如果留空，将自动生成一个。')
    parser.add_argument('--screenshot_interval', type=float, default=3.0, help='执行动作后等待多少秒再发送截图')
    parser.add_argument('--mode', type=str, default='automatic', choices=['automatic', 'predefined'], help="任务模式 ('automatic' 或 'predefined')")

    args = parser.parse_args()
    
    controller = FrontendController(
        host=args.host,
        port=args.port,
        frontend_id=args.id,
        screenshot_interval=args.screenshot_interval,
        mode=args.mode
    )
    await controller.start()

def main():
    """同步主函数入口"""
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        print("\n程序被用户中断。")
    except Exception as e:
        print(f"\n程序发生未知错误: {e}")

if __name__ == "__main__":
    main() 