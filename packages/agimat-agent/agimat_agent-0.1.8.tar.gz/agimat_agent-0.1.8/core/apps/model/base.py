from pydantic import BaseModel
from typing import Optional, List
from core.models.agent import JsonSchema, AgentConfigABC, AgentConfig
from enum import Enum

class AgentTemplate(str, Enum):
    base = 'base'
    react_agent = 'react_agent'

template_configs: dict[AgentTemplate|None, type[AgentConfigABC]] = {
    AgentTemplate.react_agent: AgentConfig,
}

class LLMConfig(BaseModel):
    name: str
    temperature: float

class ToolConfig(BaseModel):
    name: str
    description: str
    provider: Optional[str] = None

class RemoteAgentConfig(BaseModel):
    name: str
    description: str
    template: AgentTemplate
    prompt: str
    llm: Optional[LLMConfig] = None
    tools: Optional[List[ToolConfig]] = None
    context_schema: Optional[JsonSchema] = None
    output_schema: Optional[JsonSchema] = None
    use_knowledge: bool = False
    extra: Optional[dict] = None

    def to_agent_config(self):
        name = self.name
        tools = []
        mcp_tools = []
        if self.tools:
            for tool in self.tools:
                if tool.provider == 'mcp':
                    mcp_tools.append(tool.name)
                else:
                    tools.append(tool.name)
        extra = self.extra 
        return template_configs.get(self.template, AgentConfig)(
            name=name,
            description=self.description,
            prompt=self.prompt,
            llm_name=self.llm.name,
            llm_temperature=self.llm.temperature,
            tools=tools,
            mcp_tools=mcp_tools,
            context_schema=self.context_schema,
            output_schema=self.output_schema,
            use_knowledge=self.use_knowledge,
        )

