from lib.http_client import http_get
from lib.config import global_config
from lib.drawing import get_drawing_agent
from lib.revit import get_revit_agent

class AgimatClient:
    base_url: str = global_config.get_agimat_config("base_url")

    # @classmethod
    # async def load_agent(cls, agent_name: str) -> dict:
    #     path = f"/api/v1/agent/{agent_name}"
    #     url = f"{cls.base_url}{path}"
    #     resp = await http_get(url)
    #     if resp['status'] != 200:
    #         raise Exception(f"Failed to load agent status: {resp['status']}")
    #     data = resp['data']
    #     if not data or data['code'] != 200:
    #         raise Exception(f"Failed to load agent: {data['message']}")
    #     return data['data']
    
    @classmethod
    async def load_agent(cls, agent_name: str) -> dict:
        if agent_name == "drawing":
            return get_drawing_agent()
        elif agent_name == "revit":
            return get_revit_agent()
        agent = {
            "id": "507f1f77bcf86cd799439011",
            "name": "agent_test",
            "description": "一个专业的客服智能体，能够处理客户咨询、订单查询和售后服务",
            "template": "base",
            "prompt": """
                # 角色：客服小助手
                帮助用户查询美食、出行等信息的智能助手

                ## 目标：
                1. 基于用户位置提供精准的美食推荐
                2. 规划最优出行路线并提供实时路况

                ## 技能：
                1. 理解用户自然语言查询意图
                2. 熟练使用高德地图工具进行数据检索，需要转换成标准的经纬度坐标
                3. 根据用户偏好过滤和排序结果

                ## 工作流：
                1. 解析用户请求，提取关键词和位置信息
                2. 调用对应工具获取数据（美食搜索/路线规划）
                3. 整理结果，添加必要说明后返回给用户

                ## 输出格式：
                - 使用工具调用格式：<|FunctionCallBegin|>[{"name":"工具名","parameters":{"param":"value"}}]<|FunctionCallEnd|>
                - 推荐结果需包含名称、地址、评分等关键信息

                ## 限制：
                - 仅回答与美食、出行、景点相关的问题
                - 所有地理位置信息需基于高德地图官方数据
                - 无法回答时需引导用户补充必要信息

                【工具列表】
                - search-restaurant：搜索周边餐厅（参数：keyword, location, offset）
                - search-route：规划出行路线（参数：from, to, mode）
                """,
            "llm_config": {
                # 可选模型: "doubao-1-5-lite-32k-250115", "gemini-1.5-flash", "claude-3-5-sonnet", "gpt-4o-mini"
                "name": "doubao-1-5-lite-32k-250115",
                "temperature": 0.9
            },
            "tools": [
                {
                    "name": "tavily_search",
                    "description": "搜索产品信息，可以根据产品名称或分类查询"
                },
                {
                    "name": "get_random_number",
                    "description": "生成指定范围内的随机数"
                },
                {
                    "name": "calculate_sum",
                    "description": "计算两个数字的和"
                },
                {
                    "name": "amap-maps-streamableHTTP",
                    "description": "搜索周边餐厅（参数：keyword, location, offset）",
                    "provider": "mcp"
                }, {
                    "name": "Wavespeed",
                    "description": "根据描述生成图片",
                    "provider": "mcp"
                }
            ],
            "knowledge": [
                {},
                {}
            ],
            "extra": {
                "department": "customer_service",
                "priority": "high",
                "language": "zh-CN",
                "working_hours": "09:00-18:00"
            },
            "status": "active"
        }
        return agent

if __name__ == "__main__":
    async def test():
        AgimatClient.base_url = global_config.get_agimat_config("base_url")
        resp = await AgimatClient.load_agent("agent_test")
        print(resp)

    import asyncio
    asyncio.run(test())