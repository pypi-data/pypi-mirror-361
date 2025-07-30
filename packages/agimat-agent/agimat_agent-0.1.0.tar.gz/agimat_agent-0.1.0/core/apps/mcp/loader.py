"""
MCP 工具加载器
从mcp_tool.json配置文件加载到内存中
"""
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
from langchain.tools import BaseTool
import aiofiles

logger = logging.getLogger(__name__)


class MCPServerConfig(BaseModel):
    """MCP服务器配置模型"""
    transport: str = Field(..., description="传输类型: streamableHttp 或 stdio")
    url: Optional[str] = Field(None, description="StreamableHttp服务的URL")
    command: Optional[str] = Field(None, description="Stdio服务的命令")
    args: Optional[List[str]] = Field(None, description="Stdio服务的参数")
    description: Optional[str] = Field(None, description="服务描述")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP请求头")
    enabled: bool = Field(True, description="是否启用此服务")


class MCPConfigLoader:
    """MCP工具加载器"""
    
    def __init__(self, config_path: Union[str, Path] = "core/apps/mcp/mcp_tool.json"):
        self.config_path = Path(config_path)
        self.raw_config: Dict[str, Any] = {}
        self.mcp_settings: Dict[str, Dict[str, Any]] = {}
        
    async def load_config(self) -> Dict[str, Any]:
        """异步加载配置文件"""
        try:
            async with aiofiles.open(self.config_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                self.raw_config = json.loads(content)
                logger.info(f"成功加载配置文件: {self.config_path}")
                return self.raw_config
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {e}")
            raise
    
    def load_config_sync(self) -> Dict[str, Any]:
        """同步加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.raw_config = json.load(f)
                logger.info(f"成功加载配置文件: {self.config_path}")
                return self.raw_config
        except FileNotFoundError:
            logger.error(f"配置文件未找到: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {e}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件时发生错误: {e}")
            raise
    
    def validate_server_config(self, name: str, config: Dict[str, Any]) -> MCPServerConfig:
        """验证单个服务器配置"""
        try:
            return MCPServerConfig(**config)
        except Exception as e:
            logger.error(f"服务器 {name} 配置验证失败: {e}")
            raise
    
    def convert_to_mcp_settings(self) -> Dict[str, Dict[str, Any]]:
        """将原始配置转换为MCP标准settings格式"""
        if not self.raw_config:
            raise ValueError("配置文件未加载，请先调用 load_config() 或 load_config_sync()")
        
        mcp_servers = self.raw_config.get("mcpServers", {})
        self.mcp_settings = {}
        
        for server_name, server_config in mcp_servers.items():
            # 验证配置
            validated_config = self.validate_server_config(server_name, server_config)
            
            # 跳过未启用的服务
            if not validated_config.enabled:
                logger.info(f"跳过未启用的服务: {server_name}")
                continue
            
            # 转换为MCP标准格式
            mcp_server_settings = {}
            
            if validated_config.transport == "streamableHttp":
                if not validated_config.url:
                    raise ValueError(f"服务器 {server_name} 缺少必需的 url 配置")
                
                mcp_server_settings = {
                    "url": validated_config.url,
                    "transport": "streamable_http"  # MCP标准使用下划线
                }
                
                # 添加可选的headers
                if validated_config.headers:
                    mcp_server_settings["headers"] = validated_config.headers
                    
            elif validated_config.transport == "stdio":
                if not validated_config.command:
                    raise ValueError(f"服务器 {server_name} 缺少必需的 command 配置")
                
                mcp_server_settings = {
                    "command": validated_config.command,
                    "transport": "stdio"
                }
                
                # 添加可选的args
                if validated_config.args:
                    mcp_server_settings["args"] = validated_config.args
            else:
                raise ValueError(f"服务器 {server_name} 不支持的传输类型: {validated_config.transport}")
            
            # 添加描述信息（如果有）
            if validated_config.description:
                mcp_server_settings["description"] = validated_config.description
            
            self.mcp_settings[server_name] = mcp_server_settings
            logger.info(f"成功转换服务器配置: {server_name}")
        
        return self.mcp_settings
    
    def get_mcp_settings(self) -> Dict[str, Dict[str, Any]]:
        """获取MCP标准settings字典"""
        return self.mcp_settings
    
    def get_enabled_servers(self) -> List[str]:
        """获取启用的服务器列表"""
        return list(self.mcp_settings.keys())
    
    def get_server_config(self, server_name: str) -> Optional[Dict[str, Any]]:
        """获取特定服务器的配置"""
        return self.mcp_settings.get(server_name)
    
    async def load_and_convert(self) -> Dict[str, Dict[str, Any]]:
        """异步加载并转换配置的便捷方法"""
        await self.load_config()
        return self.convert_to_mcp_settings()
    
    def load_and_convert_sync(self) -> Dict[str, Dict[str, Any]]:
        """同步加载并转换配置的便捷方法"""
        self.load_config_sync()
        return self.convert_to_mcp_settings()


# 便捷函数
async def load_mcp_settings_async(config_path: Union[str, Path] = "core/apps/mcp/mcp_tool.json") -> Dict[str, Dict[str, Any]]:
    """异步加载MCP设置的便捷函数"""
    loader = MCPConfigLoader(config_path)
    return await loader.load_and_convert()


def load_mcp_settings(config_path: Union[str, Path] = "core/apps/mcp/mcp_tool.json") -> Dict[str, Dict[str, Any]]:
    """同步加载MCP设置的便捷函数"""
    loader = MCPConfigLoader(config_path)
    return loader.load_and_convert_sync()


# 示例使用
if __name__ == "__main__":
    # 同步示例
    try:
        settings = load_mcp_settings()
        print("MCP Settings:")
        print(json.dumps(settings, indent=2, ensure_ascii=False))
        print(f"\n启用的服务器: {list(settings.keys())}")
    except Exception as e:
        print(f"加载失败: {e}")
    
    # 异步示例
    async def async_example():
        try:
            settings = await load_mcp_settings_async()
            print("\n异步加载的MCP Settings:")
            print(json.dumps(settings, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"异步加载失败: {e}")
    
    # 运行异步示例
    asyncio.run(async_example())

