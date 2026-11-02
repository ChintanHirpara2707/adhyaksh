# ⚡ ADHYAKSH AI // Autonomous Multi-Lingual AI Executive & System Operating Engine

A production-grade, modular, and cyber-executive AI operating assistant engineered by **Neelkanth (Lead Engineer)**.

---

## 🏛️ Tri-Section Executive Workspace Architecture

ADHYAKSH AI is structured into **Three Dedicated Core Sections** providing a sleek, specialized user interface and workflow:

### 💬 Section 1: Executive AI & System Controller
- **Unified Multi-Lingual Conversational Interface**: Robust speech-to-text (hardware microphone & zero-latency Web Speech API dictation) paired with natural language understanding across English, Hindi, and Gujarati.
- **Physical Drive & Hardware OS Automation**: Native Windows Explorer control (`D:\`, `C:\`, `E:\`), window closer API, app launching (`VS Code`, `Chrome`, `Spotify`, `Task Manager`), desktop screenshots, and audio controls.
- **Persistent Conversational Memory**: Chat history is persistently saved to disk, ensuring sessions survive browser reloads seamlessly.

### 👁️ Section 2: YOLOv8 Neural Vision Studio
- **Neural Optical Localization**: Real-time webcam snapshot and file upload detection powered by Ultralytics YOLOv8 with high-visibility blue bounding borders.
- **Deep Semantic Scene Breakdown**: Structured entity counting, category pill tags, and scene reasoning narrative.
- **One-Click Studio Actions**: Directly dispatch vision findings to the Executive Chat or commit visual discoveries to Long-Term Memory.

### 🧠 Section 3: Neural Memory Bank & Active Learning Hub
- **Persistent Long-Term Memory Vault**:
  - Automatically extracts and permanently stores user facts, preferences, credentials, and profile attributes.
  - Bidirectional synchronization across `data/memory_bank.json`, `adhyaksh_memory.json`, and PyTorch neural weights.
  - Interactive memory explorer: live search, categorized fact cards, 1-click teach, and fact deletion.
- **AI Training & Active Learning Studio**:
  - Teach custom triggers and actions (App Launch, Drive Navigation, File Creation, Web Launch, Custom Response).
  - Live interactive inference sandbox with real-time confidence scores.
- **Operator Profile & Hardware Diagnostics**:
  - Workstation operator profile manager, language configuration, LLM brain API keys, live CPU/RAM/Disk telemetry, and chat history export.

### 1. 🌐 Multi-Lingual Speech & NLU Comprehension
- Full comprehension across **English (India & Global)**, **Hindi (हिन्दी)**, and **Gujarati (ગુજરાતી)** as well as romanized transliterations (Hinglish/Gujlish).
- **Dual-Engine Speech Recognition**:
  - **Python Robust STT**: Dynamic acoustic sensitivity calibration (`energy_threshold=300`), ambient noise reduction (`adjust_for_ambient_noise`), and auto-cascading language fallback across `en-IN` -> `hi-IN` -> `gu-IN` -> `en-US`.
  - **Zero-Latency Web Speech API**: Client-side browser microphone integration for real-time acoustic transcription without server latency.

### 2. 📁 Full File CRUD Operations Studio
- **Create**: Generate new physical files with custom templates and content directly in specified computer drives (e.g. `D:\`, `C:\`, Project Directory) with automatic launch in Visual Studio Code.
- **Read / View**: Built-in syntax-highlighted code & text viewer with line numbering, file metadata (size, lines, modified date), and binary protection.
- **Update**: Interactive live code/text editor in the UI allowing instantaneous file overwrites or content appends, plus natural voice update commands.
- **Delete**: Safe deletion using `Send2Trash` (recovering accidentally deleted files from Windows Recycle Bin) with optional permanent purge.

### 3. 🧠 Universal World Knowledge Brain (Google / Wikipedia / LLM Intelligence)
- Answers questions on **any topic in the world** (science, history, technology, people, definitions, geography, current facts, and coding concepts).
- **Multi-Tier Knowledge Engine**:
  - **Live Encyclopedia Knowledge Graph**: Real-time Wikipedia & Google search synthesis with zero setup or API keys required.
  - **Generative Neural Brain**: Built-in support for **Google Gemini 1.5 Flash** and **Groq Llama 3.3 70B** with an intuitive in-app API key configuration panel.
- Understands questions across **English, Hindi, and Gujarati**.

### 4. 🎯 Self-Learning & User Feedback Adaptation Engine
- Continuous active learning powered by **scikit-learn `TfidfVectorizer`** and **Cosine Similarity matching**.
- Train new triggers via voice (*"Train: when I say focus do spotify"*) or through the interactive **AI Training & Feedback Studio**.
- One-click feedback correction loop (*"Teach Correction"*) directly from assistant chat messages.
- Real-time inference testing sandbox with live confidence score gauge.

### 5. 👁️ YOLOv8 Neural Computer Vision & Real-time Object Recognition
- Real-time webcam and camera detection powered by **Ultralytics YOLOv8**.
- Localizes and identifies everyday objects: **Mobile Smartphones**, **Laptops**, **Keyboards**, **Bottles**, **People**, **Books**, **Mugs**, and 80+ COCO classes.
- **Deep Semantic Scene Understanding**: Generates natural language analysis of user gestures and objects shown to the camera (e.g. *"I observe you holding a mobile smartphone in front of the camera"*).
- **Spoken Audio Narration**: Automatically speaks out visual findings in real time.

### 6. ⚡ Hardware Drive & OS Process Controller
- **Physical Drive Automation**: Native Windows Explorer control to open physical drives (`C:\`, `D:\`, `E:\`).
- **Windows API Window Closer**: Employs Windows `ctypes.windll.user32` to find and close active `CabinetWClass` drive windows safely.
- **Universal Application Manager**: Launch and terminate processes (Google Chrome, VS Code, Spotify, Notepad, Task Manager, Calculator).
- **Desktop Power Tools**: Full-resolution desktop screenshot capture, master volume mute toggle, and workstation lock.

### 7. 💎 Modular Architecture
```
AI/
├── app.py                      # Main Streamlit Orchestration & UI Layout
├── config.py                   # Global constants, paths, branding, theme configuration
├── requirements.txt            # Package dependencies
├── yolov8n.pt                  # YOLOv8 Neural Vision weights for object detection
├── README.md                   # Documentation & Quickstart
├── data/
│   ├── memory_bank.json        # Persistent user memory & facts
│   └── learned_intents.json    # User training data & feedback patterns
└── modules/
    ├── __init__.py
    ├── speech_engine.py        # Robust multi-lingual STT, signal conditioning, AGC & TTS
    ├── vision_engine.py        # YOLOv8 object detection, bounding box overlay & scene reasoning
    ├── nlp_engine.py           # Multi-lingual intent routing (EN, HI, GU) & entity extraction
    ├── file_crud.py            # Complete CRUD operations (Create, Read, Update, Delete)
    ├── system_controller.py    # Windows drive manager, app launcher, hardware telemetry
    ├── learning_engine.py      # TF-IDF semantic matcher & feedback trainer
    ├── memory_bank.py          # Long-term fact memory store & recall
    └── ui_components.py        # Obsidian glassmorphic CSS, cards & voice orb
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Launch Application
```bash
streamlit run app.py
```

If port `8501` is already occupied:
```bash
streamlit run app.py --server.port 8502
```
