import argparse
import asyncio
import sys
from pathlib import Path
import shutil
try:
    import importlib.resources as pkg_resources
except ImportError:
    # Fallback for Python < 3.7
    import importlib_resources as pkg_resources

from .core.frontend_controller import FrontendController

def get_config_path(config_arg=None) -> Path:
    """
    智能地查找或创建配置文件。
    查找顺序:
    1. --config 参数指定的路径
    2. 当前工作目录下的 'config.yaml'
    3. 用户配置目录下的 '~/.config/guifrontend/config.yaml'
    如果都找不到，则从包内复制默认配置到用户配置目录。
    """
    # 1. 检查 --config 参数
    if config_arg:
        path = Path(config_arg)
        if path.exists():
            return path
        else:
            print(f"错误: 配置文件 '{path}' 不存在。")
            sys.exit(1)

    # 2. 检查当前工作目录
    local_config = Path.cwd() / "config.yaml"
    if local_config.exists():
        print(f"检测到并使用当前目录的配置文件: {local_config}")
        return local_config

    # 3. 检查用户配置目录
    user_config_dir = Path.home() / ".config" / "guifrontend"
    user_config_path = user_config_dir / "config.yaml"
    if user_config_path.exists():
        print(f"检测到并使用用户配置: {user_config_path}")
        return user_config_path

    # 4. 创建默认配置
    print("未找到现有配置文件。")
    try:
        user_config_dir.mkdir(parents=True, exist_ok=True)
        with pkg_resources.path('guifrontend.resources', 'config.yaml') as default_config:
            shutil.copy(default_config, user_config_path)
        print(f"已创建默认配置文件于: {user_config_path}")
        print("请根据您的环境修改此文件, 然后重新运行 'gui' 命令。")
        sys.exit(0)
    except Exception as e:
        print(f"错误: 无法创建默认配置文件: {e}")
        sys.exit(1)

async def main_async():
    """异步主函数"""
    parser = argparse.ArgumentParser(
        description='GUI-CS-Automation 前端代理',
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        '--config', 
        type=str, 
        help="""配置文件路径。
如果未指定, 将按以下顺序查找:
1. ./config.yaml
2. ~/.config/guifrontend/config.yaml
"""
    )
    
    args = parser.parse_args()
    
    config_path = get_config_path(args.config)
    
    controller = FrontendController(config_path)
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