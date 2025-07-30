from abc import ABC, abstractmethod
from langgraph.graph.state import CompiledStateGraph
from core.apps.model.base import RemoteAgentConfig
from core.models.agent import Context, AgentConfigType
from core.apps.utils.dict import dict_update
from typing import Annotated, Any
from langgraph.prebuilt.chat_agent_executor import AgentState
import operator


class BaseAgentState(AgentState):
    query: str
    context: Context

class AgentABC(object):
    name: str
    description: str
    agent_config: AgentConfigType | None
    agent_output: Annotated[dict[str, Any], dict_update]
    tool_resp: Annotated[dict[str, Any], dict_update]

    def __init__(self, config: AgentConfigType | None):
        self.agent_config = config


    async def init(self, context:Context):
        return {}
    
    
    async def _make_graph(self) -> CompiledStateGraph:
        raise NotImplementedError
    
    
    async def make_graph(self) -> CompiledStateGraph:
        graph = await self._make_graph()
        return graph

    @classmethod
    def load_remote_agent_config(cls, config: RemoteAgentConfig, **kwargs):
        raise NotImplementedError
    
