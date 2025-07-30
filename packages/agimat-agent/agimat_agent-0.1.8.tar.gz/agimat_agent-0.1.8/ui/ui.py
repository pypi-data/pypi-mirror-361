import streamlit as st
import requests
import json
import time
from datetime import datetime
import uuid
from typing import Dict, Any
import threading
import queue
import re

# 页面配置
st.set_page_config(
    page_title="Agimat Agent 聊天助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自定义CSS样式
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: fadeIn 0.5s ease-in;
    }
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        margin-left: 2rem;
    }
    .assistant-message {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        margin-right: 2rem;
    }
    .tool-message {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        margin-right: 2rem;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
    }
    .streaming-message {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        margin-right: 2rem;
        border-left: 4px solid #1f77b4;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e0e0e0;
        padding: 0.5rem 1rem;
    }
    .stButton > button {
        border-radius: 25px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    .sidebar-content {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "task_id" not in st.session_state:
    st.session_state.task_id = str(uuid.uuid4())
if "is_streaming" not in st.session_state:
    st.session_state.is_streaming = False
if "streaming_content" not in st.session_state:
    st.session_state.streaming_content = ""
if "result_queue" not in st.session_state:
    st.session_state.result_queue = queue.Queue()


def parse_sse_response(response_text: str) -> Dict[str, Any]:
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": "无法解析响应"}


def format_tool_message(tool_data: Dict) -> str:
    """Renders tool data into a beautiful HTML card, with special handling for POI data."""

    def format_single_poi(poi: Dict) -> str:
        """Formats a single Point of Interest dictionary into an HTML card."""
        name = poi.get("name", "未知地点")
        address = poi.get("address", "地址未提供")
        rating = poi.get("rating", "")
        open_time = poi.get("opentime2") or poi.get("open_time", "营业时间未提供")
        photo_url = poi.get("photo")

        rating_html = ""
        if rating:
            try:
                rating_val = float(rating)
                stars = "⭐" * int(round(rating_val))
                rating_html = f'<p style="margin:0 0 5px 0;"><strong>评分:</strong> {rating_val} {stars}</p>'
            except (ValueError, TypeError):
                rating_html = (
                    f'<p style="margin:0 0 5px 0;"><strong>评分:</strong> {rating}</p>'
                )

        photo_html = ""
        if photo_url:
            photo_html = (
                f'<img src="{photo_url}" alt="{name}" '
                f'style="max-width:400px; width:100%; border-radius:8px; margin-top:10px;">'
            )

        return f"""
<div style="border: 1px solid #e0e0e0; border-radius: 12px; padding: 16px; 
margin-bottom: 12px; background-color: #ffffff;">
    <h4 style="margin-top:0; margin-bottom:8px; color: #1a1a1a;">{name}</h4>
    {rating_html}
    <p style="margin:0 0 5px 0;"><strong>地址:</strong> {address}</p>
    <p style="margin:0;"><strong>营业时间:</strong> {open_time}</p>
    {photo_html}
</div>
"""

    try:
        if "pois" in tool_data and isinstance(tool_data["pois"], list):
            pois_to_show = tool_data["pois"][:5]
            formatted_list = [format_single_poi(poi) for poi in pois_to_show]
            return "为您找到以下结果：<br>" + "".join(formatted_list)
        if "name" in tool_data and ("address" in tool_data or "location" in tool_data):
            return "为您找到以下结果：<br>" + format_single_poi(tool_data)

        # Fallback for other JSON structures, nicely formatted in a code block.
        pretty_json = json.dumps(tool_data, ensure_ascii=False, indent=2)
        return (
            f"<pre style='background-color: #2b2b2b; color: #f8f8f2; "
            f"padding: 12px; border-radius: 8px;'><code>{pretty_json}</code></pre>"
        )
    except Exception:
        pretty_json = json.dumps(tool_data, ensure_ascii=False, indent=2)
        return (
            f"<pre style='background-color: #2b2b2b; color: #f8f8f2; "
            f"padding: 12px; border-radius: 8px;'><code>{pretty_json}</code></pre>"
        )


def detect_and_format_images(content: str) -> str:
    import urllib.parse

    # 处理markdown格式的图片
    markdown_image_pattern = r"!\[([^\]]*)\]\(([^)]+)\)"

    def replace_markdown_image(match):
        alt_text = match.group(1)
        image_url = match.group(2)
        if "%" in image_url and "http" in image_url:
            try:
                image_url = urllib.parse.unquote(image_url)
            except Exception:
                pass
        return (
            f'<img src="{image_url}" alt="{alt_text}" '
            f'style="max-width:400px; height:auto; border-radius:8px; '
            f'margin:10px 0; box-shadow:0 2px 8px rgba(0,0,0,0.1);">'
        )

    # 先替换markdown图片
    formatted_content = re.sub(markdown_image_pattern, replace_markdown_image, content)

    # 只替换不是<img ...>标签的裸图片URL
    def replace_url_image(match):
        image_url = match.group(0)
        # 跳过已是<img ...>标签的内容
        if image_url.strip().startswith("<img"):
            return image_url
        if "%" in image_url and "http" in image_url:
            try:
                image_url = urllib.parse.unquote(image_url)
            except Exception:
                pass
        return (
            f'<img src="{image_url}" alt="图片" '
            f'style="max-width:400px; height:auto; border-radius:8px; '
            f'margin:10px 0; box-shadow:0 2px 8px rgba(0,0,0,0.1);">'
        )

    image_patterns = [
        r'(?<!<img src=")https?://[^\s<>"]+\.(jpg|jpeg|png|gif|webp|bmp|svg)(\?[^\s<>"]*)?',
        r'(?<!<img src=")https?://[^\s<>"]+\.(jpg|jpeg|png|gif|webp|bmp|svg)/[^\s<>"]*',
    ]
    for pattern in image_patterns:
        formatted_content = re.sub(
            pattern, replace_url_image, formatted_content, flags=re.IGNORECASE
        )

    return formatted_content


def format_tool_calls(tool_calls) -> str:
    """格式化tool calls为折叠展示"""
    if not tool_calls:
        return ""

    tool_calls_content = []
    for tool_call in tool_calls:
        tool_name = tool_call.get("name", "unknown")
        tool_args = tool_call.get("args", {})
        tool_id = tool_call.get("id", "")

        args_json = json.dumps(tool_args, ensure_ascii=False, indent=2)
        tool_calls_content.append(
            f"""
**Tool Call:** `{tool_name}`  
**ID:** `{tool_id}`  
**Arguments:**
```json
{args_json}
```
"""
        )

    return "\n".join(tool_calls_content)


def call_agent_api(
    query: str,
    agent_name: str,
    task_id: str,
    session_id: str,
    result_queue: queue.Queue,
) -> None:
    url = "http://localhost:8000/api/v1/agents/stream"
    payload = {
        "agent_name": agent_name,
        "task_id": task_id,
        "session_id": session_id,
        "query": query,
    }
    try:
        with requests.post(url, json=payload, stream=True) as response:
            if response.status_code == 200:
                current_content = ""
                current_tool_calls = []
                tool_calls_list = []  # 改为列表，每个工具输出单独存储

                for line in response.iter_lines():
                    if line:
                        line_str = line.decode("utf-8")
                        if line_str.startswith("data: "):
                            data = line_str[6:]
                            if data.strip():
                                parsed_data = parse_sse_response(data)
                                if "call_llm" in parsed_data:
                                    messages = parsed_data["call_llm"].get(
                                        "messages", []
                                    )
                                    for message in messages:
                                        if message.get("type") == "AIMessage":
                                            content = message.get("content", "")
                                            tool_calls_data = message.get(
                                                "tool_calls", []
                                            )

                                            if content:
                                                current_content += content
                                                # 实时流式内容
                                                result_queue.put(
                                                    {
                                                        "type": "streaming",
                                                        "content": current_content,
                                                        "tool_calls": current_tool_calls,
                                                    }
                                                )

                                            if tool_calls_data:
                                                current_tool_calls.extend(
                                                    tool_calls_data
                                                )

                                elif "tools" in parsed_data:
                                    messages = parsed_data["tools"].get("messages", [])
                                    for message in messages:
                                        if message.get("type") == "ToolMessage":
                                            tool_content = message.get("content", "")
                                            try:
                                                tool_data = json.loads(tool_content)
                                                # 每个工具输出单独存储
                                                tool_calls_list.append(
                                                    {
                                                        "content": format_tool_message(
                                                            tool_data
                                                        ),
                                                        "timestamp": datetime.now().strftime(
                                                            "%H:%M:%S"
                                                        ),
                                                        "tool_type": "formatted",
                                                    }
                                                )
                                            except Exception:
                                                # 原始工具输出
                                                tool_calls_list.append(
                                                    {
                                                        "content": tool_content,
                                                        "timestamp": datetime.now().strftime(
                                                            "%H:%M:%S"
                                                        ),
                                                        "tool_type": "raw",
                                                    }
                                                )

                # 结束后推送最终内容
                if current_content or current_tool_calls:
                    result_queue.put(
                        {
                            "type": "assistant",
                            "content": current_content,
                            "tool_calls": current_tool_calls,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                        }
                    )

                # 每个工具输出单独推送
                for i, tool_call in enumerate(tool_calls_list):
                    result_queue.put(
                        {
                            "type": "tool",
                            "content": tool_call["content"],
                            "timestamp": tool_call["timestamp"],
                            "tool_index": i + 1,  # 添加索引用于显示
                            "tool_type": tool_call["tool_type"],
                        }
                    )

                result_queue.put({"type": "done"})
            else:
                result_queue.put(
                    {"type": "error", "content": f"API请求失败: {response.status_code}"}
                )
    except Exception as e:
        result_queue.put({"type": "error", "content": f"请求出错: {str(e)}"})


def generate_export_html() -> str:
    """生成可导出的HTML内容"""
    css = """
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .chat-message { padding: 1rem; border-radius: 10px; margin: 0.5rem 0; }
        .user-message { 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: 2rem;
        }
        .assistant-message { 
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            margin-right: 2rem;
        }
        .tool-message {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            margin-right: 2rem;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
        }
        .timestamp { font-size: 0.8rem; opacity: 0.8; }
        .expander { 
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 10px 0;
            padding: 10px;
        }
        .expander-header {
            cursor: pointer;
            padding: 5px;
            background: #f5f5f5;
        }
        .expander-content {
            padding: 10px;
            display: none;
        }
        .expander.expanded .expander-content {
            display: block;
        }
    </style>
    <script>
        function toggleExpander(el) {
            el.classList.toggle('expanded');
        }
    </script>
    """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Agimat Agent Chat Export</title>
        {css}
    </head>
    <body>
        <h1 style="text-align: center;">🤖 Agimat Agent Chat Export</h1>
        <div class="chat-container">
    """

    for message in st.session_state.messages:
        if message["role"] == "user":
            html_content += f"""
            <div class="chat-message user-message">
                <strong>👤 用户 <span class="timestamp">({message['timestamp']})</span></strong><br>
                {message['content']}
            </div>
            """
        elif message["role"] == "assistant":
            html_content += f"""
            <div class="chat-message assistant-message">
                <strong>🤖 助手 <span class="timestamp">({message['timestamp']})</span></strong><br>
                {detect_and_format_images(message['content'])}
            """

            if message.get("tool_calls"):
                for idx, tool_call in enumerate(message["tool_calls"], 1):
                    tool_calls_content = format_tool_calls([tool_call])
                    html_content += f"""
                    <div class="expander" onclick="toggleExpander(this)">
                        <div class="expander-header">🔧 工具调用 #{idx} 详情</div>
                        <div class="expander-content">
                            {tool_calls_content}
                        </div>
                    </div>
                    """

            html_content += "</div>"

        elif message["role"] == "tool":
            tool_index = message.get("tool_index", 1)
            html_content += f"""
            <div class="chat-message tool-message">
                <div class="expander" onclick="toggleExpander(this)">
                    <div class="expander-header">
                        🔧 工具输出 #{tool_index} <span class="timestamp">({message['timestamp']})</span>
                    </div>
                    <div class="expander-content">
                        {message['content']}
                    </div>
                </div>
            </div>
            """

    html_content += """
        </div>
        <footer style="text-align: center; margin-top: 20px; color: #666; font-size: 0.8rem;">
            Exported from Agimat Agent Chat
        </footer>
    </body>
    </html>
    """

    return html_content


def main():
    col_title, col_export = st.columns([4, 1])
    with col_title:
        st.markdown(
            '<h1 class="main-header">🤖 Agimat Agent 聊天助手</h1>',
            unsafe_allow_html=True,
        )
    with col_export:
        if st.session_state.messages and st.button("📤 导出聊天", type="secondary"):
            html_content = generate_export_html()
            export_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button(
                label="💾 下载HTML",
                data=html_content,
                file_name=f"agimat_chat_{export_time}.html",
                mime="text/html",
            )

    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.header("⚙️ 配置")
        st.text_input("Agent名称", value="agent_test", key="agent_name")
        st.subheader("📋 会话信息")
        st.text_input("会话ID", key="session_id")
        st.text_input("任务ID", key="task_id")
        if st.button("🔄 重置会话", type="secondary"):
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.task_id = str(uuid.uuid4())
            st.session_state.result_queue = queue.Queue()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # 轮询队列，处理新消息
    while not st.session_state.result_queue.empty():
        msg = st.session_state.result_queue.get()
        if msg["type"] == "streaming":
            st.session_state.streaming_content = msg["content"]
            st.session_state.streaming_tool_calls = msg.get("tool_calls", [])
        elif msg["type"] == "assistant":
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": msg["content"],
                    "tool_calls": msg.get("tool_calls", []),
                    "timestamp": msg["timestamp"],
                }
            )
            st.session_state.streaming_content = ""
            st.session_state.streaming_tool_calls = []
        elif msg["type"] == "tool":
            st.session_state.messages.append(
                {
                    "role": "tool",
                    "content": msg["content"],
                    "timestamp": msg["timestamp"],
                    "tool_index": msg.get("tool_index", 1),
                    "tool_type": msg.get("tool_type", "raw"),
                }
            )
        elif msg["type"] == "error":
            st.error(msg["content"])
            st.session_state.is_streaming = False
            st.session_state.streaming_content = ""
            st.session_state.streaming_tool_calls = []
        elif msg["type"] == "done":
            st.session_state.is_streaming = False
            st.session_state.streaming_content = ""
            st.session_state.streaming_tool_calls = []

    # 初始化streaming状态
    if "streaming_tool_calls" not in st.session_state:
        st.session_state.streaming_tool_calls = []

    chat_container = st.container()
    with chat_container:
        i = 0
        n = len(st.session_state.messages)
        while i < n:
            message = st.session_state.messages[i]
            if message["role"] == "user":
                st.markdown(
                    f"""
                <div class="chat-message user-message">
                    <strong>👤 用户 ({message['timestamp']})</strong><br>
                    {message['content']}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                i += 1
            elif message["role"] == "assistant":
                st.markdown(f"**🤖 助手 ({message['timestamp']})**")
                if message["content"]:
                    formatted_content = detect_and_format_images(message["content"])
                    st.markdown(formatted_content, unsafe_allow_html=True)
                # 工具调用单独折叠
                if message.get("tool_calls"):
                    for idx, tool_call in enumerate(message["tool_calls"], 1):
                        with st.expander(f"🔧 工具调用 #{idx} 详情", expanded=False):
                            tool_calls_content = format_tool_calls([tool_call])
                            st.markdown(tool_calls_content)
                # assistant后面如果紧跟tool，配对显示
                j = i + 1
                while j < n and st.session_state.messages[j]["role"] == "tool":
                    tool_msg = st.session_state.messages[j]
                    tool_index = tool_msg.get("tool_index", 1)
                    expander_title = (
                        f"🔧 工具输出 #{tool_index} ({tool_msg['timestamp']})"
                    )
                    with st.expander(expander_title, expanded=False):
                        st.markdown(tool_msg["content"], unsafe_allow_html=True)
                    j += 1
                st.markdown("---")
                i = j
            elif message["role"] == "tool":
                # 如果前面没配对到assistant，单独显示
                tool_index = message.get("tool_index", 1)
                expander_title = f"🔧 工具输出 #{tool_index} ({message['timestamp']})"
                with st.expander(expander_title, expanded=False):
                    st.markdown(message["content"], unsafe_allow_html=True)
                i += 1

    # 显示流式消息
    if st.session_state.is_streaming and st.session_state.streaming_content:
        st.markdown("**🤖 助手 (正在输入...)**")

        # 渲染流式内容
        if st.session_state.streaming_content:
            formatted_streaming = detect_and_format_images(
                st.session_state.streaming_content
            )
            st.markdown(formatted_streaming + "▌", unsafe_allow_html=True)

        # 如果有tool_calls，每个单独折叠显示
        if st.session_state.streaming_tool_calls:
            for idx, tool_call in enumerate(st.session_state.streaming_tool_calls, 1):
                with st.expander(f"🔧 工具调用 #{idx} 详情", expanded=False):
                    tool_calls_content = format_tool_calls([tool_call])
                    st.markdown(tool_calls_content)

        st.markdown("---")

    st.markdown("---")
    with st.form(key="chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            user_input = st.text_input(
                "💬 输入您的问题...",
                placeholder="例如：查看北京中关村附近好吃的东北菜",
                key="user_input",
            )
        with col2:
            submit_button = st.form_submit_button("🚀 发送", use_container_width=True)
    if submit_button and user_input and not st.session_state.is_streaming:
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_input,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }
        )
        st.session_state.is_streaming = True
        st.session_state.streaming_content = ""
        st.session_state.streaming_tool_calls = []
        st.session_state.result_queue = queue.Queue()
        thread = threading.Thread(
            target=call_agent_api,
            args=(
                user_input,
                st.session_state.get("agent_name", "agent_test"),
                st.session_state.task_id,
                st.session_state.session_id,
                st.session_state.result_queue,
            ),
        )
        thread.start()
        st.rerun()

    if st.session_state.is_streaming:
        st.info("🔄 正在处理您的请求，请稍候...")
        time.sleep(0.1)
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
        "Powered by Agimat Agent | 基于Streamlit构建"
        "</div>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
