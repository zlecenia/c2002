"""
Fleet Software Manager Module (FSM)
Manages device software, versions, and installations
"""
from fastapi import APIRouter

# Module metadata
MODULE_CODE = "fsm"
MODULE_NAME = "Fleet Software Manager"
MODULE_ROLE = "maker"
MODULE_ICON = "💿"
MODULE_COLOR = "#27ae60"
MODULE_PATH = "/fleet-software-manager"

# Create module router
router = APIRouter(prefix="/fleet-software-manager", tags=["Fleet Software Manager"])
