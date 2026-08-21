from fastapi import APIRouter, Query
from typing import List, Dict, Any
from ..models.action import ActionLogEntry
from ..core.logger import read_recent_logs
from ..core.database import get_recent_actions, get_recent_modes

router = APIRouter(prefix="", tags=["Actions & Logs"])

@router.get("/log", response_model=List[ActionLogEntry])
async def get_actions_log(limit: int = Query(default=50, ge=1, le=200)):
    """Returns recent entries directly from data/actions.log."""
    return read_recent_logs(limit=limit)

@router.get("/history/actions", response_model=List[Dict[str, Any]])
async def get_action_history(limit: int = Query(default=50, ge=1, le=200)):
    """Returns recent action history from the SQLite database."""
    return get_recent_actions(limit=limit)

@router.get("/history/modes", response_model=List[Dict[str, Any]])
async def get_mode_history(limit: int = Query(default=20, ge=1, le=100)):
    """Returns recent mode transition history from the SQLite database."""
    return get_recent_modes(limit=limit)
