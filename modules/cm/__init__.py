from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Setup templates directory
templates_dir = Path("pages/cm")
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/connect-manager", response_class=HTMLResponse)
async def connect_manager_page(request: Request):
    """Render Connect Manager page"""
    return templates.TemplateResponse("index.html", {"request": request})