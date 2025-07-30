#!/usr/bin/env python3
"""
AGI-MAT Agent CLI 启动脚本
支持配置文件路径和环境变量配置
"""

import argparse
import os
from typing import Optional
import sys
import uvicorn
import subprocess
from lib.env_loader import load_agimat_env

load_agimat_env()


def ensure_user_config_dir():
    """确保用户配置目录存在"""
    user_config_dir = os.path.join(os.path.expanduser("~"), ".agimat")
    os.makedirs(user_config_dir, exist_ok=True)
    return user_config_dir


def create_default_env_file():
    """创建默认的 .env 文件"""
    user_config_dir = ensure_user_config_dir()
    env_file_path = os.path.join(user_config_dir, "env")

    if not os.path.exists(env_file_path):
        default_env_content = """# AGI-MAT Agent 环境变量配置
# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1

# Google AI 配置
GOOGLE_API_KEY=your_google_api_key_here

# Anthropic 配置
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# LangSmith 配置 (可选)
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=agimat-agent

# 数据库配置
MONGODB_URI=mongodb://localhost:27017/agimat

# 服务器配置
HOST=127.0.0.1
PORT=8000
UI_PORT=8501

# 日志配置
LOG_LEVEL=INFO
"""
        with open(env_file_path, "w", encoding="utf-8") as f:
            f.write(default_env_content)
        print(f"📝 创建默认环境变量文件: {env_file_path}")

    return env_file_path


def find_config_file(config_path: Optional[str] = None) -> str:
    """查找配置文件路径"""
    if config_path and os.path.exists(config_path):
        return config_path

    # 查找可能的配置文件位置
    possible_paths = [
        os.path.join(os.path.expanduser("~"), ".agimat", "conf.yaml"),
        os.path.join(os.path.expanduser("~"), ".agimat", "config.yaml"),
        os.path.join(os.path.expanduser("~"), ".agimat", "conf.yml"),
        os.path.join(os.path.expanduser("~"), ".agimat", "config.yml"),
        "conf.yaml",
        "config.yaml",
        "conf.yml",
        "config.yml",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果找不到配置文件，创建默认配置
    user_config_dir = ensure_user_config_dir()
    default_config = """# AGI-MAT Agent 默认配置文件
AGIMAT_CONFIG:
  base_url: http://localhost:8000

LLM_MODEL_CONFIG:
  model_name: gpt-3.5-turbo
  temperature: 0.7
  max_tokens: 1000

MCP_CONFIG:
  enabled: true
  config_path: ~/.agimat/mcp.json
"""

    # 创建默认配置文件
    default_config_path = os.path.join(user_config_dir, "conf.yaml")
    with open(default_config_path, "w", encoding="utf-8") as f:
        f.write(default_config)

    print(f"📝 创建默认配置文件: {default_config_path}")
    return default_config_path


def find_mcp_config_file(mcp_config_path: Optional[str] = None) -> str:
    """查找MCP配置文件路径"""
    if mcp_config_path and os.path.exists(mcp_config_path):
        return mcp_config_path

    # 查找可能的MCP配置文件位置
    possible_paths = [
        os.path.join(os.path.expanduser("~"), ".agimat", "mcp.json"),
        "core/apps/mcp/mcp_tool.json",
        "mcp_tool.json",
        "mcp_config.json",
    ]

    for path in possible_paths:
        if os.path.exists(path):
            return path

    # 如果找不到MCP配置文件，创建默认配置
    user_config_dir = ensure_user_config_dir()
    default_mcp_config = {
        "mcpServers": {
            "amap-maps-streamableHTTP": {
                "url": "https://mcp.amap.com/mcp?key=d1843b64de7325315ea9abc55fcb48a7",
                "description": "高德地图MCP服务",
                "transport": "streamableHttp",
                "enabled": True,
            },
            "weather": {
                "url": "https://api.weather.com/mcp",
                "description": "天气服务MCP",
                "transport": "streamableHttp",
                "headers": {"Authorization": "Bearer YOUR_API_KEY"},
                "enabled": False,
            },
        }
    }

    import json

    default_mcp_config_path = os.path.join(user_config_dir, "mcp.json")
    with open(default_mcp_config_path, "w", encoding="utf-8") as f:
        json.dump(default_mcp_config, f, ensure_ascii=False, indent=2)

    print(f"📝 创建默认MCP配置文件: {default_mcp_config_path}")
    return default_mcp_config_path


def start_server(
    config_path: Optional[str] = None, host: str = "127.0.0.1", port: int = 8000
):
    """启动后端服务器"""
    # 设置配置文件路径
    config_file = find_config_file(config_path)
    os.environ["AGIMAT_CONFIG_PATH"] = config_file

    # 设置MCP配置文件路径
    mcp_config_file = find_mcp_config_file()

    print("🚀 启动AGI-MAT Agent服务器...")
    print(f"📁 配置文件: {config_file}")
    print(f"🔧 MCP配置: {mcp_config_file}")
    print(f"🌐 服务地址: http://{host}:{port}")

    # 延迟导入，避免在配置初始化前就导入其他模块
    try:
        from main import create_app
    except ImportError:
        print("❌ 无法导入主应用模块")
        print("💡 请确保在正确的目录中运行此命令")
        return

    # 添加项目根目录到Python路径
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    app = create_app()
    uvicorn.run(app, host=host, port=port)


def start_ui(config_path: Optional[str] = None, port: int = 8501):
    """启动前端UI"""
    # 设置配置文件路径
    config_file = find_config_file(config_path)
    os.environ["AGIMAT_CONFIG_PATH"] = config_file

    print("🎨 启动AGI-MAT Agent UI...")
    print(f"📁 配置文件: {config_file}")
    print(f"🌐 UI地址: http://localhost:{port}")

    # 启动Streamlit

    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "ui/ui.py",
        "--server.port",
        str(port),
        "--server.address",
        "127.0.0.1",
    ]

    subprocess.run(cmd)


def open_config_dir(editor: Optional[str] = None):
    """打开配置目录"""
    user_config_dir = ensure_user_config_dir()

    print(f"📁 配置目录: {user_config_dir}")

    if editor:
        # 使用指定的编辑器打开目录
        if editor == "code":
            cmd = ["code", user_config_dir]
        elif editor == "vim":
            cmd = ["vim", user_config_dir]
        elif editor == "nano":
            cmd = ["nano", user_config_dir]
        else:
            # 尝试直接使用编辑器命令
            cmd = [editor, user_config_dir]

        try:
            subprocess.run(cmd)
            print(f"✅ 已使用 {editor} 打开配置目录")
        except FileNotFoundError:
            print(f"❌ 找不到编辑器: {editor}")
            print("💡 请确保编辑器已安装并在PATH中")
    else:
        # 使用系统默认方式打开目录
        if sys.platform == "darwin":  # macOS
            cmd = ["open", user_config_dir]
        elif sys.platform == "win32":  # Windows
            cmd = ["explorer", user_config_dir]
        else:  # Linux
            cmd = ["xdg-open", user_config_dir]

        try:
            subprocess.run(cmd)
            print("✅ 已打开配置目录")
        except FileNotFoundError:
            print("❌ 无法打开配置目录")
            print(f"💡 请手动打开: {user_config_dir}")


def main():
    """主函数"""
    # 初始化用户配置目录和文件
    ensure_user_config_dir()
    env_file_path = create_default_env_file()

    # 设置环境变量，让 load_dotenv 能找到 ~/.agimat/.env
    os.environ["DOTENV_PATH"] = env_file_path

    parser = argparse.ArgumentParser(
        description="AGI-MAT Agent 管理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  agimat server --port 8000          # 启动后端服务器
  agimat ui --port 8501              # 启动前端UI
  agimat config                      # 打开配置目录
  agimat config --editor code        # 使用VS Code打开配置目录
  agimat server --config my_conf.yaml # 使用自定义配置文件
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # 配置命令
    config_parser = subparsers.add_parser("config", help="打开配置目录")
    config_parser.add_argument("--editor", help="指定编辑器 (如: code, vim, nano)")

    # 服务器命令
    server_parser = subparsers.add_parser("server", help="启动后端服务器")
    server_parser.add_argument("--config", help="配置文件路径")
    server_parser.add_argument("--host", default="127.0.0.1", help="服务器地址")
    server_parser.add_argument("--port", type=int, default=8000, help="服务器端口")

    # UI命令
    ui_parser = subparsers.add_parser("ui", help="启动前端UI")
    ui_parser.add_argument("--config", help="配置文件路径")
    ui_parser.add_argument("--port", type=int, default=8501, help="UI端口")

    args = parser.parse_args()

    if args.command == "server":
        start_server(args.config, args.host, args.port)
    elif args.command == "ui":
        start_ui(args.config, args.port)
    elif args.command == "config":
        open_config_dir(args.editor)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
