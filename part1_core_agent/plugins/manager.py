import importlib
from pathlib import Path
from typing import Dict, List, Any
from .base import PluginBase

class PluginManager:
    def __init__(self, plugins_dir: str = "./plugins"):
        self.plugins_dir = Path(plugins_dir)
        self.plugins: Dict[str, PluginBase] = {}

    def discover_plugins(self) -> List[str]:
        discovered = []
        if not self.plugins_dir.exists():
            return discovered
        for item in self.plugins_dir.iterdir():
            if item.is_dir() and (item / "__init__.py").exists():
                discovered.append(item.name)
        return discovered

    def load_plugin(self, plugin_name: str) -> bool:
        try:
            module = importlib.import_module(f"plugins.{plugin_name}")
            plugin_class = getattr(module, "Plugin")
            plugin = plugin_class()
            if not isinstance(plugin, PluginBase):
                raise ValueError(f"{plugin_name} is not a valid plugin")
            plugin.on_load()
            self.plugins[plugin_name] = plugin
            return True
        except Exception as e:
            print(f"Failed to load plugin {plugin_name}: {e}")
            return False

    def unload_plugin(self, plugin_name: str):
        if plugin_name in self.plugins:
            self.plugins[plugin_name].on_unload()
            del self.plugins[plugin_name]

    def get_all_tools(self) -> List[Dict]:
        tools = []
        for plugin in self.plugins.values():
            tools.extend(plugin.get_tools())
        return tools

    async def execute_tool(self, tool_name: str, tool_input: Dict) -> Any:
        for plugin in self.plugins.values():
            tool_names = [t['name'] for t in plugin.get_tools()]
            if tool_name in tool_names:
                return await plugin.execute_tool(tool_name, tool_input)
        raise ValueError(f"Tool {tool_name} not found")

    def list_plugins(self) -> List[Dict]:
        return [
            {"name": p.name, "version": p.version, "description": p.description}
            for p in self.plugins.values()
        ]
