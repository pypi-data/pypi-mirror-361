from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from lib.config import global_config

class LLMProvider:

    @classmethod
    def get_model(cls, model: str, temperature: float=0.7, stream: bool=False):
        llm_config = global_config.get_llm_config(model)
        if not llm_config:
            raise ValueError(f"LLM config not found for model: {model}")
        
        api_type = llm_config.get('api_type', 'openai').lower()
        
        if api_type == 'google' or model.startswith('gemini'):
            # 使用Google Gemini模型
            chat_model = ChatGoogleGenerativeAI(
                model=llm_config.get('model_name', model),
                google_api_key=llm_config.get('api_key'),
                temperature=temperature,
                # Gemini使用disable_streaming参数控制流式输出
                disable_streaming=not stream
            )
        elif api_type == 'anthropic' or model.startswith('claude'):
            # 使用Anthropic Claude模型
            chat_model = ChatAnthropic(
                model=llm_config.get('model_name', model),
                anthropic_api_key=llm_config.get('api_key'),
                temperature=temperature,
                # Claude使用streaming参数
                streaming=stream
            )
        else:
            # 使用OpenAI兼容模型（包括openai、豆包、通义千问等）
            chat_model = ChatOpenAI(
                openai_api_key=llm_config.get('api_key'),
                openai_api_base=llm_config.get('base_url'),
                model_name=llm_config.get('model_name', model),
                temperature=temperature,
                # OpenAI使用streaming参数
                streaming=stream
            )

        return chat_model
    
