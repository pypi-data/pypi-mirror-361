from pydantic import BaseModel, Field
from typing import Optional
from core.models.agent import Context

class InvokeAgentRequest(BaseModel):
    task_id: Optional[str] = None
    session_id: Optional[str] = None
    agent_name: str
    context: Optional[Context] = None
    is_stream: bool = False
    query: Optional[str] = Field(
        description="The query to invoke the agent",
        default=None,
        examples=["What is the weather in Tokyo?"]
    )

   