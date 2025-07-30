# Gemini 模型配置说明

## 获取 Google AI API 密钥

1. **访问 Google AI Studio**
   - 前往 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - 使用您的 Google 账户登录

2. **创建 API 密钥**
   - 点击 "Create API Key"
   - 选择一个 Google Cloud 项目（如果没有项目，系统会提示创建一个）
   - 复制生成的 API 密钥

## 配置 API 密钥

在 `conf.yaml` 文件中，将 `YOUR_GOOGLE_API_KEY_HERE` 替换为您的实际 API 密钥：

```yaml
LLM_MODEL_CONFIG:
  gemini-1.5-pro:
    base_url: https://generativelanguage.googleapis.com/v1beta
    name: "gemini-1.5-pro"
    api_key: "您的实际API密钥"  # 替换这里
    api_type: "google"

  gemini-1.5-flash:
    base_url: https://generativelanguage.googleapis.com/v1beta
    name: "gemini-1.5-flash"
    api_key: "您的实际API密钥"  # 替换这里
    api_type: "google"
```

## 安装依赖

确保安装了最新的依赖包：

```bash
pip install -r requirements.txt
```

## 环境变量方式（可选）

您也可以使用环境变量来设置API密钥，这样更安全：

1. 创建 `.env` 文件（如果还没有）：
```bash
GOOGLE_API_KEY=您的实际API密钥
```

2. 修改 `conf.yaml` 中的配置：
```yaml
api_key: ${GOOGLE_API_KEY}
```

## 测试配置

启动应用后，可以通过以下方式测试 Gemini 模型是否配置正确：

```bash
curl -X POST "http://localhost:8000/api/v1/agents/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "agent_test",
    "query": "你好，请介绍一下你自己",
    "task_id": "test-task-1"
  }'
```

## 模型选择建议

- **gemini-1.5-flash**: 速度快，成本低，适合大多数日常任务
- **gemini-1.5-pro**: 功能更强大，适合复杂推理和分析任务

当前默认使用 `gemini-1.5-flash` 模型。

## 常见问题

### API 密钥无效
- 确保 API 密钥正确复制，没有多余的空格
- 检查 Google Cloud 项目是否启用了 Generative AI API

### 模型访问错误
- 确保您的 Google 账户有权限访问 Gemini API
- 检查是否有足够的配额和计费设置

### 网络连接问题
- 确保网络可以访问 `generativelanguage.googleapis.com`
- 如果在中国大陆，可能需要配置代理 