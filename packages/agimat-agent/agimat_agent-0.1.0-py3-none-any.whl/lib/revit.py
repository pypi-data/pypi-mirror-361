import os
import logging

logger = logging.getLogger(__name__)


def get_revit_agent() -> dict:
    # 读取提示词文件
    prompt_file_path = os.path.join(os.path.dirname(__file__), "prompt", "revit.md")

    try:
        with open(prompt_file_path, "r", encoding="utf-8") as f:
            prompt = f.read()
    except FileNotFoundError:
        # 如果文件不存在，使用默认提示词
        logger.error(f"Prompt file not found: {prompt_file_path}")
        prompt = """
# Role: RevitAssistant - AI Revit Design Agent

I am RevitAssistant, an AI agent that helps users with Revit architecture and design tasks.

## Core Capabilities:
• Creating and modifying Revit elements
• Analyzing and querying Revit models
• Assisting with drawing and review processes
• Supporting Revit workflows for beginners
• Providing Revit knowledge and guidance
"""

    agent = {
        "id": "607e1f77bcf86cd799439013",
        "name": "revit_agent",
        "description": "A professional Revit agent that assists with Revit modeling and drawing tasks",
        "template": "base",
        "prompt": prompt,
        "llm_config": {
            # 可选模型: "doubao-1-5-lite-32k-250115", "gemini-1.5-flash", "claude-3-5-sonnet", "gpt-4o-mini"
            "name": "doubao-1-5-lite-32k-250115",
            "temperature": 0.7,
        },
        "tools": [
            {
                "name": "tavily_search",
                "description": "Search for Revit information and techniques",
            },
            {
                "name": "revit-mcp",
                "description": "Revit Model Context Protocol tools for interacting with Revit",
                "provider": "mcp",
            },
        ],
        "knowledge": [{}, {}],
        "extra": {
            "department": "architecture_design",
            "priority": "high",
            "language": "zh-CN",
            "working_hours": "24/7",
            "specialty": "revit_modeling",
        },
        "status": "active",
    }
    return agent
