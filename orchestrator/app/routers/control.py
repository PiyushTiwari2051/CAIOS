from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from ..models.mode import ModeEnum
from ..core.killswitch import kill_switch
from .context import set_override

router = APIRouter(prefix="", tags=["System Controls"])

class KillSwitchToggleResponse(BaseModel):
    is_active: bool
    message: str

class KillSwitchSetRequest(BaseModel):
    active: bool

class ModeOverrideRequest(BaseModel):
    mode: Optional[ModeEnum] = None

@router.get("/killswitch/status", response_model=KillSwitchToggleResponse)
async def get_killswitch_status():
    active = kill_switch.is_active
    return KillSwitchToggleResponse(
        is_active=active,
        message="Kill switch is ACTIVE (execution disabled)" if active else "Kill switch is INACTIVE (execution enabled)"
    )

@router.post("/killswitch/toggle", response_model=KillSwitchToggleResponse)
async def toggle_killswitch():
    new_state = kill_switch.toggle()
    return KillSwitchToggleResponse(
        is_active=new_state,
        message="Kill switch ACTIVATED (all execution paused)" if new_state else "Kill switch DEACTIVATED (normal operation)"
    )

@router.post("/killswitch/set", response_model=KillSwitchToggleResponse)
async def set_killswitch(req: KillSwitchSetRequest):
    new_state = kill_switch.set_active(req.active)
    return KillSwitchToggleResponse(
        is_active=new_state,
        message="Kill switch set to " + ("ACTIVE" if new_state else "INACTIVE")
    )

@router.post("/mode/override")
async def override_mode(req: ModeOverrideRequest):
    """Sets a manual mode override or clears it if null."""
    mode_classification = set_override(req.mode)
    return {
        "success": True,
        "mode": req.mode.value if req.mode else None,
        "is_override": req.mode is not None,
        "classification": mode_classification
    }

@router.delete("/mode/override")
async def clear_override():
    """Clears the manual mode override, returning to dynamic sensor classification."""
    mode_classification = set_override(None)
    return {
        "success": True,
        "message": "Manual override cleared. Dynamic sensor classification restored.",
        "classification": mode_classification
    }
