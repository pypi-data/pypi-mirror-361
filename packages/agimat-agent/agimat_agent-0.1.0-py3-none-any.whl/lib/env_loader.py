"""
环境变量加载器
统一处理 ~/.agimat/.env 文件的加载
"""

import os
from dotenv import load_dotenv


def load_agimat_env():
    """加载 AGI-MAT 环境变量文件"""
    # 优先从环境变量获取路径，否则使用默认的 ~/.agimat/env
    dotenv_path = os.environ.get(
        "DOTENV_PATH", os.path.join(os.path.expanduser("~"), ".agimat", "env")
    )

    # 如果文件存在则加载
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        print(f"📁 已加载环境变量文件: {dotenv_path}")
    else:
        print(f"⚠️  环境变量文件不存在: {dotenv_path}")
        # 尝试加载当前目录的 .env 文件作为备选
        load_dotenv()
