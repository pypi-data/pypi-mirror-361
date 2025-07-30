"""
环境变量加载器
统一处理环境变量文件的加载和合并
"""

import os
from dotenv import load_dotenv


def load_agimat_env():
    """加载 AGI-MAT 环境变量文件并合并当前目录的 .env"""
    # 优先从环境变量获取路径，否则使用默认的 ~/.agimat/env
    dotenv_path = os.getenv(
        "DOTENV_PATH", os.path.join(os.path.expanduser("~"), ".agimat", "env")
    )

    # 1. 首先加载当前目录的 .env 文件（优先级最低）
    load_dotenv()

    # 2. 加载用户指定的环境变量文件（优先级中等）
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"🔧 已加载用户环境变量文件: {dotenv_path}")
    else:
        print(f"⚠️  用户环境变量文件不存在: {dotenv_path}")

    # 3. 系统环境变量优先级最高（通过 os.environ 已经存在）
    print("🔧 系统环境变量已加载")
