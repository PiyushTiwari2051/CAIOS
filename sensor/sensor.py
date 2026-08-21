import time
import sys
import os
from pathlib import Path

# Add sensor directory to sys.path
SENSOR_DIR = Path(__file__).resolve().parent
if str(SENSOR_DIR) not in sys.path:
    sys.path.insert(0, str(SENSOR_DIR))

# Ensure utf-8 standard stream handling on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import httpx
from dotenv import load_dotenv

# Load environment
BASE_DIR = SENSOR_DIR.parent
load_dotenv(BASE_DIR / ".env")

from window_detector import get_current_active_window

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", f"http://127.0.0.1:{os.getenv('PORT_ORCHESTRATOR', '8000')}")
POLL_INTERVAL_SECONDS = float(os.getenv("SENSOR_POLL_INTERVAL", "1.5"))

def run_sensor():
    print("=" * 60)
    print("  CAIOS Context Sensor (Lightweight Background Daemon)")
    print(f"  Target Orchestrator: {ORCHESTRATOR_URL}")
    print(f"  Polling Interval:    {POLL_INTERVAL_SECONDS}s")
    print("  Privacy Guarantee:   Zero screen capture, zero keylogging")
    print("=" * 60)

    last_process = None
    last_title = None

    client = httpx.Client(timeout=5.0)

    try:
        while True:
            proc_name, title = get_current_active_window()
            
            # Print update if context shifted
            if proc_name != last_process or title != last_title:
                clean_title = (title or "")[:50]
                print(f"\n[Context Shift] Process: {proc_name} | Window: {clean_title}", flush=True)
                last_process = proc_name
                last_title = title

            payload = {
                "process_name": proc_name,
                "window_title": title,
                "platform": sys.platform
            }

            try:
                resp = client.post(f"{ORCHESTRATOR_URL}/context", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    mode_info = data.get("current_mode", {})
                    mode_name = mode_info.get("mode", "UNKNOWN")
                    confidence = mode_info.get("confidence", 1.0)
                    is_override = mode_info.get("is_manual_override", False)
                    override_tag = " [MANUAL OVERRIDE]" if is_override else ""
                    print(f"  -> Mode: {mode_name} ({confidence*100:.0f}% conf){override_tag}", end="\r", flush=True)
                else:
                    print(f"  -> Orchestrator HTTP Error: {resp.status_code}", end="\r", flush=True)
            except httpx.ConnectError:
                print("  -> Waiting for CAIOS Orchestrator on localhost...", end="\r", flush=True)
            except Exception as e:
                print(f"  -> Sync Error: {e}", end="\r", flush=True)

            time.sleep(POLL_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\nCAIOS Context Sensor stopped by user.", flush=True)
    finally:
        client.close()

if __name__ == "__main__":
    run_sensor()
