# CAIOS — Casual Adaptive Intelligence Operating System
> **A local-first, containerized adaptive workspace shell.**  
> *Senses context, reshapes tools, protects your hardware.*

👉 **[📖 Hinglish Technical Manual & Judge's Guide (Full Documentation)](./USER_GUIDE.md)**

---

## 1. Problem Statement: The Fragmented Workflow Crisis

Modern knowledge workers and developers suffer from **context-switch fatigue**, juggling 10+ disjointed applications for a single task with zero shared contextual awareness. Meanwhile, conventional OS desktops remain static—the taskbar and workspace look identical whether you are writing code, authoring a research paper, or in a live client meeting. Existing automation tools (Shortcuts, Zapier) require rigid, pre-programmed rules and lack ambient intent perception.

---

## 2. Competitive Wedge: How CAIOS Differs from Prior Art

| Approach | Category / Scope | Key Limitation | CAIOS Advantage |
|---|---|---|---|
| **AIOS** (Rutgers, 2024) | LLM Agent OS Kernel | Complex infrastructure designed for *agent developers*, not end users | **Consumer-facing adaptive shell** installed directly on existing laptops |
| **UFO2** (Microsoft Research) | Desktop Windows Agent | Heavyweight UI automation targeting dev research | **Lightweight meta-layer** with bounded allow-listed actions |
| **Copilot+ / Apple Intelligence** | Big Tech OS Features | Cloud-hybrid, vendor-locked, privacy-invasive screen recall | **100% Local-first, OS-agnostic**, zero cloud telemetry required |
| **Rabbit R1 / Humane Pin** | Standalone AI Hardware | Proprietary hardware, cloud-dependent, high failure rate | **Software-only**, runs safely on the laptop you already own |

**Our Defensible Gap:** CAIOS is **NOT** a new OS kernel and requires **NO** specialized hardware. It is an **OS-agnostic, local-first supervisory shell** that reads lightweight, privacy-preserving signals (active window title/process name, time of day) and adaptively suggests and executes allow-listed actions without screen capture or keylogging.

---

## 3. Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────┐
│  HOST MACHINE (Laptop Safe — Unsafe commands physically impossible)   │
│                                                                        │
│   ┌──────────────────────┐        ┌────────────────────────────────┐   │
│   │ Context Sensor       │───────▶│ CAIOS Orchestrator (FastAPI)   │   │
│   │ (sensor.py - native) │  HTTP  │ - Rule & Heuristic Classifier  │   │
│   │ psutil + win32 api   │        │ - Allow-List Action Executor   │   │
│   └──────────────────────┘        │ - SQLite State & Audit Logger  │   │
│                                   │ - Emergency Kill Switch        │   │
│                                   └──────────────┬─────────────────┘   │
│                                                  │ HTTP (port 8001)    │
│                                   ┌──────────────▼─────────────────┐   │
│                                   │ DOCKER LLM-SANDBOX             │   │
│                                   │ - Memory Limit: 1GB (hard cap) │   │
│                                   │ - CPU Limit: 1.0 core          │   │
│                                   │ - Unprivileged, No Host FS     │   │
│                                   │ - Only ./sandbox mounted       │   │
│                                   │ - Output: Strict JSON Schema   │   │
│                                   └────────────────────────────────┘   │
│   ┌─────────────────────────────┐                ▲                     │
│   │ CAIOS Dashboard (Next.js)   │────────────────┘                     │
│   │ - Live Mode Indicator       │                                      │
│   │ - 1-Click Action Execution  │                                      │
│   │ - Audit Log & Kill Switch   │                                      │
│   └─────────────────────────────┘                                      │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. Hard Safety Constraints (Baked into Code)

1. **Docker Sandbox Quotas**: LLM reasoning runs in a container limited to `--memory=1g`, `--cpus=1.0`, `privileged: false`, with only `./sandbox` mounted.
2. **Strict Python Enum Allow-List**: LLM output is strictly validated against `ActionType` (`OPEN_APP`, `OPEN_URL`, `CREATE_NOTE`, `SET_REMINDER`). Raw shell commands and unrecognized executables (`cmd`, `powershell`, `rm`) are rejected at the validator layer.
3. **Audit Trail**: Every single action is logged to `data/actions.log` and SQLite **BEFORE** execution occurs.
4. **Emergency Kill Switch**: High-visibility hardware/UI stop switch halts all pending executions with `HTTP 423 Locked`.
5. **Zero Invasive Surveillance**: No screen recording, no webcam access, no keylogging. Only active foreground window title and executable name are polled.

---

## 5. Quick Start (Run in Under 2 Minutes)

### Step 1: Clone & Configure
```bash
cp .env.example .env
```

### Step 2: Start Services

**Option A: Using Docker Compose (Recommended for Judges)**
```bash
# Starts LLM Sandbox container with 1GB RAM / 1 Core CPU quota
docker compose up -d
```

**Option B: Local / Offline Mode**
```bash
# In terminal 1: Start Orchestrator
.venv\Scripts\python.exe -m uvicorn orchestrator.app.main:app --host 127.0.0.1 --port 8000

# In terminal 2: Start LLM Sandbox service
.venv\Scripts\python.exe -m uvicorn llm-sandbox.service.main:app --host 127.0.0.1 --port 8001

# In terminal 3: Start Web Dashboard
cd dashboard && npm run dev

# In terminal 4: Start Active Context Sensor
.venv\Scripts\python.exe sensor/sensor.py
```

Open Dashboard at: **`http://localhost:3000`**

---

## 6. 60-Second Hackathon Live Demo Script

Follow these steps for a guaranteed high-impact presentation:

| Time | Action | What the Judge Sees | What to Say |
|---|---|---|---|
| **0:00 - 0:15** | Open Dashboard (`http://localhost:3000`) with VS Code in background. | Dashboard glows **Emerald ("CODING Mode — 98% Confidence")**. Suggestions show GitHub, Terminal, and Dev Scratchpad. | *"CAIOS automatically detects I am in VS Code without screen recording or cloud telemetry, and proactively sets up my coding workspace."* |
| **0:15 - 0:30** | Click **"Execute"** on *Create Dev Scratchpad*. | File is created inside `./sandbox/notes/`. Audit table updates instantly. | *"Every action is restricted to an allow-list enum. Notice the audit log recorded this to actions.log before execution."* |
| **0:30 - 0:45** | Switch to Word or click **"Writing"** preset / type in prompt *"Start literature review"*. | Dashboard morphs instantly to **Purple ("Writing & Docs Mode")** with draft templates and focus timer. | *"When intent shifts, the entire shell adaptively reconfigures itself in real-time."* |
| **0:45 - 0:60** | Click the red **"KILL SWITCH"** button and try to click Execute. | Dashboard pulses red: **"HALTED"**. Action execution is locked (`HTTP 423`). | *"Safety is guaranteed by architecture, not promises. The kill switch and Docker 1GB/1-Core sandbox prevent any runaway loops or unauthorized commands."* |

---

## 7. Automated Test Suite

Run unit and integration tests verifying allow-list enforcement, mode classification, and API security:
```bash
.venv\Scripts\python.exe -m pytest orchestrator/tests -v
```
*(17 passing unit tests covering allow-list rejection, path traversal prevention, kill switch behavior, and mode inference).*
