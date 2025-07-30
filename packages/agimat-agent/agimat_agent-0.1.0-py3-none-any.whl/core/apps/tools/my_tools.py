from langchain_core.tools import tool, BaseTool
from core.apps.tools.tools import register_tool, register_prebuilt_tool
import datetime
import random
import os

@register_tool("calculate_sum")
@tool()
def calculate_sum(a: int, b: int) -> int:
    """计算两个数字的和"""
    return a + b

@register_tool("get_current_time")
@tool
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@register_tool("reverse_string")
@tool
def reverse_string(text: str) -> str:
    """反转字符串"""
    return text[::-1]

@register_tool("get_random_number")
@tool
def get_random_number(min_val: int = 1, max_val: int = 100) -> int:
    """生成指定范围内的随机数"""
    return random.randint(min_val, max_val)

@register_prebuilt_tool("tavily_search")
def tavily_search() -> BaseTool:
    """Tavily搜索工具"""
    from langchain_tavily import TavilySearch
    
    # 从环境变量获取 API key（支持 .env 文件）
    api_key = os.getenv("TAVILY_API_KEY")
    
    if not api_key:
        raise ValueError(
            "未找到 Tavily API key。请通过以下方式之一设置：\n"
            "1. 在项目根目录创建 .env 文件，添加：TAVILY_API_KEY=your_api_key\n"
            "2. 设置系统环境变量：export TAVILY_API_KEY=your_api_key\n"
            "3. 在启动时设置：TAVILY_API_KEY=your_api_key python main.py"
        )
    
    return TavilySearch(
        max_results=2,
        tavily_api_key=api_key
    )


if __name__ == "__main__":
    print("随机数：", get_random_number.invoke({"min_val": 1, "max_val": 100}))
    print("当前时间：", get_current_time.invoke({}))
    print("反转字符串：", reverse_string.invoke({"text": "Hello, World!"}))
    print("计算和：", calculate_sum.invoke({"a": 1, "b": 2}))