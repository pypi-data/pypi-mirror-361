from langgraph.graph.state import CompiledStateGraph, StateGraph, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.prebuilt.chat_agent_executor import _get_prompt_runnable, _validate_chat_history
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, SystemMessagePromptTemplate
from langchain_core.tools import BaseTool
from core.apps.tools.tools import global_tool_provider
from core.apps.mcp.client import get_mcp_tools
from typing import Optional, cast
from core.apps.agents.abc import AgentABC, BaseAgentState
from core.apps.model.base import RemoteAgentConfig
from lib.llm_provider import LLMProvider
from core.models.agent import AgentConfig
from lib.agimat_client import AgimatClient

import logging


logger = logging.getLogger(__name__)

memory = MemorySaver()

class BaseAgent(AgentABC):
    name: str = ""
    prompt: str = ""
    llm_name: str = ""
    llm_temperature: float = 0.7
    tools: list[str] = []
    mcp_tools: list[str] = []
    tool_nodes: list[BaseTool] = [] # 工具节点

    
    def __init__(self, /, config: Optional[AgentConfig] = None, cmemory=None):
        super().__init__(config)
        self.load_agent_config(config)
        self.memory = memory if not cmemory else cmemory
        self.llm = LLMProvider.get_model(
            self.agent_config.llm_name,
            self.agent_config.llm_temperature
        )

    def load_agent_config(self, config: Optional[AgentConfig]):
        if config is None:
            return
        self.name = config.name
        self.agent_config = AgentConfig(
            name=config.name,
            description=config.description,
            prompt=config.prompt,
            llm_name=config.llm_name,
            llm_temperature=config.llm_temperature,
            tools=config.tools,
            mcp_tools=config.mcp_tools,
        )
    
    @classmethod
    def load_remote_agent_config(cls, remote_agent_config: RemoteAgentConfig, **kwargs):
        agent_config = remote_agent_config.to_agent_config()
        return cls(config=agent_config, **kwargs)
    
    async def call_llm(self, state: BaseAgentState, config: RunnableConfig):
        _validate_chat_history(state["messages"])
        llm_model = self.llm
        if self.tool_nodes:
            llm_model = llm_model.bind_tools(self.tool_nodes)
        prompt = self.build_prompt(state)
        runnable = _get_prompt_runnable(prompt) | llm_model

        update_states = {}
        response = cast(AIMessage, await runnable.ainvoke(state, config))
        update_states["messages"] = [response]
        return update_states
    
    def build_prompt(self, state: BaseAgentState):
        context = state["context"]
        prompt = self.agent_config.prompt #系统提示词

        return ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(prompt,template_format="jinja2"),
            MessagesPlaceholder(variable_name="messages",optional=True),
        ])
    
    async def _make_graph(self) -> "CompiledStateGraph":
        builder = StateGraph(BaseAgentState)
        
        # 合并本地工具和MCP工具
        self.tool_nodes: list[BaseTool] = [global_tool_provider.get_tool(tool_name) for tool_name in self.agent_config.tools]
        if self.agent_config.mcp_tools:
            mcp_tools = await get_mcp_tools(self.agent_config.mcp_tools)
            self.tool_nodes.extend(mcp_tools)
        
        # 添加节点
        builder.add_node("call_llm", self.call_llm)
        
        # 工具节点
        if self.tool_nodes:
            builder.add_node("tools", ToolNode(tools=self.tool_nodes))
            builder.add_conditional_edges("call_llm", tools_condition)
            builder.add_edge("tools", "call_llm")
        
        builder.add_edge(START, "call_llm")

        return builder.compile(checkpointer=self.memory)
    
