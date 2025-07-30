from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel
from datetime import datetime

class JsonSchema(BaseModel):
    type: str
    description: Optional[str] = None
    
class Context(BaseModel):
    session_id: Optional[str] = None


class AgentConfigABC(BaseModel):
    """
    Agent 基础配置
    """
    name: str
    description: str

    output_schema: Optional[JsonSchema] = None
    context_schema: Optional[JsonSchema] = None

    # system prompt
    prompt: Optional[str]

    # llm 
    llm_name: str
    llm_temperature: float

    # tools
    tools: Optional[List[str]] = None
    mcp_tools: Optional[List[str]] = None

    # 知识库
    use_knowledge: bool = False

    # 其他参数
    kwargs: Optional[Dict[str, Optional[str]]] = None

class AgentConfig(AgentConfigABC):
    pass

AgentConfigType = Union[AgentConfigABC, AgentConfig]