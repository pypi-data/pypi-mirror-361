import logging
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool

logger = logging.getLogger(__name__)

# 全局工具注册表
_tools_registry: Dict[str, BaseTool] = {}

def register_tool(name: str):
    """注册 @tool 装饰的函数"""
    def decorator(tool_func):
        _tools_registry[name] = tool_func
        return tool_func
    return decorator

def register_prebuilt_tool(name: str):
    """注册工厂函数"""
    def decorator(factory_func):
        _tools_registry[name] = factory_func()
        return factory_func
    return decorator
    

def get_all_tools() -> Dict[str, BaseTool]:
    """获取所有已注册的工具"""
    return _tools_registry.copy()

class LocalToolProvider:
    """
    本地工具节点，支持工具加载和管理
    """
    
    def __init__(self, tool_configs: List[Dict[str, Any]] = None):
        """
        初始化工具节点
        """
        self.tool_configs = tool_configs or []
        self.tools: dict[str, BaseTool] = {}
        if self.tool_configs:
            self._load_tools()
        # 从注册表加载工具
        self._load_registered_tools()
    
    def _load_registered_tools(self):
        """从注册表加载工具"""
        from . import my_tools  # 触发工具注册
        
        registered_tools = _tools_registry.copy()
        for name, tool in registered_tools.items():
            self.tools[name] = tool
            logger.info(f"从注册表加载工具: {name}")
    
    def get_tools(self) -> List[BaseTool]:
        """获取所有已加载的工具"""
        return self.tools
    
    def get_tool(self, name: str) -> BaseTool:
        """获取LangGraph的ToolNode实例"""
        if not self.tools:
            raise NotImplementedError("没有可用的工具")
        
        if name not in self.tools:
            raise NotImplementedError(f"工具 {name} 不存在")
        
        return self.tools[name]
    
    def list_tool_names(self) -> List[str]:
        """列出所有工具名称"""
        return list(self.tools.keys())
    
    def add_tool(self, name: str, tool: BaseTool):
        """
        添加工具实例到工具列表
        
        Args:
            tool: 工具实例
        """
        if name not in self.tools:
            self.tools[name] = tool
            logger.info(f"添加工具: {name}")
        else:
            logger.warning(f"工具 {name} 已经存在，跳过添加")

global_tool_provider = LocalToolProvider()

if __name__ == "__main__":
    from core.apps.tools.tools import global_tool_provider
    from langchain_core.messages import AIMessage
    from core.apps.tools.my_tools import *
    
    # 查看已注册的工具
    print("已注册的工具:", global_tool_provider.list_tool_names())
    
    # 方法1: 直接获取工具并调用
    tool_node = global_tool_provider.get_tool("calculate_sum")
    if tool_node:
        try:
            # 从ToolNode中获取实际的工具
            result = tool_node.invoke(AIMessage(content="calculate_sum(1, 2)"))
            print(f"calculate_sum(1, 2) = {result}")
        except Exception as e:
            print(f"调用工具时出错: {e}")
    else:
        print("工具 'calculate_sum' 不存在")
    
    # 方法4: 获取所有工具
    all_tools = global_tool_provider.get_tools()
    print(f"总共有 {len(all_tools)} 个工具")