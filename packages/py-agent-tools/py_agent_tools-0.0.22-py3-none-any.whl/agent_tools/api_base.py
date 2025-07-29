"""
Not implemented yet.
"""

from abc import ABC, abstractmethod

from pydantic_ai.settings import ModelSettings

from agent_tools.agent_base import ModelNameBase
from agent_tools.agent_runner import AgentRunner


class APIBase(ABC):
    def __init__(self, model_name: ModelNameBase, system_prompt: str = ""):
        self.model_name = model_name.value
        self.system_prompt = system_prompt
        self.runner = AgentRunner()

    @property
    def base_url(self) -> str:
        raise NotImplementedError()

    @property
    def api_key(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def run(self, prompt: str, model_settings: ModelSettings) -> AgentRunner:
        pass
