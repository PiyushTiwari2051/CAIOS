import threading
from ..config import settings

class KillSwitchManager:
    """Thread-safe manager for the global CAIOS emergency kill switch."""
    
    def __init__(self, initial_state: bool = False):
        self._is_active = initial_state
        self._lock = threading.Lock()

    @property
    def is_active(self) -> bool:
        with self._lock:
            return self._is_active

    def set_active(self, active: bool) -> bool:
        with self._lock:
            self._is_active = active
            return self._is_active

    def toggle(self) -> bool:
        with self._lock:
            self._is_active = not self._is_active
            return self._is_active

# Global singleton
kill_switch = KillSwitchManager(initial_state=settings.KILL_SWITCH_DEFAULT)
