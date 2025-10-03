from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Setup templates directory
templates_dir = Path("pages/cd")
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/connect-display", response_class=HTMLResponse)
async def connect_display_page(request: Request):
    """Render Connect Display page"""
    return templates.TemplateResponse("index.html", {"request": request})