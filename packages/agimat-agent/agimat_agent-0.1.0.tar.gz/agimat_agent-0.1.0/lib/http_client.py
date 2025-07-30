import asyncio
import aiohttp
import logging
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

class AsyncHTTPClient:
    """简单的异步HTTP客户端"""
    
    def __init__(self, timeout: int = 30, headers: Optional[Dict[str, str]] = None):
        """
        初始化HTTP客户端
        
        Args:
            timeout: 超时时间（秒）
            headers: 默认请求头
        """
        self.timeout = timeout
        self.headers = headers or {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self._ensure_session()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.close()
    
    async def _ensure_session(self):
        """确保session已创建"""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self.headers
            )
    
    async def close(self):
        """关闭客户端"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def get(self, url: str, params: Optional[Dict[str, Any]] = None, 
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        GET请求
        
        Args:
            url: 请求URL
            params: URL参数
            headers: 请求头
            
        Returns:
            响应数据字典
        """
        await self._ensure_session()
        
        try:
            async with self._session.get(url, params=params, headers=headers) as response:
                return await self._parse_response(response)
        except Exception as e:
            raise Exception(f"GET请求失败: {str(e)}")
    
    async def post(self, url: str, data: Optional[Union[Dict[str, Any], str]] = None,
                   json_data: Optional[Dict[str, Any]] = None, 
                   headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        POST请求
        
        Args:
            url: 请求URL
            data: 请求体数据
            json_data: JSON数据
            headers: 请求头
            
        Returns:
            响应数据字典
        """
        await self._ensure_session()
        
        try:
            if json_data is not None:
                async with self._session.post(url, json=json_data, headers=headers) as response:
                    return await self._parse_response(response)
            else:
                async with self._session.post(url, data=data, headers=headers) as response:
                    return await self._parse_response(response)
        except Exception as e:
            raise Exception(f"POST请求失败: {str(e)}")
    
    async def _parse_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """
        解析响应
        
        Args:
            response: aiohttp响应对象
            
        Returns:
            解析后的响应数据
        """
        try:
            # 尝试解析JSON
            if "application/json" in response.headers.get("content-type", ""):
                data = await response.json()
            else:
                data = await response.text()
        except (json.JSONDecodeError, UnicodeDecodeError):
            data = await response.read()
        
        return {
            "status": response.status,
            "headers": dict(response.headers),
            "data": data,
            "url": str(response.url)
        }


# 便捷函数
async def http_get(url: str, **kwargs) -> Dict[str, Any]:
    """便捷的GET请求函数"""
    async with AsyncHTTPClient() as client:
        return await client.get(url, **kwargs)


async def http_post(url: str, **kwargs) -> Dict[str, Any]:
    """便捷的POST请求函数"""
    async with AsyncHTTPClient() as client:
        return await client.post(url, **kwargs)


    