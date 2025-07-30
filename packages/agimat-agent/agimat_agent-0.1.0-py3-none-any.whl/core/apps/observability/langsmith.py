"""
LangSmith 本地接入配置
"""
import os
import logging
from typing import Optional, Dict, Any


logger = logging.getLogger(__name__)


class LangSmithConfig:
    """LangSmith 配置管理"""
    
    def __init__(self):
        self.api_key = os.getenv("LANGSMITH_API_KEY")
        self.project_name = os.getenv("LANGSMITH_PROJECT", "agimat-agent")
        self.endpoint = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
        self.enabled = os.getenv("LANGSMITH_TRACING", "false").lower() == "true"
        self.session_name = os.getenv("LANGSMITH_SESSION", "default")
    
    def get_config_dict(self) -> Dict[str, Any]:
        """获取配置字典"""
        return {
            "enabled": self.enabled,
            "api_key_set": bool(self.api_key),
            "project_name": self.project_name,
            "endpoint": self.endpoint,
            "session_name": self.session_name
        }


# 全局配置实例
langsmith_config = LangSmithConfig()


def create_run_config(
    task_id: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None
) -> Dict[str, Any]:
    """创建运行配置
    
    Args:
        task_id: 任务ID
        tags: 标签列表
        metadata: 元数据
        
    Returns:
        运行配置字典
    """
    config = {}
    
    if not langsmith_config.enabled:
        return config
    
    config["run_name"] = f"agent_run_{task_id or 'default'}"
    config["tags"] = tags or []
    config["metadata"] = metadata or {}
    
    return config


def create_langsmith_callback():
    """创建 LangSmith 回调处理器"""
    if not langsmith_config.enabled:
        return None
    
    try:
        from langsmith import Client
        from langchain.callbacks.tracers import LangChainTracer
        
        client = Client(
            api_key=langsmith_config.api_key,
            api_url=langsmith_config.endpoint
        )
        
        tracer = LangChainTracer(
            project_name=langsmith_config.project_name,
            client=client
        )
        
        return tracer
    except ImportError:
        logger.warning("LangSmith 客户端未安装，无法创建回调处理器")
        return None
    except Exception as e:
        logger.error(f"创建 LangSmith 回调处理器失败: {e}")
        return None


# 装饰器：为函数添加 LangSmith 追踪
def trace_langsmith(
    name: Optional[str] = None,
    tags: Optional[list] = None,
    metadata: Optional[dict] = None
):
    """LangSmith 追踪装饰器
    
    Args:
        name: 追踪名称
        tags: 标签列表
        metadata: 元数据
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not langsmith_config.enabled:
                return func(*args, **kwargs)
            
            try:
                from langsmith import traceable
                
                # 创建追踪配置
                trace_config = {
                    "name": name or func.__name__,
                    "project_name": langsmith_config.project_name
                }
                
                if tags:
                    trace_config["tags"] = tags
                if metadata:
                    trace_config["metadata"] = metadata
                
                # 应用追踪装饰器
                traced_func = traceable(**trace_config)(func)
                return traced_func(*args, **kwargs)
                
            except ImportError:
                logger.warning("LangSmith traceable 装饰器不可用，跳过追踪")
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"LangSmith 追踪失败: {e}")
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


if __name__ == "__main__":\
    # 测试配置
    print("LangSmith 配置:")
    config = langsmith_config.get_config_dict()
    for key, value in config.items():
        print(f"  {key}: {value}")
    
    # 测试运行配置
    run_config = create_run_config(
        session_id="test-session",
        user_id="test-user",
        tags=["test", "demo"],
        metadata={"version": "1.0"}
    )
    print(f"\n运行配置: {run_config}") 