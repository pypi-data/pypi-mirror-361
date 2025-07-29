from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class Frontend:
    def __init__(self, component_url: str):
        self.component_url = component_url
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "component_url": self.component_url
        }

class PluginRegister:
    def __init__(
        self, 
        name: str, 
        version: str, 
        frontend: Optional[Frontend] = None,
        dependencies: Optional["Dependencies"] = None
    ):
        self.name = name
        self.version = version
        self.frontend = frontend
        self.dependencies = dependencies
    
    def to_dict(self) -> Dict[str, Any]:
        result = {
            "name": self.name,
            "version": self.version,
        }
        
        if self.frontend:
            result["frontend"] = self.frontend.to_dict()
            
        if self.dependencies:
            result["dependencies"] = self.dependencies.to_dict()
            
        return result

class Table:
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version
    
    def to_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "version": self.version
        }

class Dependencies:
    def __init__(self, tables: List[Table]):
        self.tables = tables
    
    def to_dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {
            "tables": [table.to_dict() for table in self.tables]
        }

class CoreGateway(ABC):
    @abstractmethod
    async def register_plugin(self, plugin_register: PluginRegister) -> None:
        pass
