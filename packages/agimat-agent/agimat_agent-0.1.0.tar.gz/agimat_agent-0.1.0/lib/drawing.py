import os
import logging

logger = logging.getLogger(__name__)


def get_drawing_agent() -> dict:
    # 读取提示词文件
    prompt_file_path = os.path.join(os.path.dirname(__file__), "prompt", "drawing.md")
    
    try:
        with open(prompt_file_path, 'r', encoding='utf-8') as f:
            prompt = f.read()
    except FileNotFoundError:
        # 如果文件不存在，使用默认提示词
        logger.error(f"Prompt file not found: {prompt_file_path}")
        prompt = """
# Role: ImageGenerator - Professional AI Drawing Agent

I am ImageGenerator, a professional AI image generation agent with powerful text-to-image creation capabilities.

## Core Capabilities:
• High-quality text-to-image generation
• Image-to-image conversion and enhancement
• Support for multiple artistic styles and formats
• Detailed image customization options
• Intelligent prompt optimization
• Help users transform creative ideas into beautiful AI-generated images

## Important Guidelines:
- Always use English for MCP tool calls - image generation tools work better with English
- Follow MCP tool function descriptions and parameter requirements strictly
- Respect parameter limits (min/max values for quality, steps, etc.)
- Ensure correct data types (string, integer, float, boolean)
- Include all required parameters specified in tool descriptions
"""

    agent = {
        "id": "507f1f77bcf86cd799439012",
        "name": "drawing_agent",
        "description": "A professional drawing agent that can create images based on user requirements",
        "template": "base",
        "prompt": prompt,
        "llm_config": {
            # 可选模型: "doubao-1-5-lite-32k-250115", "gemini-1.5-flash", "claude-3-5-sonnet", "gpt-4o-mini"
            "name": "doubao-1-5-lite-32k-250115",
            "temperature": 0.9
        },
        "tools": [
            {
                "name": "tavily_search",
                "description": "Search for product information, can query based on product name or category"
            },
            {
                "name": "Wavespeed",
                "description": "AI image generation tool, supports text-to-image and image enhancement functions",
                "provider": "mcp"
            }
        ],
        "knowledge": [
            {},
            {}
        ],
        "extra": {
            "department": "creative_ai",
            "priority": "high", 
            "language": "en-US",
            "working_hours": "24/7",
            "specialty": "image_generation"
        },
        "status": "active"
    }
    return agent