"""
Fleet Software Manager Module (FSM)
Manages device software, versions, and installations
"""
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Module metadata
MODULE_CODE = "fsm"
MODULE_NAME = "Fleet Software Manager"
MODULE_ROLE = "maker"
MODULE_ICON = "💿"
MODULE_COLOR = "#27ae60"
MODULE_PATH = "/fleet-software-manager"

# Create module router
router = APIRouter(prefix="/fleet-software-manager", tags=["Fleet Software Manager"])

# Setup templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/fleet-software-manager", response_class=HTMLResponse)
async def fleet_software_manager_page(request: Request):
    """Render Fleet Software Manager page"""
    return templates.TemplateResponse("index.html", {"request": request})
