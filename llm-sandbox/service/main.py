import os
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from .providers import (
    BaseLLMProvider,
    OllamaProvider,
    GeminiCloudProvider,
    OpenAICloudProvider,
    MockHeuristicProvider
)

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("caios.sandbox")

app = FastAPI(
    title="CAIOS LLM Sandbox",
    description="Resource-isolated LLM reasoning service for adaptive workspace suggestions",
    version="0.1.0"
)

class ReasonRequest(BaseModel):
    mode: str = Field(..., description="Current detected mode (CODING, WRITING, etc.)")
    prompt: Optional[str] = Field(None, description="Optional natural language user prompt")
    active_window: Optional[str] = None
    process_name: Optional[str] = None

class ActionItem(BaseModel):
    action_type: str
    title: str
    description: str
    params: Dict[str, Any]
    requires_confirmation: bool = True

class ReasonResponse(BaseModel):
    reasoning: str
    actions: List[ActionItem]
    provider_used: str

def get_provider() -> tuple[BaseLLMProvider, str]:
    provider_name = os.getenv("LLM_PROVIDER", "ollama").lower()
    
    if provider_name == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        return OllamaProvider(base_url=base_url, model=model), f"ollama ({model})"
        
    elif provider_name == "gemini" and os.getenv("GEMINI_API_KEY"):
        return GeminiCloudProvider(api_key=os.getenv("GEMINI_API_KEY")), "gemini-1.5-flash"
        
    elif provider_name == "openai" and os.getenv("OPENAI_API_KEY"):
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAICloudProvider(api_key=os.getenv("OPENAI_API_KEY"), model=model), f"openai ({model})"
        
    # Default/Mock fallback
    return MockHeuristicProvider(), "mock_heuristic"

@app.get("/health")
async def health():
    provider_name = os.getenv("LLM_PROVIDER", "ollama")
    return {"status": "healthy", "provider": provider_name}

@app.post("/reason", response_model=ReasonResponse)
async def reason(request: ReasonRequest):
    """
    Executes reasoning inside the isolated sandbox and returns structured JSON actions.
    """
    provider, name = get_provider()
    
    try:
        data = await provider.generate_reasoning(
            mode=request.mode,
            user_request=request.prompt,
            active_window=request.active_window,
            process_name=request.process_name
        )
    except Exception as e:
        logger.warning(f"Provider '{name}' encountered error: {e}. Falling back to mock heuristic provider.")
        mock_provider = MockHeuristicProvider()
        data = await mock_provider.generate_reasoning(
            mode=request.mode,
            user_request=request.prompt,
            active_window=request.active_window,
            process_name=request.process_name
        )
        name = "mock_heuristic (fallback)"

    raw_actions = data.get("actions", [])
    valid_actions: List[ActionItem] = []
    
    for raw_act in raw_actions:
        try:
            # Ensure required fields exist
            if "action_type" in raw_act and "title" in raw_act and "params" in raw_act:
                valid_actions.append(ActionItem(
                    action_type=raw_act["action_type"],
                    title=raw_act["title"],
                    description=raw_act.get("description", raw_act["title"]),
                    params=raw_act.get("params", {}),
                    requires_confirmation=raw_act.get("requires_confirmation", True)
                ))
        except Exception as ex:
            logger.debug(f"Skipping invalid action schema from LLM: {ex}")

    return ReasonResponse(
        reasoning=data.get("reasoning", "Adaptive workspace actions derived from context."),
        actions=valid_actions,
        provider_used=name
    )
