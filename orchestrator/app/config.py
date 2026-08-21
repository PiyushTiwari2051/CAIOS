import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Base Project Root
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings(BaseModel):
    PROJECT_NAME: str = "CAIOS Orchestrator"
    VERSION: str = "0.1.0"
    
    # Network Ports
    PORT_ORCHESTRATOR: int = int(os.getenv("PORT_ORCHESTRATOR", "8000"))
    PORT_DASHBOARD: int = int(os.getenv("PORT_DASHBOARD", "3000"))
    PORT_SANDBOX: int = int(os.getenv("PORT_SANDBOX", "8001"))
    
    # LLM Sandbox / Reasoning URL
    SANDBOX_URL: str = os.getenv("SANDBOX_URL", f"http://127.0.0.1:{os.getenv('PORT_SANDBOX', '8001')}")
    
    # Safety & Storage Paths
    SANDBOX_PATH: Path = BASE_DIR / os.getenv("SANDBOX_PATH", "sandbox")
    ACTIONS_LOG_PATH: Path = BASE_DIR / os.getenv("ACTIONS_LOG_PATH", "data/actions.log")
    DATABASE_PATH: Path = BASE_DIR / os.getenv("DATABASE_PATH", "data/caios.db")
    
    # Default Kill Switch State
    KILL_SWITCH_DEFAULT: bool = os.getenv("KILL_SWITCH_DEFAULT", "false").lower() == "true"

settings = Settings()

# Ensure directories exist
settings.SANDBOX_PATH.mkdir(parents=True, exist_ok=True)
(settings.SANDBOX_PATH / "notes").mkdir(parents=True, exist_ok=True)
settings.ACTIONS_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
settings.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
