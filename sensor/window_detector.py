import sys
import os
import psutil
from typing import Tuple

def get_active_window_windows() -> Tuple[str, str]:
    """
    Retrieves active window title and process name on Windows using Win32 API + psutil.
    Ultra-lightweight, zero invasive hooks, no screen capture.
    """
    try:
        import ctypes
        from ctypes import wintypes

        user32 = ctypes.windll.user32
        
        # Get handle to foreground window
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ("idle", "Desktop / No Active Window")

        # Get window title
        length = user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buff, length + 1)
        title = buff.value.strip()

        # Get process ID from window handle
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        
        process_name = "unknown"
        if pid.value:
            try:
                proc = psutil.Process(pid.value)
                process_name = proc.name().lower()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_name = "system"

        return (process_name, title or "Untitled Window")
        
    except Exception as e:
        return ("unknown", f"Detection error: {e}")

def get_active_window_fallback() -> Tuple[str, str]:
    """Cross-platform fallback for non-Windows or virtual environments."""
    try:
        # Check top CPU process
        for proc in psutil.process_iter(['name']):
            name = proc.info.get('name', '').lower()
            if any(ide in name for ide in ['code', 'cursor', 'pycharm', 'idea']):
                return (name, "Active Development Environment")
            if any(doc in name for doc in ['word', 'notepad', 'notion']):
                return (name, "Document Workspace")
            if any(call in name for call in ['zoom', 'teams', 'slack']):
                return (name, "Communication App")
        return ("idle", "Ambient / Desktop")
    except Exception:
        return ("idle", "Desktop")

def get_current_active_window() -> Tuple[str, str]:
    """Returns (process_name, window_title)."""
    if sys.platform == "win32":
        return get_active_window_windows()
    else:
        return get_active_window_fallback()
