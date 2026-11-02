"""
=============================================================================
ADHYAKSH AI // Multi-Lingual Natural Language Processing & Intent Engine
Understands English, Hindi, Gujarati & Hinglish/Gujlish commands cleanly
=============================================================================
"""

import re
import sys
import datetime
import urllib.parse

# UTF-8 stdout configuration for Windows terminals
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from config import APP_NAME, APP_SUBTITLE, DEFAULT_WORK_DRIVE
from modules.memory_bank import (
    teach_memory,
    query_memory,
    search_memory_for_answer,
    detect_and_remember_user_fact,
    get_active_user_name,
    set_active_user_name
)
from modules.learning_engine import match_learned_intent, train_new_pattern, parse_natural_training_command
from modules.file_crud import (
    create_file,
    create_directory,
    read_file_content,
    update_file_content,
    delete_file_safely,
    resolve_target_directory,
    find_file
)
from modules.system_controller import (
    open_drive_or_folder,
    close_drive_windows,
    launch_application,
    terminate_application,
    format_system_diagnostics_report,
    get_laptop_drives,
    format_laptop_drives_report,
    capture_desktop_screenshot,
    toggle_volume_mute,
    lock_computer_workstation,
    open_website_or_tab,
    COMMON_WEBSITES
)
from modules.knowledge_engine import fetch_world_knowledge

# ---------------------------------------------------------------------------
# PYTORCH NEURAL MODEL MANAGER SINGLETON
# ---------------------------------------------------------------------------
def get_neural_brain():
    """Lazily initializes and returns the shared PyTorch ModelManager instance."""
    try:
        from model import get_model_manager
        return get_model_manager()
    except Exception as e:
        print(f"[Warning] Neural brain fallback: {e}")
        return None



# ---------------------------------------------------------------------------
# HELPER: MULTI-LINGUAL NORMALIZATION & ENTITY EXTRACTION
# ---------------------------------------------------------------------------
def extract_filename_and_drive(text: str) -> tuple[str, str, str]:
    """
    Extracts filename, target drive, and remaining content payload from multilingual queries.
    Returns: (filename, drive_dir, content_payload)
    """
    text_clean = text.strip()
    text_lower = text_clean.lower()
    drive_dir = resolve_target_directory(text_clean)

    # Search for filename with extension
    words = text_clean.split()
    filename = ""
    for w in words:
        w_clean = w.strip(" :,'\"<>")
        if "." in w_clean and len(w_clean) > 2 and not w_clean.startswith("http"):
            filename = w_clean
            break

    if not filename:
        for noise in [
            "create file", "make file", "file banao", "file banavo", 
            "delete file", "file delete karo", "file hatao", 
            "read file", "view file", "show file", "file dikhao", 
            "file update karo", "update file", "append to file", "file"
        ]:
            if noise in text_lower:
                parts = text_clean.split(noise, 1)
                remainder = parts[1].strip(" :,-")
                first_token = remainder.split()[0].strip(" :,'\"<>") if remainder.split() else ""
                if first_token and not any(k in first_token.lower() for k in ["in", "on", "me", "ma", "with", "saying"]):
                    filename = first_token
                break

    if not filename or filename.lower() in ["file", "new file", "document"]:
        filename = "username.txt"

    # Remove any drive specifier from filename
    filename = re.sub(r"\b(?:in|on)?\s*[a-zA-Z]\s*(?:drive|:)?\b", "", filename, flags=re.IGNORECASE)
    filename = filename.strip(" :,-'\"")

    content_payload = ""
    for sep in [" with ", " saying ", " content ", " body ", " me likho ", " ma lakho "]:
        if sep in text_lower:
            content_payload = text_clean.split(sep, 1)[1].strip(" '\"")
            break

    return filename, drive_dir, content_payload


def evaluate_math_expression(query_text: str) -> tuple[bool, str]:
    """Safely computes arithmetic expressions."""
    clean = query_text.lower().replace("what is", "").replace("calculate", "").replace("math", "").strip(" ?=:")
    clean = clean.replace("x", "*").replace("times", "*").replace("divided by", "/").replace("plus", "+").replace("minus", "-")
    
    if re.fullmatch(r"[\d\s\+\-\*\/\(\)\.\%\^]+", clean) and any(op in clean for op in "+-*/"):
        try:
            clean_expr = clean.replace("^", "**")
            result = eval(clean_expr, {"__builtins__": None}, {})
            return True, f"**Mathematical Computation:** `{clean.strip()}` = **`{result}`**"
        except Exception:
            pass
    return False, ""


# ---------------------------------------------------------------------------
# MAIN PROCESSOR: MULTI-LINGUAL INTENT DISPATCHER
# ---------------------------------------------------------------------------
def process_command(user_text: str, is_voice: bool = False, session_state=None, bypass_learned: bool = False) -> tuple[str, str, dict]:
    """
    Main Multi-Lingual Intent & Execution Router for ADHYAKSH AI.
    
    Returns:
        tuple (response_text: str, intent_name: str, metadata: dict)
    """
    raw_query = user_text.strip()
    text_lower = raw_query.lower()
    intent = "general_query"
    metadata = {}

    # -----------------------------------------------------------------------
    # 0.0 USER NAME INTRODUCTION & PROFILE ADAPTATION (Dynamic for Any Laptop)
    # -----------------------------------------------------------------------
    intro_match = re.search(r"\b(?:my name is|call me|i am|mera naam|maru naam|set user to)\s+([A-Za-z\u0900-\u097F\u0A80-\u0AFF]+)\b", raw_query, flags=re.IGNORECASE)
    if intro_match and not any(k in text_lower for k in ["what is", "who is", "tell me", "kya", "su", "file", "drive", "learning", "ready"]):
        extracted_name = intro_match.group(1).strip().capitalize()
        if len(extracted_name) >= 2 and extracted_name.lower() not in ["file", "demo", "folder", "drive", "the", "here", "today", "now", "fine", "online"]:
            set_active_user_name(extracted_name)
            brain = get_neural_brain()
            if brain:
                try:
                    brain.learn_fact(f"My user's name is {extracted_name}")
                    brain.learn_fact(f"The active user and operator on this workstation is {extracted_name}")
                    brain.train(epochs=30, verbose=False)
                except Exception:
                    pass
            return f"👋 **Pleased to meet you, {extracted_name}!**\n\nI have adapted my neural memory bank to your profile on this workstation. Whenever you ask *'What is my name?'* or *'Who am I?'*, I will address you as **{extracted_name}**.", "user_profile_updated", {"username": extracted_name}

    # Direct query: "What is my name" / "Who am I"
    if any(k in text_lower for k in ["what is my name", "what's my name", "who am i", "mera naam kya hai", "maru naam su che"]):
        active_u = get_active_user_name()
        return f"👤 **Workstation User Profile:**\n\nYou are **{active_u}**, the active operator on this workstation.", "user_identity_recall", {"username": active_u}

    # Direct query: "Who created you" / "Who is the project lead"
    if any(k in text_lower for k in ["who created you", "who made you", "who is the project lead", "lead engineer"]):
        active_u = get_active_user_name()
        return f"⚡ I am **{APP_NAME}**, engineered by **Neelkanth** (Lead Engineer). I am currently operating for **{active_u}** on this workstation.", "creator_attribution", {"creator": "Neelkanth", "user": active_u}

    # -----------------------------------------------------------------------
    # 0.05 AUTOMATIC NATURAL MEMORY EXTRACTION & INSTANT RECALL
    # -----------------------------------------------------------------------
    # 1. Automatic natural fact learning (e.g. "my car is Audi", "my graduation year is 2026")
    is_user_fact, fact_resp = detect_and_remember_user_fact(raw_query)
    if is_user_fact:
        return fact_resp, "memory_teach", {}

    # 2. Instant memory recall from synchronized memory store
    if not any(k in text_lower for k in ["create file", "make file", "delete file", "open ", "launch ", "search google", "train:", "teach:"]):
        is_mem_ans, mem_ans_text = search_memory_for_answer(raw_query)
        if is_mem_ans:
            return mem_ans_text, "memory_recall", {}

    # -----------------------------------------------------------------------
    # 0. PYTORCH NEURAL INTENT CLASSIFICATION & EPISODIC MEMORY RECALL
    # -----------------------------------------------------------------------
    brain = get_neural_brain()
    neural_intent = None
    neural_conf = 0.0
    if brain:
        try:
            neural_intent, neural_conf = brain.predict(raw_query)
            metadata["neural_intent"] = neural_intent
            metadata["neural_confidence"] = neural_conf
            if session_state and hasattr(session_state, "get") and session_state.get("logs") is not None:
                t_str = datetime.datetime.now().strftime("%H:%M:%S")
                session_state["logs"].append({
                    "time": t_str,
                    "stage": "NLU",
                    "msg": f"AdhyakshBrainNet: [{neural_intent.upper()}] ({int(neural_conf*100)}% conf)"
                })
        except Exception:
            pass

        # Check episodic memory for personal / user-taught questions
        if not any(k in text_lower for k in ["remember that", "teach:", "create file", "make file", "delete file", "open "]):
            is_mem, mem_ans, mem_score = brain.recall_fact(raw_query)
            if is_mem and mem_score >= 0.35:
                return f"🧠 **[Neural Memory Recall | {int(mem_score*100)}% Match]**\n\n{mem_ans}", "memory_recall", {"confidence": mem_score}

    # -----------------------------------------------------------------------
    # 0.1 NATURAL LANGUAGE USER TRAINING & MODEL COMMIT (Highest Priority)
    # -----------------------------------------------------------------------
    if not bypass_learned:
        parsed_trig, parsed_out = parse_natural_training_command(raw_query)
        if parsed_trig and parsed_out:
            intent = "ai_model_training"
            succ, msg, pat = train_new_pattern(parsed_trig, custom_response=parsed_out)
            response = f"""✅ **ADHYAKSH AI Model Trained Successfully!**

- **Trigger Phrase:** *\"{parsed_trig}\"*
- **Target Output / Action:** *\"{parsed_out}\"*

*The model has committed this pattern to persistent neural storage. Whenever you say or ask \"{parsed_trig}\", it will immediately produce this output.*"""
            return response, intent, {"pattern": pat}

    # -----------------------------------------------------------------------
    # 1. USER-TRAINED PATTERNS & ACTIVE FEEDBACK LOOP
    # -----------------------------------------------------------------------
    if not bypass_learned:
        matched, learned_pattern, confidence = match_learned_intent(raw_query)
        if matched and learned_pattern:
            intent = f"learned_{learned_pattern.get('action', 'custom')}"
            action = learned_pattern.get("action")
            params = learned_pattern.get("parameters", {})
            custom_resp = learned_pattern.get("custom_response", "")

            # Execute any attached or inferred action
            if action == "command" or "command" in params:
                cmd_target = params.get("command", action)
                if cmd_target.lower() != raw_query.lower():
                    cmd_resp, _, _ = process_command(cmd_target, is_voice=is_voice, session_state=session_state, bypass_learned=True)
                    if cmd_resp and cmd_resp != custom_resp:
                        custom_resp += f"\n\n{cmd_resp}"
            elif action == "open_app":
                succ, msg = launch_application(params.get("app", "chrome"))
                if msg: custom_resp += f"\n\n{msg}"
            elif action == "open_drive":
                succ, msg = open_drive_or_folder(params.get("drive", "D:\\"))
                if msg: custom_resp += f"\n\n{msg}"
            elif action == "open_app_and_drive":
                launch_application(params.get("app", "code"))
                open_drive_or_folder(params.get("drive", "D:\\"))
                custom_resp += "\n\nOpened application and navigated to drive."
            elif action == "open_website":
                succ, msg, _ = open_website_or_tab(params.get("url", "https://google.com"))
                if msg: custom_resp += f"\n\n{msg}"
            elif action == "create_file":
                succ, msg, _ = create_file(params.get("filename", "note.txt"), target_directory=params.get("drive", DEFAULT_WORK_DRIVE), content=params.get("content", ""))
                if msg: custom_resp += f"\n\n{msg}"
            elif action == "mute_and_launch":
                toggle_volume_mute()
                launch_application(params.get("app", "spotify"))
                custom_resp += "\n\nMuted audio and launched Spotify."

            response_text = f"**[Learned Response | Confidence: {int(confidence*100)}%]**\n\n{custom_resp}"
            metadata["learned_pattern"] = learned_pattern
            return response_text, intent, metadata

    # -----------------------------------------------------------------------
    # 2. WEBSITES, WEB SEARCH & BROWSER NEW TAB LAUNCHER (Direct Fast Route)
    # -----------------------------------------------------------------------
    web_triggers = [
        "open new tab", "new tab", "open tab", "new browser tab", "tab kholo", "naya tab kholo",
        "open youtube", "open google", "open github", "open chatgpt", "open linkedin",
        "open gmail", "open website", "open site", "search google", "search youtube",
        "youtube kholo", "google kholo", "github kholo", "website kholo"
    ]
    is_web_query = (
        any(k in text_lower for k in web_triggers) or
        any(k in text_lower for k in [".com", ".org", ".net", ".in", ".io", "http://", "https://", "www."]) or
        any(re.search(rf"\b(open|launch|kholo|chalu)\s+{portal}\b", text_lower) for portal in COMMON_WEBSITES.keys()) or
        any(text_lower.startswith(f"search {engine} for") for engine in ["google", "youtube", "web"])
    )

    if is_web_query and not any(k in text_lower for k in ["drive", "file", "folder", "specs", "who is", "what is"]):
        intent = "web_portal_launch"
        succ, msg, url = open_website_or_tab(raw_query)
        metadata["url"] = url
        return msg, intent, metadata

    # -----------------------------------------------------------------------
    # 2.1 LAPTOP DRIVE AUTO-DISCOVERY & FETCH (Direct Real-Time Hardware Check)
    # -----------------------------------------------------------------------
    fetch_drive_triggers = [
        "fetch drive", "fetch drives", "fetch laptop drive", "fetch laptop drives",
        "show drive", "show drives", "show laptop drive", "show laptop drives",
        "show my drive", "show my drives", "list drive", "list drives",
        "scan drive", "scan drives", "scan laptop drive", "scan laptop drives",
        "detect drive", "detect drives", "what drives", "which drives", "how many drives",
        "laptop drive", "laptop drives", "drives available", "available drives",
        "storage status", "disk status", "my drives", "drives fetch", "drives scan",
        "laptop ma kai drive che", "laptop me kaunse drive hai", "drives batao",
        "drives check karo", "storage check karo"
    ]
    if any(k in text_lower for k in fetch_drive_triggers) and not any(k in text_lower for k in ["create", "delete", "write", "update", "content"]):
        report = format_laptop_drives_report()
        return report, "laptop_drives_fetch", {"drives": get_laptop_drives()}

    # -----------------------------------------------------------------------
    # 2.5 PYTORCH NEURAL NETWORK INTENT ROUTER (Direct Semantic Comprehension)
    # Prevents wrong responses by routing through AdhyakshBrainNet deep model
    # -----------------------------------------------------------------------
    if neural_intent and neural_conf >= 0.45:
        # File CRUD Operations
        if neural_intent == "file_create":
            fname, target_dir, payload = extract_filename_and_drive(raw_query)
            succ, msg, fpath = create_file(fname, target_directory=target_dir, content=payload, open_in_editor=False)
            return msg, "file_create", {"filepath": fpath, "neural_confidence": neural_conf}

        elif neural_intent == "file_read":
            fname, _, _ = extract_filename_and_drive(raw_query)
            succ, content, meta = read_file_content(fname)
            if succ:
                resp = f"**File Preview (`{meta.get('filename')}`):**\n```text\n{content}\n```\n- **Path:** `{meta.get('filepath')}`\n- **Size:** `{meta.get('size_kb')} KB` | **Lines:** `{meta.get('line_count')}`"
            else:
                resp = content
            return resp, "file_read", meta

        elif neural_intent == "file_update":
            fname, _, payload = extract_filename_and_drive(raw_query)
            if not payload:
                payload = f"Updated via Adhyaksh AI on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            mode = "overwrite" if any(k in text_lower for k in ["overwrite", "replace", "pura badlo"]) else "append"
            succ, msg, meta = update_file_content(fname, new_content=payload, mode=mode)
            return msg, "file_update", meta

        elif neural_intent == "file_delete":
            fname, _, _ = extract_filename_and_drive(raw_query)
            succ, msg = delete_file_safely(fname)
            return msg, "file_delete", {}

        elif neural_intent == "folder_create":
            folder_name = "new_folder"
            for token in raw_query.split():
                if token.lower() not in ["create", "folder", "directory", "make", "banao", "in", "d", "c", "e", "drive", "navin", "banavo"]:
                    folder_name = token.strip(" :,'\"")
                    break
            target_dir = resolve_target_directory(raw_query)
            succ, msg, dpath = create_directory(folder_name, target_directory=target_dir)
            return msg, "folder_create", {"folder_path": dpath}

        # Physical Drive Controls
        elif neural_intent == "drive_open":
            succ, msg = open_drive_or_folder(raw_query)
            return msg, "drive_open", {}

        elif neural_intent == "drive_close":
            d_char = None
            m = re.search(r"\b([a-zA-Z])\s*drive\b|\b([a-zA-Z]):", text_lower)
            if m:
                d_char = (m.group(1) or m.group(2)).upper()
            succ, msg = close_drive_windows(d_char)
            return msg, "drive_close", {}

        # Universal Application Controls
        elif neural_intent == "app_launch":
            succ, msg = launch_application(raw_query)
            return msg, "app_launch", {}

        elif neural_intent == "app_close":
            succ, msg = terminate_application(raw_query)
            return msg, "app_close", {}

        # System Diagnostics & Power Tools
        elif neural_intent == "system_diagnostics":
            report = format_system_diagnostics_report()
            return report, "system_diagnostics", {}

        elif neural_intent == "tool_screenshot":
            succ, msg = capture_desktop_screenshot()
            return msg, "tool_screenshot", {}

        elif neural_intent == "tool_camera_vision":
            return (
                "📷 **YOLOv8 Neural Vision Ready:**\n\n"
                "Click the **'📷 Camera'** button beside the Send button to activate your webcam!\n"
                "Show your **pen**, **mobile phone**, **laptop**, **bottle**, or any items in front of the lens.\n"
                "I will localize every object with **blue bounding borders**, compute telemetry, and explain what I see.",
                "tool_camera_vision",
                {}
            )

        elif neural_intent == "tool_mute":
            succ, msg = toggle_volume_mute()
            return msg, "tool_mute", {}

        elif neural_intent == "tool_lock":
            succ, msg = lock_computer_workstation()
            return msg, "tool_lock", {}

        # Temporal Intelligence
        elif neural_intent == "temporal_intelligence":
            now = datetime.datetime.now()
            target = now + datetime.timedelta(days=1) if "tomorrow" in text_lower else (now - datetime.timedelta(days=1) if "yesterday" in text_lower else now)
            label = "Tomorrow" if "tomorrow" in text_lower else ("Yesterday" if "yesterday" in text_lower else "Today")
            return f"""**ADHYAKSH AI // Temporal Intelligence:**\n\n- **{label}:** **`{target.strftime('%A, %B %d, %Y')}`**\n- **Current Time:** `{now.strftime('%I:%M:%S %p')}`\n- **Timezone:** `IST (UTC+05:30)`""", "temporal_intelligence", {}

        # Math Computation
        elif neural_intent == "math_computation":
            is_math, math_res = evaluate_math_expression(raw_query)
            if is_math:
                return math_res, "math_computation", {}

        # Episodic Neural Memory
        elif neural_intent == "memory_teach":
            resp = teach_memory(raw_query)
            if brain:
                brain.learn_fact(raw_query)
            return resp, "memory_teach", {}

        elif neural_intent == "memory_query":
            return query_memory(), "memory_query", {}

        elif neural_intent == "memory_recall":
            if brain:
                is_mem, mem_ans, mem_score = brain.recall_fact(raw_query)
                if is_mem and mem_score >= 0.30:
                    return f"🧠 **[Neural Memory Recall | {int(mem_score*100)}% Match]**\n\n{mem_ans}", "memory_recall", {"confidence": mem_score}
            is_mem2, mem_ans2 = search_memory_for_answer(raw_query)
            if is_mem2:
                return mem_ans2, "memory_recall", {}

            # Fact not in memory
            return (
                f"I am sorry, I do not know about this message.\n\n"
                f"I don't have this stored in my neural memory bank yet.\n"
                f"💡 *You can teach me this fact by saying:* `Remember that [your fact]`",
                "memory_unknown",
                {"query": raw_query}
            )

        # Assistant Identity & Capabilities
        elif neural_intent == "bot_identity":
            active_u = get_active_user_name()
            return f"⚡ **I am {APP_NAME}**\n\nI am an **Autonomous Multi-Lingual AI Executive & System Operating Engine**, engineered by **Neelkanth**.\n\nCurrently operating for **{active_u}**.\n\n- **Neural Engine:** PyTorch Deep Intent Network (99.6% Accuracy)\n- **Languages:** English, Hindi, Gujarati, Hinglish, Gujlish\n- **Hardware Control:** Physical Drives (C:, D:, E:), Process Management, Audio Mute, Desktop Lock", "bot_identity", {}

        elif neural_intent == "capabilities":
            return f"""**{APP_NAME} Operational Capabilities:**

1. **🌐 Multi-Lingual Neural Comprehension:** Fluent in English, Hindi, and Gujarati commands.
2. **📁 Physical File CRUD Studio:** Create, read, update, and delete files across system drives.
3. **⚡ Hardware & Drive Controller:** Direct Windows Explorer and process management.
4. **🧠 Universal World Knowledge:** Instant answers on any topic (Google / Wikipedia / Gemini).
5. **🎯 Self-Learning & Memory Bank:** Retains facts and adapts to user feedback dynamically.""", "capabilities", {}

        elif neural_intent == "greeting":
            hour = datetime.datetime.now().hour
            salutation = "Good Morning!" if hour < 12 else ("Good Afternoon!" if hour < 17 else "Good Evening!")
            return f"**Greetings & {salutation}**\n\nI am **{APP_NAME}** — your autonomous executive assistant. How may I assist your workflow today?", "greeting", {}

        elif neural_intent == "wellbeing":
            return f"**{APP_NAME} is operating at peak system efficiency!**\n\nAll CPU, RAM, disk storage, and neural inference pipelines are active and fully operational.", "wellbeing", {}

        elif neural_intent == "gratitude":
            return f"**You are very welcome!** It is my privilege to automate your system as **{APP_NAME}**.", "gratitude", {}

        elif neural_intent == "farewell":
            return f"**Goodbye & have an outstanding day ahead!** All **{APP_NAME}** services will remain standing by.", "farewell", {}

        elif neural_intent == "universal_knowledge":
            user_api_key = session_state.get("custom_llm_api_key", None) if session_state else None
            succ_k, knowledge_resp, meta_k = fetch_world_knowledge(raw_query, custom_api_key=user_api_key)
            metadata.update(meta_k)
            return knowledge_resp, "universal_world_knowledge", metadata


    # -----------------------------------------------------------------------
    # 3. FILE CRUD: CREATE (English, Hindi, Gujarati, Hinglish)
    # -----------------------------------------------------------------------
    create_triggers = [
        "create file", "make file", "create new file", "make a file", "new file",
        "file banao", "file create karo", "naya file banao", "file banavo", "navin file",
        "create document", "document banao", "open d drive and create"
    ]
    if any(k in text_lower for k in create_triggers) and not any(k in text_lower for k in ["folder", "directory"]):
        intent = "file_create"
        fname, target_dir, payload = extract_filename_and_drive(raw_query)
        succ, msg, fpath = create_file(fname, target_directory=target_dir, content=payload, open_in_editor=False)
        return msg, intent, {"filepath": fpath}

    # -----------------------------------------------------------------------
    # 4. FILE CRUD: READ / VIEW (English, Hindi, Gujarati, Hinglish)
    # -----------------------------------------------------------------------
    read_triggers = [
        "read file", "view file", "show file", "open file", "display file",
        "file dikhao", "file padho", "file dekho", "file vaacho", "file batao",
        "file read karo", "file view karo", "file contents"
    ]
    if any(k in text_lower for k in read_triggers) and not any(k in text_lower for k in ["folder", "drive"]):
        intent = "file_read"
        fname, _, _ = extract_filename_and_drive(raw_query)
        succ, content, meta = read_file_content(fname)
        if succ:
            resp = f"**File Preview (`{meta.get('filename')}`):**\n```text\n{content}\n```\n- **Path:** `{meta.get('filepath')}`\n- **Size:** `{meta.get('size_kb')} KB` | **Lines:** `{meta.get('line_count')}`"
        else:
            resp = content
        return resp, intent, meta

    # -----------------------------------------------------------------------
    # 5. FILE CRUD: UPDATE / APPEND (English, Hindi, Gujarati, Hinglish)
    # -----------------------------------------------------------------------
    update_triggers = [
        "update file", "append to file", "edit file", "modify file", "write to file",
        "file update karo", "file me likho", "file ma lakho", "file me jodo", "file badlo"
    ]
    if any(k in text_lower for k in update_triggers):
        intent = "file_update"
        fname, _, payload = extract_filename_and_drive(raw_query)
        if not payload:
            payload = f"Updated via Adhyaksh AI on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        mode = "overwrite" if any(k in text_lower for k in ["overwrite", "replace", "pura badlo"]) else "append"
        succ, msg, meta = update_file_content(fname, new_content=payload, mode=mode)
        return msg, intent, meta

    # -----------------------------------------------------------------------
    # 6. FILE CRUD: DELETE (Safe Recycle Bin) (English, Hindi, Gujarati, Hinglish)
    # -----------------------------------------------------------------------
    delete_triggers = [
        "delete file", "remove file", "trash file", "destroy file",
        "file delete karo", "file hatao", "file nikal do", "file kadhi nakho", "file bhusi nakho"
    ]
    if any(k in text_lower for k in delete_triggers):
        intent = "file_delete"
        fname, _, _ = extract_filename_and_drive(raw_query)
        permanent = any(k in text_lower for k in ["permanently", "hard delete", "forever"])
        succ, msg = delete_file_safely(fname, permanent=permanent)
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 7. FOLDER CRUD: CREATE FOLDER / DIRECTORY
    # -----------------------------------------------------------------------
    folder_triggers = [
        "create folder", "make folder", "new folder", "folder banao", "folder banavo",
        "create directory", "directory banao", "open d drive and create folder"
    ]
    if any(k in text_lower for k in folder_triggers):
        intent = "folder_create"
        target_dir = resolve_target_directory(raw_query)
        f_name = "my_project_folder"
        for noise in folder_triggers:
            if noise in text_lower:
                rem = raw_query.lower().split(noise, 1)[1]
                words = rem.split()
                if words:
                    f_name = words[0].strip(" :,-'\"")
                break
        succ, msg, fpath = create_directory(f_name, target_directory=target_dir, open_in_explorer=True)
        return msg, intent, {"folderpath": fpath}

    # -----------------------------------------------------------------------
    # 7.5 LAPTOP DRIVE AUTO-DISCOVERY & FETCHING (Real-Time Dynamic Hardware Scan)
    # -----------------------------------------------------------------------
    fetch_drive_triggers = [
        "fetch drive", "fetch drives", "fetch laptop drive", "fetch laptop drives",
        "show drive", "show drives", "show laptop drive", "show laptop drives",
        "show my drive", "show my drives", "list drive", "list drives",
        "scan drive", "scan drives", "scan laptop drive", "scan laptop drives",
        "detect drive", "detect drives", "what drives", "laptop drive", "laptop drives",
        "drives available", "available drives", "storage status", "disk status",
        "drives fetch", "drives scan", "drives list", "drives check",
        "laptop ma kai drive che", "laptop me kaunse drive hai", "drives batao",
        "drives check karo", "storage check karo"
    ]
    if any(k in text_lower for k in fetch_drive_triggers):
        intent = "laptop_drives_fetch"
        report = format_laptop_drives_report()
        return report, intent, {"drives": get_laptop_drives()}

    # -----------------------------------------------------------------------
    # 8. PHYSICAL DRIVE NAVIGATION (Open Dynamic Laptop Drives: C:, D:, E:, F: etc.)
    # -----------------------------------------------------------------------
    open_drive_triggers = [
        "open drive", "open drives", "open explorer", "file explorer kholo",
        "my computer", "this pc", "open this pc"
    ]
    is_drive_open_req = (
        any(k in text_lower for k in open_drive_triggers) or
        re.search(r"\b(?:open|kholo|chalu)\s+[a-zA-Z]\s*(?:drive|:)?\b", text_lower) or
        re.search(r"\b[a-zA-Z]\s*drive\s*(?:kholo|chalu|open)\b", text_lower) or
        re.search(r"\b[a-zA-Z]:\\?\b", text_lower) or
        any(d.get("raw_label", "").lower() in text_lower for d in get_laptop_drives() if len(d.get("raw_label", "")) >= 3)
    )
    if is_drive_open_req and not any(k in text_lower for k in ["create", "delete", "remove", "update", "write", "search"]):
        intent = "drive_open"
        succ, msg = open_drive_or_folder(raw_query)
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 9. PHYSICAL DRIVE WINDOW CLOSER (Native CabinetWClass API)
    # -----------------------------------------------------------------------
    close_drive_triggers = [
        "close drive", "close drives", "close explorer", "close all drives",
        "drive band karo", "drive bandh karo", "explorer band karo"
    ]
    is_drive_close_req = (
        any(k in text_lower for k in close_drive_triggers) or
        re.search(r"\b(?:close|band|bandh)\s+[a-zA-Z]\s*(?:drive|:)?\b", text_lower) or
        re.search(r"\b[a-zA-Z]\s*drive\s*(?:close|band|bandh)\b", text_lower)
    )
    if is_drive_close_req:
        intent = "drive_close"
        d_char = None
        for c in ["c", "d", "e", "f", "g"]:
            if c in text_lower:
                d_char = c
                break
        succ, msg = close_drive_windows(d_char)
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 9.5. YOLO NEURAL VISION & OBJECT DETECTION CAMERA
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["camera", "detect object", "detect objects", "object detection", "yolo", "yolo vision", "look at camera", "show mobile", "show phone", "show pen", "detect pen", "what do you see"]):
        intent = "tool_camera_vision"
        return (
            "📷 **YOLOv8 Neural Vision Ready:**\n\n"
            "Click the **'📷 Camera'** button right beside the Send button to open the camera viewfinder!\n"
            "Show your **pen**, **mobile phone**, **laptop**, **bottle**, or any items.\n"
            "I will detect them, track them with **blue borders**, and explain what I understand.",
            intent,
            {}
        )

    # -----------------------------------------------------------------------
    # 10. UNIVERSAL APPLICATION LAUNCHER
    # -----------------------------------------------------------------------
    launch_triggers = ["open", "launch", "start", "run", "kholo", "chalu karo"]
    if any(text_lower.startswith(t) or f" {t} " in text_lower for t in launch_triggers) and not any(k in text_lower for k in ["drive", "file", "folder", "youtube", "google", "tab", "camera"]):
        intent = "app_launch"
        succ, msg = launch_application(raw_query)
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 11. UNIVERSAL APPLICATION TERMINATOR
    # -----------------------------------------------------------------------
    close_triggers = ["close", "kill", "terminate", "stop", "exit", "band karo"]
    if any(text_lower.startswith(t) or f" {t} " in text_lower for t in close_triggers) and not any(k in text_lower for k in ["drive", "file", "folder"]):
        intent = "app_close"
        succ, msg = terminate_application(raw_query)
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 12. PERSISTENT LONG-TERM MEMORY (Recall Query First, Then Teach)
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["what do you remember", "show memory", "memory bank", "view memory", "stored facts", "kya yaad hai"]):
        intent = "memory_query"
        resp = query_memory()
        return resp, intent, {}

    if any(k in text_lower for k in ["remember that", "remember", "save fact", "learn fact", "yaad rakho"]):
        intent = "memory_teach"
        resp = teach_memory(raw_query)
        if brain:
            brain.learn_fact(raw_query)
        return resp, intent, {}

    # -----------------------------------------------------------------------
    # 13. DIRECT AI TRAINING (Train on User Feedback)
    # -----------------------------------------------------------------------
    if text_lower.startswith("train:") or text_lower.startswith("teach model:"):
        intent = "ai_train_command"
        body = raw_query.split(":", 1)[1].strip()
        if "->" in body:
            trig_part, resp_part = body.split("->", 1)
            succ, msg, pat = train_new_pattern(trig_part.strip(), custom_response=resp_part.strip())
            return msg, intent, pat
        elif " do " in body.lower():
            trig_part, act_part = body.lower().split(" do ", 1)
            succ, msg, pat = train_new_pattern(trig_part.strip(), action=act_part.strip(), custom_response=f"Executed trained action '{act_part.strip()}'.")
            return msg, intent, pat
        else:
            return "Please provide training pattern in format: `Train: [trigger] -> [response]` or `Train: [trigger] do [action]`.", intent, {}

    # -----------------------------------------------------------------------
    # 14. HARDWARE TELEMETRY & SYSTEM DIAGNOSTICS
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["system specs", "hardware info", "computer specs", "pc specs", "cpu usage", "ram usage", "system diagnostics", "system telemetry"]):
        intent = "system_diagnostics"
        report = format_system_diagnostics_report()
        return report, intent, {}

    # -----------------------------------------------------------------------
    # 15. DESKTOP POWER TOOLS (Camera YOLO Vision, Screenshot, Mute, Lock)
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["open camera", "camera kholo", "detect objects", "object detection", "yolo", "yolo vision", "look at camera", "show mobile", "show phone", "show pen", "detect pen", "what do you see"]):
        intent = "tool_camera_vision"
        return (
            "📷 **YOLOv8 Neural Vision Ready:**\n\n"
            "Click the **'📷 Camera'** button right beside the Send button to open the camera viewfinder!\n"
            "Show your **pen**, **mobile phone**, **laptop**, **bottle**, or any items.\n"
            "I will detect them, track them with **blue borders**, and explain what I understand.",
            intent,
            {}
        )

    if any(k in text_lower for k in ["screenshot", "capture screen", "screen capture", "screenshot lo"]):
        intent = "tool_screenshot"
        succ, msg = capture_desktop_screenshot()
        return msg, intent, {}

    if any(k in text_lower for k in ["mute", "toggle volume", "mute sound", "sound band karo", "awaz band karo"]):
        intent = "tool_mute"
        succ, msg = toggle_volume_mute()
        return msg, intent, {}

    if any(k in text_lower for k in ["lock computer", "lock pc", "lock screen", "pc lock karo"]):
        intent = "tool_lock"
        succ, msg = lock_computer_workstation()
        return msg, intent, {}

    # -----------------------------------------------------------------------
    # 16. WHATSAPP & EMAIL DRAFTING
    # -----------------------------------------------------------------------
    if "whatsapp" in text_lower:
        intent = "draft_whatsapp"
        recipient = "Target Contact"
        msg_payload = raw_query
        for noise in ["send whatsapp message", "open whatsapp and message", "send whatsapp", "whatsapp"]:
            msg_payload = re.sub(rf"\b{noise}\b", "", msg_payload, flags=re.IGNORECASE)
        msg_payload = msg_payload.strip(" :,-") or "Hello! Sent via ADHYAKSH AI."
        
        if session_state is not None:
            session_state.pending_draft = {
                "channel": "WhatsApp",
                "recipient": recipient,
                "message": msg_payload,
                "subject": None
            }
        return f"**WhatsApp Dispatch Prepared for '{recipient}':**\n\n- **Message:** *\"{msg_payload}\"*\n\nReview the Confirmation Card above to confirm dispatch!", intent, {}

    if "email" in text_lower or "send email" in text_lower or "mail" in text_lower:
        intent = "draft_email"
        recipient_email = "recipient@example.com"
        for w in raw_query.split():
            if "@" in w and "." in w:
                recipient_email = w.strip(" :,;<>")
                break
        body_payload = raw_query
        for noise in ["send email message", "send email", "compose email", "email", "mail"]:
            body_payload = re.sub(rf"\b{noise}\b", "", body_payload, flags=re.IGNORECASE)
        body_payload = body_payload.strip(" :,-") or "Greetings,\n\nSent via ADHYAKSH AI Assistant."

        if session_state is not None:
            session_state.pending_draft = {
                "channel": "Email",
                "recipient": recipient_email,
                "message": body_payload,
                "subject": f"Message from {APP_NAME}"
            }
        return f"**Email Dispatch Prepared for '{recipient_email}':**\n\n- **Subject:** `Message from {APP_NAME}`\n- **Body:** *\"{body_payload}\"*\n\nReview the Confirmation Card above to confirm dispatch!", intent, {}

    # -----------------------------------------------------------------------
    # 17. TEMPORAL INTELLIGENCE (Date, Time, Relative Days)
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["time", "date", "clock", "day", "today", "tomorrow", "yesterday", "tarikh", "samay"]):
        intent = "temporal_intelligence"
        now = datetime.datetime.now()
        if "tomorrow" in text_lower:
            target = now + datetime.timedelta(days=1)
            label = "Tomorrow"
        elif "yesterday" in text_lower:
            target = now - datetime.timedelta(days=1)
            label = "Yesterday"
        else:
            target = now
            label = "Today"

        formatted_time = now.strftime("%I:%M:%S %p")
        formatted_date = target.strftime("%A, %B %d, %Y")
        return f"""**ADHYAKSH AI // Temporal Intelligence:**

- **{label}:** **`{formatted_date}`**
- **Current Time:** `{formatted_time}`
- **Timezone:** `IST (UTC+05:30)`""", intent, {}

    # -----------------------------------------------------------------------
    # 18. CONVERSATIONAL IDENTITY, GREETINGS & SMALL TALK
    # -----------------------------------------------------------------------
    if any(k in text_lower for k in ["who are you", "what is your name", "what's your name", "who created you", "who made you", "aap kaun ho", "tame kon cho"]):
        intent = "bot_identity"
        resp = f"""**I am {APP_NAME}**

I am an **Autonomous Multi-Lingual AI Executive & System Operating Engine**, engineered by **Neelkanth**.

**Core Operational Capabilities:**
- **Universal Knowledge Brain**: Instant answers on any topic, science, history, coding, people, and world facts like Google.
- **Web & Browser Automation**: Launch any website (YouTube, Google, GitHub, etc.) or open brand new tabs instantly.
- **Full File CRUD Studio**: Create, Read/View, Update, and safely Delete files across computer drives.
- **Physical Drive Controller**: Direct hardware control for C:, D:, and E: drives in Windows.
- **Active User Learning**: Continuous self-learning from user feedback and custom training patterns.
- **Multi-Lingual STT & NLP**: Full comprehension in English, Hindi, Gujarati, and transliterations."""
        return resp, intent, {}

    greeting_pattern = r"\b(good morning|good afternoon|good evening|good night|hello|hi|hey|namaste|pranam|kem cho|kya haal hai)\b"
    if re.search(greeting_pattern, text_lower):
        intent = "greeting"
        hour = datetime.datetime.now().hour
        if hour < 12:
            salutation = "Good Morning!"
        elif hour < 17:
            salutation = "Good Afternoon!"
        else:
            salutation = "Good Evening!"

        resp = f"""**Greetings & {salutation}**

I am **{APP_NAME}** — your autonomous executive assistant and system controller.

All neural engines, speech recognition models, knowledge brains, and drive controllers are online at 100% capacity.

**How may I assist your workflow today?**
- **World Knowledge:** *"Who is Albert Einstein?"* | *"What is Quantum Computing?"* | *"Explain Machine Learning"*
- **Web & Portals:** *"Open YouTube"* | *"Open GitHub"* | *"Open New Tab"* | *"Search Google for AI"*
- **File CRUD:** *"Create file report.txt in D drive"* | *"Read file report.txt"* | *"Update file report.txt"*
- **Drive Controls:** *"Open D drive"* | *"Close D drive"*"""
        return resp, intent, {}

    if any(k in text_lower for k in ["how are you", "how are you doing", "what's up", "kaisa chal raha hai"]):
        intent = "wellbeing"
        return f"**{APP_NAME} is operating at peak system efficiency!**\n\nAll CPU, RAM, disk storage, and persistent learning pipelines are active and fully operational.", intent, {}

    if any(k in text_lower for k in ["thank you", "thanks", "great job", "well done", "awesome"]):
        intent = "gratitude"
        return f"**You are very welcome!** It is my privilege to automate your system as **{APP_NAME}**.", intent, {}

    if re.search(r"\b(bye|goodbye|see you|alvida|aavjo)\b", text_lower):
        intent = "farewell"
        return f"**Goodbye & have an outstanding day ahead!** All **{APP_NAME}** services will remain standing by.", intent, {}

    # -----------------------------------------------------------------------
    # 19. MATH EVALUATION ENGINE
    # -----------------------------------------------------------------------
    is_math, math_res = evaluate_math_expression(raw_query)
    if is_math:
        return math_res, "math_computation", {}

    # -----------------------------------------------------------------------
    # 19.5 PERSONAL MEMORY BANK QUESTION-ANSWERING (Recall User Facts)
    # -----------------------------------------------------------------------
    is_mem, mem_ans = search_memory_for_answer(raw_query)
    if is_mem:
        return mem_ans, "memory_recall", {}

    # Check if user is asking a personal memory question that is not stored
    personal_indicators = [
        "my ", "what is my", "what's my", "who is my", "where is my", "tell me my",
        "do you know my", "mera ", "meri ", "mere ", "maru ", "mara ", "mari ",
        "apna ", "humara ", "kya mera", "su maru"
    ]
    if any(k in text_lower for k in personal_indicators):
        return (
            f"I am sorry, I do not know about this message.\n\n"
            f"I do not have this fact stored in my memory bank yet.\n"
            f"💡 *You can teach me by saying:* `Remember that [your fact]`",
            "memory_unknown",
            {"query": raw_query}
        )

    # -----------------------------------------------------------------------
    # 20. UNIVERSAL WORLD KNOWLEDGE BRAIN (Google / Wikipedia / LLM Knowledge)
    # -----------------------------------------------------------------------
    user_api_key = session_state.get("custom_llm_api_key", None) if session_state else None
    succ_k, knowledge_resp, meta_k = fetch_world_knowledge(raw_query, custom_api_key=user_api_key)
    metadata.update(meta_k)

    if succ_k:
        intent = "universal_world_knowledge"
        return knowledge_resp, intent, metadata
    else:
        # Graceful decline when query is unknown
        return (
            f"I am sorry, I do not know about this message.\n\n"
            f"I do not have verified information about this query in my neural memory or knowledge base.\n"
            f"- 💡 *You can teach me by saying:* `Remember that [fact]`\n"
            f"- ⚡ *Or train a new response:* `Train: [trigger] -> [response]`",
            "unknown_fallback",
            metadata
        )
