from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_reasoning(
        self,
        mode: str,
        user_request: Optional[str] = None,
        active_window: Optional[str] = None,
        process_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Returns parsed JSON dictionary with keys 'reasoning' and 'actions'."""
        pass
