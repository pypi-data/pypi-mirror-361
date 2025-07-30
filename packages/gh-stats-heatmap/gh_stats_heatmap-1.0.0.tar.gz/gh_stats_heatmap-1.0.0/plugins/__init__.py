"""Plugin system for ghstats optional features."""

from typing import Dict, Any, Optional
from plugins.base import GhStatsPlugin

class PluginManager:
    """Manages loaded plugins."""
    
    def __init__(self):
        self._plugins: Dict[str, GhStatsPlugin] = {}
    
    def register(self, plugin: GhStatsPlugin):
        """Register a plugin."""
        self._plugins[plugin.name()] = plugin
    
    def get(self, name: str) -> Optional[GhStatsPlugin]:
        """Get plugin by name."""
        return self._plugins.get(name)
    
    def list_plugins(self) -> Dict[str, str]:
        """List all available plugins with descriptions."""
        return {name: plugin.description() for name, plugin in self._plugins.items()}
    
    def has_plugin(self, name: str) -> bool:
        """Check if plugin exists."""
        return name in self._plugins

from .global_leaderboard import GlobalLeaderboardPlugin 