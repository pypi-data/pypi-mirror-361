"""
    config for app
"""

from dataclasses import dataclass
import os
import json
from typing import Literal, TypeVar, overload, Any

T = TypeVar('T')


@dataclass
class LLM:
    model: str
    base_url: str
    api_key: str


@dataclass
class LLMConfig:
    llm: LLM
    llm_vision: LLM


@dataclass
class SearchConfig:
    serper_api_key: str
    baidu_authorization: str


@dataclass
class WorkspaceConfig:
    dir: str


ModelType = Literal["hero_model", "coder_model", "extractor_model",
                     "answer_model", "browser_model", "search", "stormer_model"]


class Config:
    """
    配置
    """

    def __init__(self):
        """
        初始化配置
        """
        with open(
            os.path.join(os.path.dirname(__file__), "../config.json"),
            "r",
            encoding="utf-8",
        ) as f:
            self.config = json.load(f)

        self.use_profile = self.config["use_profile"]

    @overload
    def get(self, key: str) -> Any | None: ...

    @overload
    def get(self, key: str, default: T) -> T: ...

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置
        """
        # 优先从profile中获取
        if key in self.config["profile"][self.use_profile]:
            return self.config["profile"][self.use_profile][key]
        elif key in self.config["app"]:
            return self.config["app"][key]
        else:
            return default

    def model(self, model_name: ModelType):
        """
        获取模型
        """
        model = self.config["profile"][self.use_profile][model_name]
        server = model[0]
        model = model[1]

        return LLM(
            model=model,
            base_url=self.config["api_service"][server]["base_url"],
            api_key=self.config["api_service"][server]["api_key"],
        )

    def search(self, key):
        """
        获取搜索
        """
        return self.config["api_service"][
            self.config["profile"][self.use_profile]["search"]
        ][key]
    
    def python_venv_dir(self):
        """
        获取Python虚拟环境目录
        """
        return self.get("python_venv_dir")

    def is_debug(self):
        """
        是否为调试模式
        """
        return self.config["debug"]
    
    def prompt_dir(self):
        """
        获取Prompt目录
        """
        language = self.get("language")
        if language is None or language == "":
            return "prompt"
        if language == "zh":
            return "prompt/zh"
        return ""


config = Config()
