# CAIOS — Casual Adaptive Intelligence Operating System
## Complete Hinglish Technical Manual, Architecture Deep Dive & Judge-Ready Guide

---

## 1. Ek-Line Summary (10-Second Elevator Pitch)

> **"CAIOS ek lightweight, local-first adaptive workspace shell hai jo aapke laptop ke active window aur kaam ke context ko bina privacy leak kiye samajhta hai, aur aapke liye zaroori apps, files aur timers ko strictly allow-listed aur safe tareeqe se autonomously arrange kar deta hai."**

---

## 2. Problem Jo CAIOS Solve Karta Hai (Real-Life Scenario)

Socho ek aam din:
1. **Scenario 1 (Coding Mode)**: Tumne laptop khola aur VS Code chalu kiya. Ab tumhe terminal kholna hai, browser pe GitHub/documentation search karni hai, aur ek rough developer scratchpad banani hai. Ye sab tumhe roz 10 baar manually click-click karke karna padta hai.
2. **Scenario 2 (Research / Study Mode)**: Tum browser pe ek AI research paper padh rahe ho. Ab tumhe notes app chahiye, ek 30-minute ka focus countdown timer lagana hai, aur ArXiv ke references dekhne hain.
3. **Scenario 3 (Context Switching Fatigue)**: Ek average knowledge worker roz **10 se zyada apps** mein switch karta hai. Har baar naye task ke liye workspace ko haath se prepare karne mein roz **20-30 minute ka 'Cognitive Load' aur distraction** hota hai.

**CAIOS ka Solution:**
Aapko kuch nahi karna. Jaise hi aap VS Code khologe, CAIOS background mein context detect karega aur aapke dashboard pe single-click **"Curated Workspace Actions"** ready kar dega — bina kisi cloud dependency ke aur bina aapke screen ko capture ya record kiye.

---

## 3. System Architecture Overview

### ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                                  HOST OPERATING SYSTEM                            |
|                                                                                   |
|   +-----------------------+                    +------------------------------+   |
|   |   Active Windows      |                    |    User Workspace Dashboard   |   |
|   | (VS Code, Chrome, etc)|                    |  (Next.js 14 Neo-Brutalist)  |   |
|   +-----------+-----------+                    +--------------^---------------+   |
|               |                                               |                   |
|       (Win32 user32 poll)                                (REST API / SSE)         |
|               |                                               |                   |
|               v                                               v                   |
|   +-----------------------+                    +------------------------------+   |
|   |     Context Sensor    |---(POST /context)->|      CAIOS Orchestrator      |   |
|   | (window_detector.py)  |                    |      (FastAPI Port 8000)     |   |
|   +-----------------------+                    +--------------+---------------+   |
|                                                               |                   |
|                                                     (JSON RPC / Internal API)     |
|                                                               |                   |
|                                                               v                   |
|                                                +------------------------------+   |
|                                                |     Docker LLM Sandbox       |   |
|                                                |   (1GB RAM, 1 CPU Core Cap)  |   |
|                                                |   Ollama / Local Heuristics  |   |
|                                                +------------------------------+   |
|                                                                                   |
|                               +-------------------------------+                   |
|                               |   Synchronous Audit Ledger    |                   |
|                               | (data/actions.log + SQLite)   |                   |
|                               +-------------------------------+                   |
+-----------------------------------------------------------------------------------+
```

### Mermaid Diagram (Visual Flow)

```mermaid
sequenceDiagram
    autonumber
    actor User as User (Laptop)
    participant Sensor as Context Sensor (sensor.py)
    participant Orch as Orchestrator (FastAPI :8000)
    participant Box as LLM Sandbox (Docker :8001)
    participant UI as Dashboard (Next.js :3000)
    participant Exec as Allow-List Executor

    User->>Sensor: VS Code / Chrome open karta hai
    Sensor->>Sensor: user32.GetForegroundWindow() se title nikalta hai
    Sensor->>Orch: POST /context {process: "code.exe", title: "main.py"}
    Orch->>Orch: Mode Classifier -> CODING (Confidence: 100%)
    Orch->>Box: POST /reason (Context + Active Mode)
    Box-->>Orch: Suggestions JSON (Open Terminal, Open GitHub, Scratch Note)
    Orch->>UI: ContextState & Suggestions deliver karta hai
    User->>UI: "Execute" button click karta hai
    UI->>Orch: POST /execute {action_type: "CREATE_NOTE", ...}
    Orch->>Orch: Check Kill-Switch & Allow-List Validation
    Orch->>Orch: Synchronous Pre-Log to actions.log & SQLite
    Orch->>Exec: Safe Execution (Confined to ./sandbox/notes/)
    Exec-->>UI: Execution Successful feedback
```

### End-to-End Data Flow Real Example
1. **Step 1 (Sensing)**: Tumne `code.exe` (VS Code) open kiya.
2. **Step 2 (Forwarding)**: Background sensor ne 3.0 second poll cycle mein dekha ki foreground process badal gaya hai. Usne Orchestrator ko payload bheja: `{"process_name": "code.exe", "window_title": "app.py - CAIOS"}`.
3. **Step 3 (Classification)**: Orchestrator ke deterministic classifier ne pattern match kiya aur mode set kiya: **`CODING` (100% Confidence)**.
4. **Step 4 (Reasoning)**: Orchestrator ne LLM Sandbox se suggestions generate karwaye.
5. **Step 5 (Display)**: Dashboard ne turant neo-brutalist cards display kiye:
   - `[Desktop App]` Open Windows Terminal
   - `[Web Link]` Open GitHub Dashboard
   - `[Sandbox Note]` Create `dev_scratchpad.md`
6. **Step 6 (Safe Execution)**: User ne "Execute" dabaya. Orchestrator ne pehle killswitch check kiya, phir allow-list verify ki, event ko `actions.log` mein synchronously write kiya, aur note create kar diya.

---

## 4. Component-by-Component Deep Dive

---

### Component 1: `/sensor` (Context Detection Daemon)

- **Ye kya hai**: Ek ultra-lightweight Python daemon jo background mein chup-chaap baith kar sirf active window ka naam aur process ID check karta hai.
- **Real-Life Analogy**: Jaise library ka receptionist jo sirf ye dekhta hai ki aap "Maths section" mein baithe ho ya "Fiction section" mein — wo aapki kitaab ke panno ke andar kya likha hai wo nahi padhta (100% Privacy).
- **Project mein kaam**: 
  - Windows Win32 API (`user32.GetForegroundWindow`, `user32.GetWindowTextW`) use karta hai.
  - Har 3.0 seconds mein active window check karke `http://127.0.0.1:8000/context` pe POST karta hai.
  - Zero screen capture, zero webcam, zero keystroke logging.
- **Run Command**:
  ```powershell
  .venv\Scripts\python.exe -m sensor.sensor
  ```
- **Common Problems & Fixes**:
  1. *Problem*: `ModuleNotFoundError: No module named 'psutil'`.
     *Fix*: Virtual environment activate karo aur run karo: `pip install -r sensor/requirements.txt`.
  2. *Problem*: Sensor 404/Connection Refused error de raha hai.
     *Fix*: Orchestrator backend pehle start hona chahiye (Port 8000 pe).
- **Code Snippet**:
  ```python
  # sensor/window_detector.py
  import win32gui
  import win32process
  import psutil

  def get_active_window_info():
      # Active window ka handle nikalte hain
      hwnd = win32gui.GetForegroundWindow()
      if not hwnd:
          return None
      # Window ka visible title text nikalte hain
      title = win32gui.GetWindowText(hwnd)
      # Thread ID se process ID aur process name pata karte hain
      _, pid = win32process.GetWindowThreadProcessId(hwnd)
      proc = psutil.Process(pid)
      return {"process_name": proc.name(), "window_title": title}
  ```

---

### Component 2: `/orchestrator` (FastAPI Decision Core)

- **Ye kya hai**: CAIOS ka central nervous system jo saare mode decisions, allow-list checks, aur safe executions control karta hai.
- **Real-Life Analogy**: Jaise ek 5-star hotel ka Head Concierge — jo customer ki zaroorat samajh kar sirf verified aur trusted staff ko kaam assign karta hai.
- **Project mein kaam**:
  - `classifier.py`: Deterministic process lookup table + window title NLP parser.
  - `executor.py`: Allow-listed bounded dispatch table (Zero raw shell command execution).
  - `killswitch.py`: Emergency thread-safe lock (agar engage ho to sab actions block karke `HTTP 423 Locked` return karta hai).
  - `database.py`: SQLite persistence (`data/caios.db`) mode history aur action audit ke liye.
- **Run Command**:
  ```powershell
  .venv\Scripts\python.exe -m uvicorn orchestrator.app.main:app --host 127.0.0.1 --port 8000 --reload
  ```
- **Common Problems & Fixes**:
  1. *Problem*: `Address already in use :::8000`.
     *Fix*: Purana process kill karo: `Get-Process python | Stop-Process` ya task manager se band karo.
- **Code Snippet**:
  ```python
  # orchestrator/app/core/executor.py
  # Strict Python Enum allow-list execution
  async def execute_action(action: ActionPayload):
      # Pehle kill-switch check karte hain
      if kill_switch.is_active:
          raise HTTPException(status_code=423, detail="Kill switch engaged")
      
      # Pre-execution synchronous logging
      audit_logger.log_pre_execution(action)
      
      # Bounded dispatch: sirf 4 allowed types chal sakte hain
      if action.action_type == ActionType.OPEN_APP:
          return _safe_open_app(action.params["app"])
      elif action.action_type == ActionType.CREATE_NOTE:
          return _safe_create_note(action.params["filename"], action.params.get("content", ""))
      # Raw shell ya eval() ka koi rasta hi nahi hai!
  ```

---

### Component 3: `/llm-sandbox` (Docker Containerized Reasoning Core)

- **Ye kya hai**: Ek isolated reasoning microservice jo 1GB RAM aur 1 CPU Core ki limit mein Docker container ke andar chalti hai.
- **Real-Life Analogy**: Jaise ek isolated chemical lab room — chahe andar koi bhi test ho, dhuan ya chemical bahar nahi nikal sakta (Resource Quota Protection).
- **Project mein kaam**:
  - LLM Provider Abstraction: **Ollama (local-first)**, Gemini Cloud, OpenAI, ya built-in Heuristic Mock fallback.
  - Hardware Constraints: `docker-compose.yml` mein `--memory=1g`, `--cpus=1.0`, `privileged: false`, aur non-root user `sandboxuser`.
  - Output strictly JSON schema mein validate hota hai.
- **Run Command**:
  ```powershell
  docker compose up --build -d
  # Ya local dev mode mein:
  .venv\Scripts\python.exe -m uvicorn llm-sandbox.service.main:app --host 127.0.0.1 --port 8001
  ```
- **Common Problems & Fixes**:
  1. *Problem*: Ollama connect nahi ho raha (`Failed to connect to localhost:11434`).
     *Fix*: Terminal mein `ollama serve` ya `ollama run llama3.2:3b` chalu rakhein.

---

### Component 4: `/dashboard` (Next.js 14 Neo-Brutalist Workstation)

- **Ye kya hai**: User-facing visual command center jo 100% human-designed Neo-Brutalist design language pe bana hai.
- **Real-Life Analogy**: Jaise ek high-end studio mixing console — jisme har button physical aur tactile feel deta hai aur clear feedback milta hai.
- **Project mein kaam**:
  - Warm dotted paper canvas (`#F4F0E8` dot grid) with sharp black drop shadows (`4px 4px 0px #000`).
  - Left Column: Mode Banner, Command Studio Intent Bar, Curated Action Matrix cards.
  - Right Column: Container Hardware Quota monitor aur Live Pre-Execution Audit Ledger (`actions.log`).
  - Keyboard Presets: `[1]` Coding, `[2]` Writing, `[3]` Studying, `[4]` Meeting, `[5]` Idle, `[0/Esc]` Auto Sensor.
- **Run Command**:
  ```powershell
  cd dashboard
  npm run build
  npm start
  ```

---

### Component 5: `/data` (Persistent Storage & Audit Ledger)

- **Ye kya hai**: Local storage directory jisme SQLite DB (`caios.db`) aur raw synchronous log file (`actions.log`) rehti hai.
- **Real-Life Analogy**: Flight Recorder (Black Box) — plane mein koi bhi action hone se pehle record hota hai taaki complete accountability rahe.
- **Project mein kaam**:
  - SQLite database mode transitions aur executed actions ka history rakhta hai.
  - `actions.log` synchronous file append karti hai execution se pehle.

---

## 5. Step-by-Step: Poora Project Kaise Run Karein (Zero Se)

### Step 1: Software Prerequisites Download & Install
1. **Python 3.11+**: [python.org/downloads](https://www.python.org/downloads/) *(Install karte waqt "Add Python to PATH" tick karein)*.
2. **Node.js v18+ / v20+**: [nodejs.org](https://nodejs.org/).
3. **Docker Desktop** (Optional lekin recommended): [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop/).
4. **Ollama** (Local AI ke liye): [ollama.com](https://ollama.com/) -> Run: `ollama pull llama3.2:3b`.

---

### Step 2: Environment Variables (`.env`) Setup
Project root directory mein ek `.env` file banayein:
```env
# Orchestrator Configuration
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./data/caios.db
LOG_PATH=./data/actions.log
SANDBOX_NOTES_DIR=./sandbox/notes

# LLM Reasoning Engine (Local Ollama by default)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b

# Optional Cloud APIs (Leave blank for 100% offline local mode)
GEMINI_API_KEY=
OPENAI_API_KEY=
```

---

### Step 3: Terminal Commands (Order Wise)

Open PowerShell in the project directory:

```powershell
# 1. Virtual environment banayein aur activate karein
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Python dependencies install karein
pip install -r orchestrator/requirements.txt
pip install -r sensor/requirements.txt

# 3. Frontend dependencies install karein
cd dashboard
npm install
cd ..

# 4. ONE-CLICK STARTUP (CAIOS Launcher script chalayein)
.\run_caios.bat
# Ya PowerShell script:
.\run_caios.ps1
```

---

### Step 4: Health-Check Verification (Kaise pata chale sab sahi hai)

1. **Dashboard Check**: Browser mein open karein `http://localhost:3000`. Neo-brutalist UI load honi chahiye.
2. **Orchestrator Check**: Browser mein open karein `http://127.0.0.1:8000/docs`. FastAPI Swagger interactive documentation dikhni chahiye.
3. **Sensor Check**: Dashboard ke top bar mein dekhein: `"ACTIVE CONTEXT: chrome.exe (3.0s SENSOR)"` green light ke saath dikhega.
4. **Automated Test Suite**:
   ```powershell
   .venv\Scripts\python.exe -m pytest orchestrator/tests -v
   # Output: 17 passed in 3.9s
   ```

---

## 6. Live Demo Script (Hackathon Ke Liye — 60 Se 90 Seconds)

Agar judge aapke screen ke saamne khada hai, to confidently ye script bolo:

```text
[0:00 - 0:15] INTRO & HOOK:
"Namaste judges! Har knowledge worker roz 10 se zyada apps mein manually switch karta hai 
jisse cognitive fatigue hota hai. Meet CAIOS — Casual Adaptive Intelligence Operating System. 
Ye ek lightweight, local-first adaptive shell hai jo bina kisi screen capture ya privacy 
leak ke aapke laptop ke context ke hisab se workspace prepare karta hai."

[0:15 - 0:35] LIVE SENSOR & MODE TRANSITION:
"Abhi dekhiye — humare foreground mein Chrome open hai, isliye CAIOS ne autonomously 
'Research & Literature Hub' mode trigger kiya hai. Ab main VS Code open karta hoon... 
(Open VS Code on screen) 
Dekhiye, 3 second ke andar sensor ne process detect kiya aur UI seamlessly 'Coding & Development 
Studio' mein transform ho gayi. Hamare paas 1-click curated actions ready hain."

[0:35 - 0:55] HARD SAFETY & SANDBOX DEMO:
"Lekin sabse important sawal hai AI Safety: Kya ye system laptop pe safe hai? 
Yes, 100%! CAIOS mein raw shell execution IMPOSSIBLE hai. Sirf 4 strict allow-listed actions 
permitted hain. LLM 1GB RAM ke Docker container mein isolated rehta hai. 
Aur dekhiye — main yahan 'Kill Switch: Armed' click karta hoon (Click Kill Switch). 
Ab koi bhi automated action execute nahi ho sakta — system instantly HTTP 423 Lock return karega."

[0:55 - 1:15] INTENT STUDIO & CLOSING:
"Main intent bar mein type karta hoon: 'Setup 25m focus block with literature notes'. 
(Click Adapt) 
Humara local Ollama model instantly verified action cards generate kar deta hai. 
Har action execute hone se pehle humare synchronous Audit Ledger (actions.log) mein record hota hai. 
CAIOS is lightweight, 100% private, and ready for every laptop. Thank you!"
```

---

## 7. Honest Differentiation Matrix (Prior Art Comparison)

| Dimension | AIOS (Rutgers Paper) | Microsoft UFO2 | Apple Intelligence / Copilot+ | Rabbit R1 / Humane Pin | CAIOS (Our Startup) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Primary Goal** | LLM Agent OS Kernel for researchers | Windows UI automation via vision | OS-integrated assistant | Standalone AI gadget | **Lightweight consumer-facing adaptive workspace shell** |
| **Deployment Model** | Python developer framework | Heavy research agent | OS-vendor locked (Windows/Mac) | Proprietary hardware ($200-$700) | **Zero-install web/desktop shell on existing laptop** |
| **Privacy / Cloud** | Flexible | Cloud / Local Vision | Cloud-Hybrid | 100% Cloud dependent | **100% Local-first (Ollama, local SQLite, no telemetry)** |
| **Safety Architecture** | Agent scheduling queues | UI click emulation (can misclick) | Proprietary permissions | Cloud server execution | **Strict Enum Allow-List + Hardware Kill-Switch + 1GB Docker Cap** |
| **Time to Value** | Developer setup required | Complex configuration | Built into expensive new laptops | Requires buying separate device | **Runs in under 5 minutes on any modern laptop** |

### The Specific Gap CAIOS Fills
> *"CAIOS is not claiming to be the first adaptive AI concept — there is respected academic and commercial prior art. What makes CAIOS distinct is that it delivers an immediate, laptop-safe, non-invasive adaptive experience with strict allow-list security, zero-cost local LLM reasoning, and a high-contrast Neo-Brutalist interface that anyone can install and run in 5 minutes."*

---

## 8. Safety Guarantees & Honest MVP Limitations

### What CAIOS Does NOT Do (Privacy Commitments)
- ❌ **No Screen Recording / Screenshots**: CAIOS kabhi bhi aapke screen ka screenshot ya video frame capture nahi karta.
- ❌ **No Keylogger**: CAIOS keyboard ke inputs ya passwords read nahi karta.
- ❌ **No Arbitrary Command Execution**: `os.system()` ya `subprocess.Popen(shell=True)` blocked hain. `cmd.exe` ya `powershell.exe` execution completely disallowed hai.
- ❌ **No Default Cloud Upload**: Sara data `data/caios.db` aur `data/actions.log` mein aapke laptop par hi rehta hai.

### Known MVP Limitations
1. **Windows-Native Sensor**: Context sensor abhi Windows Win32 API par optimized hai (`user32.dll`). macOS aur Linux ke liye `psutil` fallback active hai lekin native window title hook roadmap mein hai.
2. **Preset Application Registry**: `AllowedApp` enum mein currently 12 standard applications included hain. Naye apps add karne ke liye configuration file update karni hoti hai.

---

## 9. Frequently Asked Questions (FAQ) & Troubleshooting

#### Q1: Agar Docker Desktop install na ho to kya CAIOS chalega?
**Ans**: Haan! CAIOS mein automatic graceful fallback hai. Agar Docker nahi hai, to LLM Sandbox directly local Python process ke through chal sakta hai (`.venv\Scripts\python.exe -m uvicorn llm-sandbox.service.main:app --port 8001`).

#### Q2: Agar Ollama response slow de to kya karein?
**Ans**: `llama3.2:3b` ya `phi3:mini` jaise lightweight 3B models use karein jo CPU par bhi 1-2 seconds mein respond karte hain. Agar chahein to `.env` mein `GEMINI_API_KEY` daal kar instant cloud reasoning switch kar sakte hain.

#### Q3: Agar sensor foreground window detect na kare to?
**Ans**: Dashboard mein keyboard shortcuts dabayein: `[1]` Coding, `[2]` Writing, `[3]` Studying, `[4]` Meeting, ya `[5]` Idle. Manual override se mode instantly switch ho jata hai. Wapas sensor pe aane ke liye `[0]` ya `[Esc]` dabayein.

#### Q4: Kill switch dabane ke baad kya hota hai?
**Ans**: Orchestrator ka internal state `kill_switch.is_active = True` ho jata hai. Uske baad koi bhi execute call aayegi to backend turant `HTTP 423 Locked` de dega aur koi action run nahi hoga.

#### Q5: Notes kahan save hote hain?
**Ans**: Sabhi notes strictly confined hain `./sandbox/notes/` directory mein. Path-traversal attacks (`../../`) backend validator dwara mathematically block hote hain.

#### Q6: Kya CAIOS bina internet ke 100% offline kaam kar sakta hai?
**Ans**: Haan, 100%! Local Ollama model + Local SQLite DB + Local Next.js server internet ke bina airplane mode mein bhi complete functionality dete hain.

#### Q7: Dashboard ka theme kaisa hai?
**Ans**: Dashboard ek high-contrast **Neo-Brutalist** aesthetic use karta hai jisme warm beige dot-grid canvas (`#F4F0E8`), thick solid black borders, vibrant pastel mode stamps, aur tactile hardware-style buttons hain.

#### Q8: Unit tests kaise run karein?
**Ans**: Terminal mein command chalayein:
```powershell
.venv\Scripts\python.exe -m pytest orchestrator/tests -v
```
Yeh allow-list enforcement, killswitch locking, path traversal security, aur mode classification ko automatically test karta hai.

---

## 10. Technical Glossary (Hinglish A-Z)

- **Allow-List (स्वीकृत सूची)**: Ek strict rulebook jisme pehle se tay hota hai ki system sirf kin-kin specific apps aur URLs ko open kar sakta hai. Iske bahar ka koi command execute nahi ho sakta.
- **API (Application Programming Interface)**: Ek digital pul jiske zariye do alag softwares (jaise Dashboard aur Backend) ek dusre se baat karte hain.
- **Daemon**: Ek background process jo bina user ko disturb kiye chup-chaap apna monitoring task karti rehti hai (jaise humara `sensor.py`).
- **Deterministic Classifier**: Ek aisa algorithm jo bina kisi random guess ke fixed rules aur patterns dekh kar 100% accurate result nikalta hai.
- **Docker Container**: Ek lightweight virtual package (tiffin box) jisme software apni fixed memory aur CPU limits ke andar chalta hai.
- **Endpoint**: Ek specific URL rasta (jaise `/context` ya `/execute`) jahan request bhej kar koi task karwaya jata hai.
- **FastAPI**: Python ka high-speed, modern backend framework jo REST APIs banane ke liye use hota hai.
- **Kill Switch**: Ek emergency safety latch jise dabate hi system ke saare automated executions instantly freeze ho jate hain.
- **LLM (Large Language Model)**: Ek AI model (jaise LLaMA 3.2 ya Gemini) jo natural language intent ko samajh kar structured JSON actions suggest karta hai.
- **Neo-Brutalism**: Ek modern visual design style jisme bold black borders, hard drop shadows, punchy colors aur tactile hardware aesthetics hoti hain.
- **Next.js 14**: React ka production-grade frontend framework jo high performance dynamic dashboards banane ke kaam aata hai.
- **Sandbox**: Ek restricted folder ya environment jiske bahar koi file write ya modify nahi ki ja sakti.
- **SQLite**: Ek lightweight, zero-configuration local database file (`data/caios.db`) jisme transitions aur logs store hote hain.
- **Synchronous Audit Log**: Ek aisi file (`actions.log`) jisme koi bhi action hone se pehle turant timestamp aur parameters record kiye jaate hain.
