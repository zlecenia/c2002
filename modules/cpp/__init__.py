from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Setup templates directory
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

@router.get("/connect-plus", response_class=HTMLResponse)
async def connect_plus_page(request: Request):
    """Render Connect Plus page"""
    return templates.TemplateResponse("index.html", {"request": request})