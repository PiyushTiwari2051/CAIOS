from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class ModeEnum(str, Enum):
    CODING = "CODING"
    WRITING = "WRITING"
    STUDYING = "STUDYING"
    MEETING = "MEETING"
    IDLE = "IDLE"

class ModeClassification(BaseModel):
    mode: ModeEnum
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    reasoning: str
    is_manual_override: bool = False
    suggested_apps: List[str] = Field(default_factory=list)
    suggested_shortcuts: List[str] = Field(default_factory=list)
