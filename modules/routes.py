"""
Module routes configuration
This file imports and configures all module routers for the FastAPI application
"""
from fastapi import FastAPI

# Import module routers
from static.common import router as common_router
from modules.cpp import router as cpp_router
from modules.cd import router as cd_router
from modules.cm import router as cm_router
from modules.fdm import router as fdm_router
from modules.fcm import router as fcm_router
from modules.fsm import router as fsm_router
from modules.fwm import router as fwm_router


def include_module_routes(app: FastAPI):
    """
    Include all module routers in the FastAPI application
    
    Args:
        app: FastAPI application instance
    """
    # Include page routers (no prefix - direct URL mapping)
    app.include_router(common_router, tags=["Home"])
    app.include_router(cpp_router, tags=["Connect Plus"])
    app.include_router(cd_router, tags=["Connect Display"])
    app.include_router(cm_router, tags=["Connect Manager"])
    app.include_router(fdm_router, tags=["Fleet Data Manager"])
    app.include_router(fcm_router, tags=["Fleet Config Manager"])
    app.include_router(fsm_router, tags=["Fleet Software Manager"])
    app.include_router(fwm_router, tags=["Fleet Workshop Manager"])
    
    print("✅ Module routes included successfully")
