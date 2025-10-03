"""
Connect++ (CPP) Main Application
Port: 8080
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import socketio

from .api import test_routes
from .core.config import settings

# Create FastAPI app
app = FastAPI(
    title="Connect++ (CPP)",
    description="Operator module for device testing",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO for real-time communication
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.CORS_ORIGINS
)
socket_app = socketio.ASGIApp(sio, app)

# Include routers
app.include_router(test_routes.router, prefix="/api/v1")

# Health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "module": "Connect++ (CPP)",
        "port": 8080,
        "version": "1.0.0"
    }

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Connect++ (CPP) API",
        "docs": "/docs",
        "health": "/health"
    }

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
    await sio.emit('connection_established', {'sid': sid}, room=sid)

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def sensor_data(sid, data):
    """Receive sensor data from client"""
    print(f"Sensor data from {sid}: {data}")
    # Broadcast to all connected clients
    await sio.emit('sensor_update', data)

# Mount static files (for frontend)
# app.mount("/static", StaticFiles(directory="static"), name="static")
