from lib.agimat_client import AgimatClient
from core.apps.model.base import RemoteAgentConfig, AgentTemplate, LLMConfig, ToolConfig
from core.apps.agents.base import BaseAgent
from core.apps.agents.abc import AgentABC


agent_context = {
    'base': BaseAgent,
    'react_agent': BaseAgent,
    'xxx-muti-agent': BaseAgent,
}

class AgentBuilder:
   
   @staticmethod
   async def load(agent_name:str, input: dict[str, str] = None) -> RemoteAgentConfig:
       config = await AgimatClient.load_agent(agent_name)
       if config is None:
           raise ValueError(f"Agent {agent_name} not found")
       return RemoteAgentConfig(
           name=agent_name,
           description=config.get('description', ''),
           template=AgentTemplate(config.get('template', 'base')),
           prompt=config.get('prompt', ''),
           llm=LLMConfig(
               name=config['llm_config']['name'],
               temperature=config['llm_config']['temperature'],
           ) if config.get('llm_config') else None,
           tools=[
               ToolConfig(name=tool['name'], description=tool['description'], provider=tool.get('provider', None)) 
               for tool in config.get('tools', []) if tool.get('name')
           ],
           context_schema=config.get('context_schema'),
           output_schema=config.get('output_schema'),
           use_knowledge=config.get('use_knowledge', False),
           extra=config.get('extra')
       )

   @staticmethod
   async def build(agent_name:str, **kwargs) -> AgentABC:
       remote_agent_config = await AgentBuilder.load(agent_name)
       agent = agent_context[remote_agent_config.template].load_remote_agent_config(remote_agent_config, **kwargs)
       return agent
   