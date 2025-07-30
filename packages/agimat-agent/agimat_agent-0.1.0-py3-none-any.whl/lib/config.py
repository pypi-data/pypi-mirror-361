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
        path = os.getenv("AGIMAT_CONFIG_PATH")
        if not path:
            path = "conf.yaml"

        try:
            # 检查文件是否存在
            if not os.path.exists(path):
                raise FileNotFoundError(f"配置文件不存在: {path}")

            # 读取YAML文件
            with open(path, "r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                print("初始化配置文件:", path)

            return config

        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return {}

    def get_llm_config(self, model_name: str) -> dict[str, str]:
        return self.global_config.get("LLM_MODEL_CONFIG", {}).get(model_name)

    def get_agimat_config(self, key: str) -> str:
        return self.global_config.get("AGIMAT_CONFIG", {}).get(key)


global_config = Config()
