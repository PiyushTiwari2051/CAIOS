from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from .mode import ModeEnum, ModeClassification

class ContextPayload(BaseModel):
    process_name: str = Field(default="unknown", description="Active process executable name, e.g. code.exe")
    window_title: str = Field(default="", description="Active window title bar text")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    platform: str = Field(default="windows", description="Host OS platform")

class ContextState(BaseModel):
    current_context: ContextPayload
    current_mode: ModeClassification
    manual_override: Optional[ModeEnum] = None
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    kill_switch_active: bool = False
