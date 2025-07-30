from abc import ABC, abstractmethod
from typing import Dict, Any

class GhStatsPlugin(ABC):
    """Base class for ghstats plugins."""
    @abstractmethod
    def name(self) -> str:
        pass
    @abstractmethod
    def description(self) -> str:
        pass
    @abstractmethod
    def requires_token(self) -> bool:
        pass
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        pass 