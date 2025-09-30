"""
Fleet Management System - Modular Architecture
Module Registry and Loader
"""
from typing import Dict, List, Callable
from fastapi import FastAPI, APIRouter

class ModuleRegistry:
    """Central registry for all fleet management modules."""
    
    def __init__(self):
        self.modules: Dict[str, dict] = {}
        self._registered_routers: List[APIRouter] = []
    
    def register_module(
        self,
        code: str,
        name: str,
        router: APIRouter,
        role: str,
        description: str = "",
        icon: str = "",
        color: str = ""
    ):
        """Register a new module with the system."""
        self.modules[code] = {
            "code": code,
            "name": name,
            "router": router,
            "role": role,
            "description": description,
            "icon": icon,
            "color": color,
            "path": f"/{code.replace('_', '-')}"
        }
        self._registered_routers.append(router)
    
    def get_module(self, code: str) -> dict:
        """Get module by code."""
        return self.modules.get(code)
    
    def get_all_modules(self) -> Dict[str, dict]:
        """Get all registered modules."""
        return self.modules
    
    def get_routers(self) -> List[APIRouter]:
        """Get all registered routers for FastAPI."""
        return self._registered_routers
    
    def get_navigation_items(self) -> List[dict]:
        """Get navigation items for all modules."""
        return [
            {
                "code": mod["code"],
                "name": mod["name"],
                "path": mod["path"],
                "icon": mod["icon"],
                "role": mod["role"],
                "color": mod["color"]
            }
            for mod in self.modules.values()
        ]

# Global module registry instance
registry = ModuleRegistry()
