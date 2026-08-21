from fastapi import APIRouter, HTTPException
from datetime import datetime
from typing import Optional

from ..models.context import ContextPayload, ContextState
from ..models.mode import ModeClassification, ModeEnum
from ..core.classifier import classifier
from ..core.database import record_mode_transition
from ..core.killswitch import kill_switch

router = APIRouter(prefix="/context", tags=["Context"])

# In-memory current state cache
_current_context: ContextPayload = ContextPayload(process_name="idle", window_title="Desktop")
_current_mode: ModeClassification = classifier.classify(_current_context)
_manual_override: Optional[ModeEnum] = None

@router.post("", response_model=ContextState)
async def update_context(payload: ContextPayload):
    """
    Receives active window and process context from the sensor.
    Classifies user mode and logs transitions to SQLite.
    """
    global _current_context, _current_mode, _manual_override
    
    _current_context = payload
    new_mode = classifier.classify(payload, manual_override=_manual_override)
    
    # If mode changed or first time, record in SQLite
    if new_mode.mode != _current_mode.mode or _manual_override is not None:
        record_mode_transition(
            mode=new_mode.mode.value,
            confidence=new_mode.confidence,
            process_name=payload.process_name,
            window_title=payload.window_title,
            reasoning=new_mode.reasoning,
            is_manual_override=new_mode.is_manual_override
        )
        
    _current_mode = new_mode
    
    return ContextState(
        current_context=_current_context,
        current_mode=_current_mode,
        manual_override=_manual_override,
        last_updated=datetime.utcnow().isoformat() + "Z",
        kill_switch_active=kill_switch.is_active
    )

@router.get("/current", response_model=ContextState)
async def get_current_context():
    """Returns the current context, detected mode, and kill switch status."""
    global _current_context, _current_mode, _manual_override
    return ContextState(
        current_context=_current_context,
        current_mode=_current_mode,
        manual_override=_manual_override,
        last_updated=datetime.utcnow().isoformat() + "Z",
        kill_switch_active=kill_switch.is_active
    )

def set_override(mode: Optional[ModeEnum]):
    global _manual_override, _current_mode, _current_context
    _manual_override = mode
    _current_mode = classifier.classify(_current_context, manual_override=_manual_override)
    record_mode_transition(
        mode=_current_mode.mode.value,
        confidence=_current_mode.confidence,
        process_name=_current_context.process_name,
        window_title=_current_context.window_title,
        reasoning=_current_mode.reasoning,
        is_manual_override=_current_mode.is_manual_override
    )
    return _current_mode
