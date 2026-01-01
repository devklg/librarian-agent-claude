from abc import ABC, abstractmethod
from typing import Dict, Any, List

class PluginBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        pass

    @property
    def description(self) -> str:
        return ""

    @abstractmethod
    def get_tools(self) -> List[Dict]:
        pass

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        pass

    def on_load(self):
        pass

    def on_unload(self):
        pass
