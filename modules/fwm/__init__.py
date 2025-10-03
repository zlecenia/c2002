from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Setup templates directory
templates_dir = Path("pages/fwm")
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/fleet-workshop-manager", response_class=HTMLResponse)
async def fleet_workshop_manager_page(request: Request):
    """Render Fleet Workshop Manager page"""
    return templates.TemplateResponse("index.html", {"request": request})