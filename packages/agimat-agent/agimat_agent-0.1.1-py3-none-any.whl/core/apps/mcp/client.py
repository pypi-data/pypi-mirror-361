"""
MCP Client 实现
加载mcp_loader.py中的配置文件到内存中
支持根据tools输入，加载mcp_tools, 用于后续agent调用
"""
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio
import logging
from typing import Dict, List, Any, Optional
from langchain_core.tools import BaseTool
from core.apps.mcp.loader import load_mcp_settings, load_mcp_settings_async, MCPConfigLoader
import os
import json
    

logger = logging.getLogger(__name__)


class MCPClientManager:
    """MCP Client 管理器"""
    
    def __init__(self, config_path: str = "core/apps/mcp/mcp_tool.json"):
        """
        初始化MCP客户端管理器
        
        Args:
            config_path: MCP配置文件路径
        """
        self.config_path = os.getenv("AGIMAT_MCP_CONFIG_PATH")
        if not self.config_path:
            self.config_path = config_path
        self.mcp_settings: Dict[str, Dict[str, Any]] = {}
        self.client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []
        self.initialized = False
        
        # 加载配置
        self._load_settings()
    
    def _load_settings(self) -> None:
        """加载MCP设置"""
        try:
            self.mcp_settings = load_mcp_settings(self.config_path)
            logger.info(f"成功加载MCP设置，共 {len(self.mcp_settings)} 个服务")
        except Exception as e:
            logger.error(f"加载MCP设置失败: {e}")
            self.mcp_settings = {}
    
    async def _load_settings_async(self) -> None:
        """异步加载MCP设置"""
        try:
            self.mcp_settings = await load_mcp_settings_async(self.config_path)
            logger.info(f"成功异步加载MCP设置，共 {len(self.mcp_settings)} 个服务")
        except Exception as e:
            logger.error(f"异步加载MCP设置失败: {e}")
            self.mcp_settings = {}
    
    def get_mcp_settings(self) -> Dict[str, Dict[str, Any]]:
        """获取MCP设置"""
        return self.mcp_settings
    
    def get_enabled_servers(self) -> List[str]:
        """获取启用的服务器列表"""
        return list(self.mcp_settings.keys())
    
    def create_client(self, server_names: Optional[List[str]] = None) -> MultiServerMCPClient:
        """
        创建MCP客户端
        
        Args:
            server_names: 要启用的服务器名称列表，如果为None则使用所有启用的服务器
        
        Returns:
            MultiServerMCPClient实例
        """
        if not self.mcp_settings:
            raise ValueError("MCP设置为空，请先加载配置")
        
        # 如果指定了服务器名称，只使用指定的服务器
        if server_names:
            filtered_settings = {
                name: config for name, config in self.mcp_settings.items()
                if name in server_names
            }
            if not filtered_settings:
                raise ValueError(f"指定的服务器名称 {server_names} 在配置中未找到")
            settings_to_use = filtered_settings
        else:
            settings_to_use = self.mcp_settings
        
        logger.info(f"创建MCP客户端，使用以下服务器配置: {json.dumps(settings_to_use, indent=2)}")
        
        try:
            self.client = MultiServerMCPClient(settings_to_use)
            return self.client
        except Exception as e:
            logger.error(f"创建MCP客户端失败: {str(e)}", exc_info=True)
            raise
    
    def initialize_client(self, server_names: Optional[List[str]] = None) -> None:
        """
        初始化MCP客户端
        
        Args:
            server_names: 要启用的服务器名称列表
        """
        if not self.initialized:
            # 创建客户端
            self.create_client(server_names)
            
            # 异步初始化（如果需要）
            if self.client:
                try:
                    # 这里可以添加客户端初始化逻辑
                    logger.info("MCP客户端初始化完成")
                    self.initialized = True
                except Exception as e:
                    logger.error(f"MCP客户端初始化失败: {e}")
                    raise
    
    async def get_tools(self, tools: Optional[List[str]] = None) -> List[BaseTool]:
        """
        获取MCP工具列表
        
        Args:
            server_names: 要获取工具的服务器名称列表    
        
        Returns:
            BaseTool列表
        """
        mcp_servers = set()
        for tool in tools:
            mcp_servers.add(tool.split('.')[0])
        
        if not self.initialized:
            self.initialize_client(list(mcp_servers))
        
        if not self.client:
            raise ValueError("MCP客户端未初始化")
        
        try:
            # 获取工具
            tools = await self.client.get_tools()
            self.tools = tools
            
            logger.info(f"成功获取 {len(tools)} 个MCP工具")
            return tools
        except Exception as e:
            logger.error(f"获取MCP工具失败，详细错误: {str(e)}", exc_info=True)
            raise
    
    def get_cached_tools(self) -> List[BaseTool]:
        """获取缓存的工具列表"""
        return self.tools
    
    async def refresh_tools(self, server_names: Optional[List[str]] = None) -> List[BaseTool]:
        """
        刷新工具列表
        
        Args:
            server_names: 要刷新工具的服务器名称列表
        
        Returns:
            刷新后的工具列表
        """
        # 重新加载配置
        await self._load_settings_async()
        
        # 重新初始化客户端
        self.initialized = False
        self.client = None
        
        # 获取新的工具列表
        return await self.get_tools(server_names)
    
    def filter_tools_by_name(self, tool_names: List[str]) -> List[BaseTool]:
        """
        根据工具名称过滤工具
        
        Args:
            tool_names: 要过滤的工具名称列表
        
        Returns:
            过滤后的工具列表
        """
        if not self.tools:
            logger.warning("工具列表为空，请先调用get_tools()")
            return []
        
        filtered_tools = []
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name in tool_names:
                filtered_tools.append(tool)
        
        logger.info(f"过滤后的工具数量: {len(filtered_tools)}")
        return filtered_tools
    
    def get_tool_by_name(self, tool_name: str) -> Optional[BaseTool]:
        """
        根据名称获取特定工具
        
        Args:
            tool_name: 工具名称
        
        Returns:
            工具实例或None
        """
        for tool in self.tools:
            if hasattr(tool, 'name') and tool.name == tool_name:
                return tool
        return None
    
    def get_tools_info(self) -> Dict[str, Any]:
        """
        获取工具信息摘要
        
        Returns:
            工具信息字典
        """
        tools_info = {
            "total_servers": len(self.mcp_settings),
            "enabled_servers": list(self.mcp_settings.keys()),
            "total_tools": len(self.tools),
            "tool_names": [tool.name for tool in self.tools if hasattr(tool, 'name')],
            "client_initialized": self.initialized
        }
        return tools_info
    
    async def close(self) -> None:
        """关闭MCP客户端"""
        if self.client:
            try:
                # 这里可以添加客户端关闭逻辑
                logger.info("MCP客户端已关闭")
            except Exception as e:
                logger.error(f"关闭MCP客户端时发生错误: {e}")
        
        self.client = None
        self.initialized = False
    
    def __del__(self):
        """析构函数"""
        if self.client and self.initialized:
            # 异步关闭需要在事件循环中处理
            logger.info("MCPClientManager正在清理资源")


async def get_mcp_tools(
    tools: Optional[List[str]] = None
) -> List[BaseTool]:
    """
    获取MCP工具的便捷函数
    
    Args:
        tools: 要获取工具的服务器名称列表，通常用.分割，如"github-tools.get_repo"
    
    Returns:
        工具列表
    """
    manager = MCPClientManager()
    return await manager.get_tools(tools)


# 示例使用
if __name__ == "__main__":
    async def test_mcp_client():
        """测试MCP客户端管理器"""
        try:
            # 创建管理器
            manager = MCPClientManager()
            
            # 显示配置信息
            print("MCP设置:")
            print(f"启用的服务器: {manager.get_enabled_servers()}")
            
            # 获取工具（这里可能会失败，因为服务器可能不可用）
            try:
                tools = await manager.get_tools()
                print(f"获取到 {len(tools)} 个工具")
                # 显示工具信息
                tools_info = manager.get_tools_info()
                print(f"工具信息: {tools_info}")
                
            except Exception as e:
                print(f"获取工具失败（这是正常的，因为测试服务器不可用）: {e}")
            
            # 关闭管理器
            await manager.close()
            
        except Exception as e:
            print(f"测试失败: {e}")
    
    # 运行测试
    asyncio.run(test_mcp_client())

