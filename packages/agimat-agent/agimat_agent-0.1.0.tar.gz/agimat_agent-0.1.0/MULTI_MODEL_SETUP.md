# 多模型配置指南

本项目现在支持多种大语言模型，包括OpenAI、Google Gemini、Anthropic Claude、字节跳动豆包等。

## 🎯 支持的模型类型

### 1. OpenAI 系列
- `gpt-4o-mini` - 轻量级多模态模型
- `gpt-4o` - 完整多模态模型
- `gpt-3.5-turbo` - 经典对话模型

### 2. Google Gemini 系列
- `gemini-1.5-pro` - 高性能模型，适合复杂任务
- `gemini-1.5-flash` - 快速响应模型，适合日常对话

### 3. Anthropic Claude 系列
- `claude-3-5-sonnet` - 最新平衡型模型
- `claude-3-5-haiku` - 快速轻量级模型
- `claude-3-opus` - 最强推理能力模型

### 4. 国产模型
- `doubao-1-5-lite-32k-250115` - 字节跳动豆包

## 📝 API密钥获取指南

### Google Gemini API密钥
1. 访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
2. 使用Google账户登录
3. 点击 "Create API Key"
4. 复制生成的API密钥

### Anthropic Claude API密钥
1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册并登录账户
3. 进入 "API Keys" 页面
4. 点击 "Create Key"
5. 复制生成的API密钥

### OpenAI API密钥
1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 登录OpenAI账户
3. 点击 "Create new secret key"
4. 复制API密钥

## ⚙️ 配置方法

### 方式1：修改conf.yaml文件

```yaml
LLM_MODEL_CONFIG:
  # Google Gemini配置
  gemini-1.5-pro:
    base_url: https://generativelanguage.googleapis.com/v1beta
    name: "gemini-1.5-pro"
    api_key: "你的Google API密钥"
    api_type: "google"

  gemini-1.5-flash:
    base_url: https://generativelanguage.googleapis.com/v1beta
    name: "gemini-1.5-flash"
    api_key: "你的Google API密钥"
    api_type: "google"

  # Anthropic Claude配置
  claude-3-5-sonnet:
    base_url: https://api.anthropic.com
    name: "claude-3-5-sonnet-20241022"
    api_key: "你的Anthropic API密钥"
    api_type: "anthropic"

  claude-3-5-haiku:
    base_url: https://api.anthropic.com
    name: "claude-3-5-haiku-20241022"
    api_key: "你的Anthropic API密钥"
    api_type: "anthropic"

  # OpenAI配置
  gpt-4o-mini:
    base_url: https://api.openai.com/v1
    name: "gpt-4o-mini"
    api_key: "你的OpenAI API密钥"
    api_type: "openai"
```

### 方式2：使用环境变量（推荐）

创建`.env`文件：

```bash
# Google AI
GOOGLE_API_KEY=你的Google_API密钥

# Anthropic
ANTHROPIC_API_KEY=你的Anthropic_API密钥

# OpenAI
OPENAI_API_KEY=你的OpenAI_API密钥

# 字节跳动豆包
DOUBAO_API_KEY=你的豆包_API密钥
```

然后在`conf.yaml`中使用环境变量：

```yaml
LLM_MODEL_CONFIG:
  gemini-1.5-flash:
    api_key: ${GOOGLE_API_KEY}
    api_type: "google"
  
  claude-3-5-sonnet:
    api_key: ${ANTHROPIC_API_KEY}
    api_type: "anthropic"
  
  gpt-4o-mini:
    api_key: ${OPENAI_API_KEY}
    api_type: "openai"
```

## 🚀 使用示例

### 在Agent配置中指定模型

修改`lib/agimat_client.py`中的模型配置：

```python
"llm_config": {
    "name": "claude-3-5-sonnet",  # 或其他模型名称
    "temperature": 0.9
}
```

### API调用示例

```bash
curl -X POST "http://localhost:8000/api/v1/agents/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "agent_test",
    "query": "你好，请用中文回答",
    "task_id": "test-task-1"
  }'
```

## 📊 模型特点对比

| 模型 | 优势 | 适用场景 | 成本 |
|-----|------|---------|------|
| Claude-3.5-Sonnet | 推理能力强、安全性高 | 复杂分析、代码生成 | 中等 |
| Claude-3.5-Haiku | 速度快、成本低 | 日常对话、简单任务 | 低 |
| Gemini-1.5-Pro | 多模态、长上下文 | 文档分析、复杂推理 | 中等 |
| Gemini-1.5-Flash | 响应快、成本低 | 实时对话、快速查询 | 低 |
| GPT-4o-mini | 平衡性好 | 通用任务 | 低 |

## 🔧 高级配置

### 动态切换模型

可以在运行时通过API参数指定不同的模型：

```python
# 在Agent配置中支持多模型
def create_agent_with_model(model_name: str):
    return {
        "llm_config": {
            "name": model_name,
            "temperature": 0.7
        }
    }
```

### 模型回退机制

配置主备模型，当主模型失败时自动切换：

```python
primary_model = "claude-3-5-sonnet"
fallback_model = "gemini-1.5-flash"
```

## 🛠️ 故障排除

### 常见错误

1. **API密钥无效**
   - 检查密钥是否正确复制
   - 确认API密钥有足够的配额

2. **网络连接问题**
   - 确保网络可以访问对应的API端点
   - 考虑使用代理（如果在中国大陆）

3. **模型名称错误**
   - 检查配置中的model_name是否与API文档一致

### 测试模型连接

```bash
# 安装依赖
pip install -r requirements.txt

# 测试模型连接
python -c "
from lib.llm_provider import LLMProvider
model = LLMProvider.get_model('claude-3-5-sonnet')
print('✅ Claude连接成功')
"
```

## 💰 成本优化建议

1. **任务匹配**：简单任务使用Haiku/Flash，复杂任务使用Sonnet/Pro
2. **批量处理**：合并相似请求减少API调用
3. **缓存机制**：对重复查询启用缓存
4. **监控用量**：定期检查API使用量和费用

## 🔄 版本更新

当模型版本更新时，只需修改`conf.yaml`中的`name`字段：

```yaml
claude-3-5-sonnet:
  name: "claude-3-5-sonnet-20241022"  # 更新到最新版本
``` 