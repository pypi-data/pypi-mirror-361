import yaml
import os
from typing import Dict, Any


class Config(object):
    agimat_config: dict[str, str]
    llm_model_config: dict[str, Any]

    def __init__(self):
        self.global_config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """
        从本地YAML文件加载配置

        Args:
            path: 配置文件路径

        Returns:
            配置字典
        """

        def deep_update_2level(base: dict, override: dict) -> dict:
            for k, v in override.items():
                if k in base and isinstance(base[k], dict) and isinstance(v, dict):
                    # 只递归到第二层（直接整体替换第二层的 key）
                    for sub_k, sub_v in v.items():
                        base[k][sub_k] = sub_v
                else:
                    base[k] = v
            return base

        base_path = "conf.yaml"
        user_path = os.getenv("CUSTOM_CONFIG_PATH")
        config = {}

        try:
            # 1. 加载基础配置
            if os.path.exists(base_path):
                with open(base_path, "r", encoding="utf-8") as file:
                    config = yaml.safe_load(file) or {}
                    print("📁 初始化系统配置文件:", base_path)

            # 2. 加载用户自定义配置并递归合并
            if user_path and os.path.exists(user_path):
                with open(user_path, "r", encoding="utf-8") as user_file:
                    user_config = yaml.safe_load(user_file) or {}
                    config = deep_update_2level(config, user_config)
                    print("📁 初始化用户自定义配置:", user_path)

            return config

        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return {}

    def get_llm_config(self, model_name: str) -> dict[str, str]:
        return self.global_config.get("LLM_MODEL_CONFIG", {}).get(model_name)

    def get_agimat_config(self, key: str) -> str:
        return self.global_config.get("AGIMAT_CONFIG", {}).get(key)


global_config = Config()


# 测试
if __name__ == "__main__":
    print(global_config.global_config)
