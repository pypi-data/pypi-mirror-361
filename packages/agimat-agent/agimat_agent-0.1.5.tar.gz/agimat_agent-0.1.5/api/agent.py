# Agent API 路由
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import StreamingResponse
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from core.models.request import InvokeAgentRequest, Context
from core.models.response import CommonResponse
from core.apps.builder.builder import AgentBuilder
from lib.agimat_client import AgimatClient
from core.apps.observability.langsmith import create_run_config, create_langsmith_callback
import json
import asyncio
import logging
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/agents", tags=["agents"])

def serialize_chunk(chunk):
    """序列化流式数据块"""
    if isinstance(chunk, dict):
        result = {}
        for key, value in chunk.items():
            if isinstance(value, BaseMessage):
                # 序列化消息对象
                result[key] = {
                    "type": value.__class__.__name__,
                    "content": value.content,
                    "additional_kwargs": getattr(value, 'additional_kwargs', {}),
                    "tool_calls": getattr(value, 'tool_calls', None)
                }
            elif isinstance(value, list):
                result[key] = [serialize_chunk(item) for item in value]
            elif isinstance(value, dict):
                result[key] = serialize_chunk(value)
            else:
                result[key] = value
        return result
    elif isinstance(chunk, BaseMessage):
        return {
            "type": chunk.__class__.__name__,
            "content": chunk.content,
            "additional_kwargs": getattr(chunk, 'additional_kwargs', {}),
            "tool_calls": getattr(chunk, 'tool_calls', None)
        }
    else:
        return chunk

@router.post("/invoke")
async def invoke(req: InvokeAgentRequest):
    resp = CommonResponse()
    try:
        # 创建 LangSmith 追踪配置
        langsmith_config = create_run_config(
            task_id=req.task_id,
            metadata={
                "agent_name": req.agent_name,
                "query": req.query,
                "task_id": req.task_id
            }
        )
        
        # 创建运行配置（合并LangSmith回调）
        runnable_config = RunnableConfig(
            configurable={'thread_id': req.task_id},
            callbacks=[create_langsmith_callback()],
            **langsmith_config
        )
        
        agent = await AgentBuilder.build(req.agent_name)
        graph = await agent.make_graph()
        context = req.context if req.context else Context()
        history = ''
        if req.session_id:
            # 历史消息 todo - 暂时不实现
            pass
        input = {
            'messages': [HumanMessage(content=req.query)],
            'query': req.query,
            'context': context,
            'history': history,
        }
        
        result = await graph.ainvoke(input, config=runnable_config)
        resp.data = result

    except Exception as e:
        logger.error(f"Error invoking agent: {e}")
        resp.code = 500
        resp.message = str(e)
    return resp.model_dump()

@router.post("/stream")
async def stream(req: InvokeAgentRequest):
    """流式Agent调用接口"""
    async def generate():
        try:
            # 创建 LangSmith 追踪配置
            langsmith_config = create_run_config(
                task_id=req.task_id,
                metadata={
                    "agent_name": req.agent_name,
                    "query": req.query,
                    "task_id": req.task_id
                }
            )
            
            # 创建运行配置（合并LangSmith回调）
            runnable_config = RunnableConfig(
                configurable={'thread_id': req.task_id},
                callbacks=[create_langsmith_callback()],
                **langsmith_config
            )
            
            agent = await AgentBuilder.build(req.agent_name)
            graph = await agent.make_graph()
            context = req.context if req.context else Context()
            history = ''
            if req.session_id:
                # 历史消息 todo - 暂时不实现
                pass
            input = {
                'messages': [HumanMessage(content=req.query)],
                'query': req.query,
                'context': context,
                'history': history,
            }
            
            # 流式执行
            async for chunk in graph.astream(input, config=runnable_config):
                # 处理复杂对象的序列化
                try:
                    serialized_chunk = serialize_chunk(chunk)
                    yield f"data: {json.dumps(serialized_chunk, ensure_ascii=False)}\n\n"
                except Exception as e:
                    logger.warning(f"Failed to serialize chunk: {e}")
                    # 发送简化的数据
                    simple_chunk = {"type": "chunk", "data": str(chunk)}
                    yield f"data: {json.dumps(simple_chunk, ensure_ascii=False)}\n\n"
                
        except Exception as e:
            logger.error(f"Error in stream agent: {e}")
            error_data = {
                "error": True,
                "message": str(e),
                "code": 500
            }
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "text/event-stream"
        }
    )