"""
=============================================================================
ADHYAKSH AI // Autonomous Multi-Lingual AI Executive & Operating Engine
Dedicated Direct-Access Modules:
- 💬 Executive AI (Autonomous Executive Chat & Reasoning)
- 🎙️ Voice Studio (Dedicated Voice Cockpit & Neural Speech)
- ⚡ System Controls & Drives (Laptop Drives & Hardware Automation)
- 👁️ YOLOv8 Vision (Spatial Object Detection & Tuning)
- 🧠 Memory & Learning (Neural Memory Bank & Adaptive Training)
=============================================================================
"""

import streamlit as st
import datetime
import urllib.parse
import webbrowser
import os
import json
import time

# Core Configuration & Engine Modules
import config
from modules.speech_engine import (
    transcribe_audio_robust,
    synthesize_speech_wav,
    record_system_mic_direct
)
from modules.nlp_engine import process_command, get_neural_brain
from modules.vision_engine import get_vision_engine
from modules.yolo_trainer import (
    get_yolo_model_status,
    fine_tune_yolo_model,
    reset_to_base_yolo_model
)
from modules.file_crud import (
    create_file,
    read_file_content,
    update_file_content,
    delete_file_safely,
    list_directory_contents,
    resolve_target_directory
)
from modules.system_controller import (
    open_drive_or_folder,
    close_drive_windows,
    launch_application,
    terminate_application,
    get_system_telemetry,
    get_laptop_drives,
    format_laptop_drives_report,
    capture_desktop_screenshot,
    toggle_volume_mute,
    lock_computer_workstation,
    open_website_or_tab,
    COMMON_WEBSITES
)
from modules.learning_engine import (
    get_all_learned_patterns,
    train_new_pattern,
    match_learned_intent,
    delete_learned_pattern,
    get_training_statistics
)
from modules.memory_bank import (
    load_memory,
    save_memory,
    teach_memory,
    query_memory,
    delete_memory,
    get_active_user_name,
    set_active_user_name,
    get_all_memories_list,
    load_chat_history,
    save_chat_history,
    clear_chat_history
)
from modules.ui_components import (
    inject_custom_css,
    render_navbar,
    render_welcome_hero,
    render_activity_logs,
    render_telemetry_summary,
    render_drives_overview
)

# ===========================================================================
# 1. PAGE SETUP & THEME INJECTION
# ===========================================================================
st.set_page_config(
    page_title=f"{config.APP_NAME}",
    page_icon=config.APP_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

inject_custom_css()

# ===========================================================================
# 2. SESSION STATE MANAGEMENT & CHAT PERSISTENCE
# ===========================================================================
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

if "pending_draft" not in st.session_state:
    st.session_state.pending_draft = None

if "logs" not in st.session_state:
    st.session_state.logs = [
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "stage": "STT", "msg": "Speech Engine ready."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "stage": "NLU", "msg": "Semantic Router & Memory Bank ready."},
        {"time": datetime.datetime.now().strftime("%H:%M:%S"), "stage": "EXEC", "msg": f"{config.APP_NAME} operational."},
    ]

if "selected_language" not in st.session_state:
    st.session_state.selected_language = config.DEFAULT_LANGUAGE

if "crud_selected_file" not in st.session_state:
    st.session_state.crud_selected_file = ""

if "feedback_train_prompt" not in st.session_state:
    st.session_state.feedback_train_prompt = ""

if "custom_llm_api_key" not in st.session_state:
    st.session_state.custom_llm_api_key = os.getenv("GEMINI_API_KEY", os.getenv("GROQ_API_KEY", ""))

if "last_processed_audio_bytes" not in st.session_state:
    st.session_state.last_processed_audio_bytes = None

if "pending_query" not in st.session_state:
    st.session_state.pending_query = None

if "memory_search_filter" not in st.session_state:
    st.session_state.memory_search_filter = ""

if "laptop_drives" not in st.session_state:
    st.session_state.laptop_drives = get_laptop_drives()

# Handle Live Dictate voice prompt passed from browser Web Speech API
if "voice_prompt" in st.query_params:
    vp = st.query_params.get("voice_prompt", "")
    st.query_params.clear()
    if vp and vp.strip():
        st.session_state.pending_query = vp.strip()


def add_log(stage: str, msg: str):
    """Appends an event to the session telemetry log."""
    t_stamp = datetime.datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append({"time": t_stamp, "stage": stage, "msg": msg})
    if len(st.session_state.logs) > 40:
        st.session_state.logs.pop(0)


def run_query(prompt_text: str, is_voice: bool = False):
    """Executes a user prompt through the unified NLP router, saving history persistently."""
    if not prompt_text.strip():
        return

    add_log("NLU", f"'{prompt_text.strip()}'")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt_text.strip(),
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    with st.spinner("Processing..."):
        resp_text, intent_name, meta = process_command(
            prompt_text.strip(),
            is_voice=is_voice,
            session_state=st.session_state
        )

    add_log("EXEC", f"{intent_name}")
    st.session_state.messages.append({
        "role": "assistant",
        "content": resp_text,
        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
    })

    save_chat_history(st.session_state.messages)

    if is_voice:
        st.session_state.pending_speech_audio = resp_text[:280]

    st.rerun()


# System state variables
all_memories = load_memory()
fact_count = len(all_memories)
active_user = get_active_user_name()
telemetry = get_system_telemetry()

# ===========================================================================
# 3. SIDEBAR: UNIFIED MODULE EXPANDERS (Direct Names, strictly NO Section 1, 2, 3)
# ===========================================================================
with st.sidebar:
    st.markdown(f"""
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:14px; padding-left:2px;">
            <span style="font-size:20px;">⚡</span>
            <span style="font-weight:700; font-size:16px; color:#f8fafc; letter-spacing:-0.2px;">{config.APP_NAME}</span>
        </div>
    """, unsafe_allow_html=True)

    # 1. Executive AI Expander
    with st.expander("💬 Executive AI", expanded=True):
        c_btn1, c_btn2 = st.columns(2, gap="small")
        with c_btn1:
            if st.button("➕ New Chat", use_container_width=True, key="sb_btn_new_chat"):
                st.session_state.messages = []
                st.session_state.pending_draft = None
                clear_chat_history()
                st.toast("Started new chat", icon="✨")
                st.rerun()
        with c_btn2:
            if st.button("🗑️ Clear", use_container_width=True, key="sb_btn_clear_chat"):
                st.session_state.messages = []
                st.session_state.pending_draft = None
                clear_chat_history()
                st.toast("Chat cleared", icon="🗑️")
                st.rerun()
        st.caption(f"💬 {len(st.session_state.messages)} message(s) in active session")

    # 2. Voice Studio Expander
    with st.expander("🎙️ Voice Studio", expanded=False):
        st.caption("Neural Speech & Hardware Mic:")
        if st.button("🎙️ Push to Speak (5s)", key="sb_btn_studio_pc_mic", use_container_width=True, type="primary"):
            st.toast("Listening to laptop microphone...", icon="🎙️")
            succ, txt, lang, msg = record_system_mic_direct(
                duration_sec=5,
                target_language=st.session_state.selected_language
            )
            if succ and txt:
                st.toast(f"Heard: '{txt}'", icon="🎙️")
                run_query(txt, is_voice=True)
            else:
                st.warning(msg)

        lang_opts = list(config.SUPPORTED_LANGUAGES.keys())
        lang_labels = [config.SUPPORTED_LANGUAGES[k] for k in lang_opts]
        curr_idx = lang_opts.index(st.session_state.selected_language) if st.session_state.selected_language in lang_opts else 0
        sb_lang_sel = st.selectbox("Speech Language:", options=lang_labels, index=curr_idx, key="sb_sel_lang")
        for k, v in config.SUPPORTED_LANGUAGES.items():
            if v == sb_lang_sel:
                st.session_state.selected_language = k
                break

    # 3. System Controls & Drives Expander
    with st.expander("⚡ System Controls & Drives", expanded=False):
        drives_list = st.session_state.laptop_drives
        st.caption(f"Detected {len(drives_list)} Laptop Drive(s):")

        for i in range(0, len(drives_list), 2):
            c1, c2 = st.columns(2)
            with c1:
                d1 = drives_list[i]
                if st.button(f"{d1.get('icon', '💾')} Open {d1['letter']}:", key=f"sb_drv_{d1['letter']}", use_container_width=True, help=f"{d1['label']} ({d1['free_gb']} GB free)"):
                    run_query(f"Open {d1['letter']} drive")
            with c2:
                if i + 1 < len(drives_list):
                    d2 = drives_list[i + 1]
                    if st.button(f"{d2.get('icon', '💾')} Open {d2['letter']}:", key=f"sb_drv_{d2['letter']}", use_container_width=True, help=f"{d2['label']} ({d2['free_gb']} GB free)"):
                        run_query(f"Open {d2['letter']} drive")

        c_dr1, c_dr2 = st.columns(2)
        with c_dr1:
            if st.button("🔄 Rescan", use_container_width=True, key="sb_rescan_drives", help="Scan for newly attached USB or external drives"):
                st.session_state.laptop_drives = get_laptop_drives()
                st.toast(f"Detected {len(st.session_state.laptop_drives)} live drives", icon="💽")
                st.rerun()
        with c_dr2:
            if st.button("🚪 Close Drives", use_container_width=True, key="sb_close_d"):
                run_query("Close drives")

        st.divider()
        c_app1, c_app2 = st.columns(2)
        with c_app1:
            if st.button("💻 VS Code", use_container_width=True, key="sb_btn_code"):
                launch_application("code")
                st.toast("Opened VS Code")
        with c_app2:
            if st.button("🌐 Chrome", use_container_width=True, key="sb_btn_chrome"):
                launch_application("chrome")
                st.toast("Opened Chrome")

        c_p1, c_p2 = st.columns(2)
        with c_p1:
            if st.button("📸 Screenshot", use_container_width=True, key="sb_btn_ss"):
                run_query("Take screenshot")
        with c_p2:
            if st.button("🔇 Mute Audio", use_container_width=True, key="sb_btn_mute"):
                run_query("Mute volume")

    # 4. YOLOv8 Vision Expander
    with st.expander("👁️ YOLOv8 Vision", expanded=False):
        y_stat = get_yolo_model_status()
        st.caption(f"Active Model: `{y_stat['active_model']}` ({y_stat['size_mb']} MB)")
        sb_conf = st.slider("Detection Confidence:", 0.10, 0.85, 0.20, 0.05, key="sb_yolo_conf_slider")
        if st.button("🔄 Reset to Base YOLO Model", use_container_width=True, key="sb_btn_reset_yolo"):
            succ, msg = reset_to_base_yolo_model()
            get_vision_engine().reload_model()
            st.toast("Model reset to base", icon="🔄")
            st.rerun()

    # 5. Memory & Learning Expander
    with st.expander("🧠 Memory & Learning", expanded=False):
        st.caption(f"Stored Facts: `{fact_count}` | Active User: `{active_user}`")
        quick_fact = st.text_input("Quick Teach Fact:", placeholder="e.g. Favorite tool is Python", key="sb_in_quick_fact")
        if st.button("🧠 Save Fact to Memory", use_container_width=True, key="sb_btn_save_fact"):
            if quick_fact.strip():
                teach_memory(quick_fact.strip())
                st.toast("Saved fact to memory!", icon="🧠")
                st.rerun()

    # 6. Telemetry Expander
    with st.expander("📊 Telemetry", expanded=False):
        render_telemetry_summary(telemetry)


# ===========================================================================
# 4. TOP NAVBAR (Clean Executive Brand & Status)
# ===========================================================================
render_navbar(
    fact_count=fact_count,
    user_name=active_user
)


# ===========================================================================
# 5. MAIN WORKSPACE TABS (Direct Named Modules, strictly NO Section 1, 2, 3)
# ===========================================================================
tab_exec, tab_voice, tab_sys, tab_vision, tab_mem = st.tabs([
    "💬 Executive AI",
    "🎙️ Voice Studio",
    "⚡ System Controls & Drives",
    "👁️ YOLOv8 Vision",
    "🧠 Memory & Learning"
])

# ---------------------------------------------------------------------------
# TAB 1: EXECUTIVE AI (Pure Conversational AI & Reasoning Canvas)
# ---------------------------------------------------------------------------
with tab_exec:
    # Optional Dispatch Confirmation Card (WhatsApp / Email)
    if st.session_state.pending_draft is not None:
        draft = st.session_state.pending_draft
        st.markdown(f"""
            <div class="confirm-card">
                <div class="confirm-title">Confirm Dispatch: {draft['channel']}</div>
            </div>
        """, unsafe_allow_html=True)

        col_rec, col_msg = st.columns([1, 2], gap="medium")
        with col_rec:
            t_rec = st.text_input("Recipient:", value=draft.get("recipient", "Contact"), key="confirm_rec_input")
            t_sub = st.text_input("Subject:", value=draft.get("subject", ""), key="confirm_sub_input") if draft["channel"] == "Email" else ""
        with col_msg:
            st.markdown(f"""
                <div style="background:#09090b; border:1px solid rgba(255,255,255,0.08); border-radius:8px; padding:10px; font-family:'JetBrains Mono',monospace; font-size:12px; color:#d4d4d8;">
                    <b>Draft ({draft['channel']}):</b><br/>"{draft['message']}"
                </div>
            """, unsafe_allow_html=True)

        col_c1, col_c2 = st.columns(2, gap="medium")
        with col_c1:
            if st.button(f"Send via {draft['channel']}", type="primary", use_container_width=True, key="btn_confirm_send"):
                enc = urllib.parse.quote(draft["message"])
                if draft["channel"] == "WhatsApp":
                    clean_digits = ''.join(c for c in t_rec if c.isdigit() or c == '+')
                    url = f"https://web.whatsapp.com/send?phone={clean_digits}&text={enc}" if len(clean_digits) >= 10 else f"https://web.whatsapp.com/send?text={enc}"
                    webbrowser.open_new_tab(url)
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Sent WhatsApp message for **{t_rec}**."})
                else:
                    mail_t = t_rec if "@" in t_rec else ""
                    url = f"mailto:{mail_t}?subject={urllib.parse.quote(t_sub)}&body={enc}"
                    webbrowser.open_new_tab(url)
                    st.session_state.messages.append({"role": "assistant", "content": f"✅ Launched Email for **{t_rec}**."})
                save_chat_history(st.session_state.messages)
                st.session_state.pending_draft = None
                st.rerun()

        with col_c2:
            if st.button("Cancel", use_container_width=True, key="btn_cancel_draft"):
                st.session_state.pending_draft = None
                st.rerun()

        st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

    # Minimal Starter Chips for New Conversations (Pure conversational, no open/speak buttons)
    if len(st.session_state.messages) == 0:
        render_welcome_hero(user_name=active_user)

        st.markdown('<div class="starter-card-container">', unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2, gap="small")
        with col_s1:
            if st.button("🌐 Search Google for Machine Learning", use_container_width=True, key="start_g"):
                run_query("Search Google for Machine Learning")
            if st.button("🧠 View Stored Memory Bank", use_container_width=True, key="start_mem"):
                run_query("Show memory bank")
        with col_s2:
            if st.button("👤 Who is Neelkanth?", use_container_width=True, key="start_lead"):
                run_query("Who is Neelkanth?")
            if st.button("💡 What are your core capabilities?", use_container_width=True, key="start_cap"):
                run_query("What are your capabilities?")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:16px;'></div>", unsafe_allow_html=True)

    # Conversation Stream
    for idx, msg in enumerate(st.session_state.messages):
        avatar = "⚡" if msg["role"] == "assistant" else None
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            if "timestamp" in msg:
                st.caption(msg["timestamp"])

            # Minimal Inline Correction Expander
            if msg["role"] == "assistant" and idx > 0:
                prev_msg = st.session_state.messages[idx - 1]["content"] if idx > 0 else ""
                clean_prev = prev_msg.replace("🎙️ *[Voice -", "").replace("]*", "").strip(" '\"")
                with st.expander("🎯 Train Model for this query", expanded=False):
                    trig_val = st.text_input("Trigger:", value=clean_prev, key=f"corr_trig_{idx}")
                    resp_val = st.text_input("Desired Response / Action:", placeholder="e.g. open spotify, or custom response", key=f"corr_resp_{idx}")
                    if st.button("Save Training", key=f"corr_btn_{idx}", use_container_width=True):
                        if trig_val.strip() and resp_val.strip():
                            train_new_pattern(trig_val.strip(), custom_response=resp_val.strip())
                            brain = get_neural_brain()
                            if brain:
                                try:
                                    brain.train(epochs=35, verbose=False)
                                except Exception:
                                    pass
                            st.toast(f"Trained on '{trig_val.strip()}'", icon="✅")
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": f"✅ **Pattern Trained:** *\"{trig_val.strip()}\"* → *\"{resp_val.strip()}\"*",
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                            })
                            save_chat_history(st.session_state.messages)
                            st.rerun()


# ---------------------------------------------------------------------------
# TAB 2: VOICE STUDIO (Dedicated Speak & Acoustic Cockpit)
# ---------------------------------------------------------------------------
with tab_voice:
    st.markdown("""
        <div class="voice-hero-card">
            <div class="voice-orb-glow">🎙️</div>
            <div class="voice-title">Neural Acoustic Voice Cockpit</div>
            <div class="voice-subtitle">Zero-latency speech comprehension across English, Hindi, and Gujarati</div>
        </div>
    """, unsafe_allow_html=True)

    voice_status_placeholder = st.empty()
    col_v1, col_v2 = st.columns([1.0, 1.0], gap="large")

    with col_v1:
        st.markdown("#### 🎙️ Hardware Microphone")
        st.caption("Click to record 5 seconds directly from your laptop microphone:")
        if st.button("🎙️ Push to Speak (5 Seconds)", key="btn_studio_pc_mic", use_container_width=True, type="primary"):
            voice_status_placeholder.markdown("""
                <div style="background:#1e1b4b; border:2px solid #818cf8; border-radius:12px; padding:16px; text-align:center; margin-bottom:12px; box-shadow:0 0 25px rgba(129,140,248,0.4);">
                    <div style="font-size:17px; font-weight:700; color:#c7d2fe;">🎙️ LISTENING NOW... SPEAK CLEARLY</div>
                    <div style="font-size:12px; color:#e0e7ff; margin-top:4px;">Recording PC microphone for 5 seconds...</div>
                </div>
            """, unsafe_allow_html=True)

            succ, txt, lang, msg = record_system_mic_direct(
                duration_sec=5,
                target_language=st.session_state.selected_language
            )
            voice_status_placeholder.empty()
            if succ and txt:
                st.toast(f"Recognized: '{txt}'", icon="🎙️")
                run_query(txt, is_voice=True)
            else:
                st.warning(msg)

    with col_v2:
        st.markdown("#### 🔴 Live Browser Speech")
        st.caption("Click to dictate in real time via your browser:")

        st.components.v1.html("""
            <button id="dictBtn" onclick="toggleDictate()" style="background:#2563eb; color:white; border:none; padding:9px 18px; border-radius:8px; font-size:13px; font-weight:600; cursor:pointer; display:inline-flex; align-items:center; gap:6px;">
                🎙️ Live Dictate to Chat
            </button>
            <div id="dictStatus" style="font-size:12px; color:#94a3b8; margin-top:8px;">Click and speak in real time</div>
            <script>
                var rec = null;
                function toggleDictate() {
                    var btn = document.getElementById('dictBtn');
                    var stat = document.getElementById('dictStatus');
                    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if (!SpeechRecognition) { stat.innerText = 'Browser Speech Recognition not supported'; return; }
                    if (rec) { try{rec.stop();}catch(e){} rec = null; btn.innerText = '🎙️ Live Dictate to Chat'; btn.style.background = '#2563eb'; return; }
                    rec = new SpeechRecognition();
                    rec.lang = 'en-IN';
                    btn.innerText = '🔴 Listening... (Speak now)';
                    btn.style.background = '#dc2626';
                    rec.onresult = function(e) {
                        var transcript = e.results[0][0].transcript;
                        stat.innerText = 'Heard: ' + transcript;
                        var url = new URL(window.parent.location.href);
                        url.searchParams.set('voice_prompt', transcript);
                        window.parent.location.href = url.toString();
                    };
                    rec.onerror = function(err) { btn.innerText = '🎙️ Live Dictate to Chat'; btn.style.background = '#2563eb'; stat.innerText = 'Notice: ' + err.error; rec = null; };
                    rec.onend = function() { btn.innerText = '🎙️ Live Dictate to Chat'; btn.style.background = '#2563eb'; rec = null; };
                    rec.start();
                }
            </script>
        """, height=70)

        voice_audio = st.audio_input("Or record audio clip:", key="dock_voice_audio_input")
        if voice_audio is not None:
            audio_bytes = voice_audio.getvalue()
            h = hash(audio_bytes)
            if st.session_state.get("last_processed_audio_bytes") != h:
                st.session_state.last_processed_audio_bytes = h
                succ, txt, lang, msg = transcribe_audio_robust(audio_bytes, target_language=st.session_state.selected_language)
                if succ and txt:
                    st.toast(f"Recognized: '{txt}'", icon="🎙️")
                    run_query(txt, is_voice=True)
                else:
                    st.warning(msg)

    # Spoken audio playback via Web Speech API
    if st.session_state.get("pending_speech_audio"):
        tts_speech_text = st.session_state.pop("pending_speech_audio")
        safe_speak_js = (
            tts_speech_text.replace("'", "\'")
            .replace('"', '\"')
            .replace("\n", " ")
            .replace("*", "")
            .replace("#", "")
            .replace("`", "")
        )
        st.components.v1.html(f"""
            <script>
                if ('speechSynthesis' in window) {{
                    window.speechSynthesis.cancel();
                    var u = new SpeechSynthesisUtterance("{safe_speak_js}");
                    u.rate = 1.0;
                    u.pitch = 1.0;
                    u.lang = 'en-US';
                    window.speechSynthesis.speak(u);
                }}
            </script>
        """, height=0)


# ---------------------------------------------------------------------------
# TAB 3: SYSTEM CONTROLS & DRIVES (Dedicated Open & Laptop Hardware Studio)
# ---------------------------------------------------------------------------
with tab_sys:
    st.markdown("#### 💽 Laptop Drives Auto-Discovery & Storage Telemetry")
    st.caption("Live scan of physical partitions, external hard drives, and USB media connected to this laptop:")

    render_drives_overview(st.session_state.laptop_drives)

    # Dynamic Drive Opening Buttons
    st.markdown("##### 📂 Open Detected Laptop Drives")
    active_drives = st.session_state.laptop_drives

    for i in range(0, len(active_drives), 2):
        c_od1, c_od2 = st.columns(2)
        with c_od1:
            d1 = active_drives[i]
            if st.button(f"{d1.get('icon', '💾')} Open {d1['letter']}:\\ ({d1['label']})", key=f"main_open_drv_{d1['letter']}", use_container_width=True):
                run_query(f"Open {d1['letter']} drive")
        with c_od2:
            if i + 1 < len(active_drives):
                d2 = active_drives[i + 1]
                if st.button(f"{d2.get('icon', '💾')} Open {d2['letter']}:\\ ({d2['label']})", key=f"main_open_drv_{d2['letter']}", use_container_width=True):
                    run_query(f"Open {d2['letter']} drive")

    c_act1, c_act2, c_act3 = st.columns(3)
    with c_act1:
        if st.button("🔄 Re-Scan Connected Drives", use_container_width=True, key="btn_sys_rescan_drives"):
            st.session_state.laptop_drives = get_laptop_drives()
            st.toast(f"Detected {len(st.session_state.laptop_drives)} drives", icon="💽")
            st.rerun()
    with c_act2:
        if st.button("🚪 Close All Drive Windows", use_container_width=True, key="btn_sys_close_drives"):
            run_query("Close drives")
    with c_act3:
        if st.button("📂 Open File Explorer (This PC)", use_container_width=True, key="btn_sys_open_explorer"):
            open_drive_or_folder("open explorer")

    st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
    st.markdown("#### 🚀 Quick Application Launcher")

    col_app1, col_app2, col_app3 = st.columns(3)
    with col_app1:
        if st.button("💻 Visual Studio Code", use_container_width=True, key="btn_sys_code"):
            launch_application("code")
            st.toast("Launched VS Code", icon="💻")
        if st.button("📝 Notepad", use_container_width=True, key="btn_sys_notepad"):
            launch_application("notepad")
            st.toast("Launched Notepad", icon="📝")
    with col_app2:
        if st.button("🌐 Google Chrome", use_container_width=True, key="btn_sys_chrome"):
            launch_application("chrome")
            st.toast("Launched Chrome", icon="🌐")
        if st.button("🧮 Calculator", use_container_width=True, key="btn_sys_calc"):
            launch_application("calc")
            st.toast("Launched Calculator", icon="🧮")
    with col_app3:
        if st.button("⚡ Task Manager", use_container_width=True, key="btn_sys_taskmgr"):
            launch_application("taskmgr")
            st.toast("Launched Task Manager", icon="⚡")
        if st.button("⚙️ Windows Settings", use_container_width=True, key="btn_sys_settings"):
            launch_application("settings")
            st.toast("Opened Windows Settings", icon="⚙️")

    st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
    st.markdown("#### ⚡ Hardware Utilities")
    col_ut1, col_ut2, col_ut3 = st.columns(3)
    with col_ut1:
        if st.button("📸 Capture Screenshot", use_container_width=True, key="btn_sys_ss"):
            run_query("Take screenshot")
    with col_ut2:
        if st.button("🔇 Toggle Audio Mute", use_container_width=True, key="btn_sys_mute"):
            run_query("Mute volume")
    with col_ut3:
        if st.button("🔒 Lock Workstation", use_container_width=True, key="btn_sys_lock"):
            lock_computer_workstation()
            st.toast("Locked computer workstation", icon="🔒")


# ---------------------------------------------------------------------------
# TAB 4: YOLOV8 VISION STUDIO
# ---------------------------------------------------------------------------
with tab_vision:
    tab_vis_detect, tab_vis_train = st.tabs(["📷 Object Detection", "⚡ Model Training & Tuning"])

    with tab_vis_detect:
        col_v_left, col_v_right = st.columns([1.0, 1.0], gap="large")

        with col_v_left:
            conf_slider = st.slider("Confidence Threshold:", 0.10, 0.85, 0.20, 0.05, key="yolo_conf_slider")

            vision_mode = st.radio(
                "Source Mode:",
                ["📷 Webcam Snapshot", "📁 Upload Image"],
                horizontal=True,
                key="yolo_input_mode_radio"
            )

            captured_vision_bytes = None
            if vision_mode == "📷 Webcam Snapshot":
                cam_snap = st.camera_input("Webcam Capture:", key="yolo_camera_studio_input")
                if cam_snap is not None:
                    captured_vision_bytes = cam_snap.getvalue()
            else:
                up_img = st.file_uploader("Upload Image:", type=["jpg", "jpeg", "png", "webp"], key="yolo_file_upload_input")
                if up_img is not None:
                    captured_vision_bytes = up_img.getvalue()

        with col_v_right:
            if captured_vision_bytes is not None:
                vision_engine = get_vision_engine()
                with st.spinner("Detecting objects..."):
                    succ, annotated_img, detections, counts, narrative = vision_engine.detect_and_analyze(
                        captured_vision_bytes,
                        conf_threshold=conf_slider
                    )

                if succ and annotated_img is not None:
                    st.image(annotated_img, caption=f"YOLOv8 Detection ({len(detections)} Objects)", use_container_width=True)

                    if counts:
                        tags_html = "<div style='display:flex; flex-wrap:wrap; gap:6px; margin: 6px 0;'>"
                        for c_name, c_cnt in counts.items():
                            tags_html += f"<span style='background:rgba(56,189,248,0.12); border:1px solid #38bdf8; color:#e0f2fe; padding:2px 8px; border-radius:10px; font-size:11.5px; font-weight:600;'>{c_name.title()}: {c_cnt}</span>"
                        tags_html += "</div>"
                        st.markdown(tags_html, unsafe_allow_html=True)

                    st.markdown(narrative)

                    col_va1, col_va2 = st.columns(2, gap="small")
                    with col_va1:
                        if st.button("💬 Send to Chat", use_container_width=True, key="btn_post_vision_to_chat"):
                            st.session_state.messages.append({
                                "role": "user",
                                "content": "📷 *[Camera Snapshot analyzed with YOLOv8 Vision]*",
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                            })
                            st.session_state.messages.append({
                                "role": "assistant",
                                "content": narrative,
                                "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                            })
                            save_chat_history(st.session_state.messages)
                            add_log("VISION", f"YOLOv8 detected {len(detections)} objects")
                            st.toast("Saved to chat", icon="👁️")
                            st.rerun()

                    with col_va2:
                        if st.button("💾 Save to Memory", use_container_width=True, key="btn_save_vision_memory"):
                            summary_fact = f"Observed {len(detections)} items ({', '.join(list(counts.keys()))}) on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}."
                            teach_memory(summary_fact, category="Vision Observation")
                            st.toast("Saved observation to Memory Bank", icon="🧠")
                            st.rerun()
                else:
                    st.warning(narrative)
            else:
                st.info("Take a webcam photo or upload an image to run object detection.")

    with tab_vis_train:
        yolo_stat = get_yolo_model_status()
        col_t1, col_t2 = st.columns([1.0, 1.0], gap="large")

        with col_t1:
            st.markdown("#### ⚙️ Active Model Status")
            active_badge = "Custom Trained" if yolo_stat["is_custom_trained"] else "Base Official"
            st.markdown(f"""
                <div style="background:#101117; border:1px solid rgba(255,255,255,0.08); border-radius:10px; padding:12px 14px; margin-bottom:12px;">
                    <div style="font-size:12px; color:#94a3b8;">ACTIVE DETECTION WEIGHTS</div>
                    <div style="font-size:16px; font-weight:700; color:#38bdf8; margin-top:2px;">{yolo_stat['active_model']} ({active_badge})</div>
                    <div style="font-size:11.5px; color:#64748b; margin-top:4px;">Size: {yolo_stat['size_mb']} MB</div>
                </div>
            """, unsafe_allow_html=True)

            train_epochs = st.slider("Fine-Tuning Epochs:", min_value=1, max_value=25, value=5, step=1, key="yolo_train_epochs")
            train_batch = st.selectbox("Batch Size:", [2, 4, 8], index=1, key="yolo_train_batch")

            if st.button("🚀 Train / Fine-Tune YOLO Model", use_container_width=True, type="primary", key="btn_run_yolo_train"):
                with st.spinner("Fine-tuning YOLO neural model..."):
                    succ, msg_train, meta = fine_tune_yolo_model(epochs=train_epochs, batch_size=train_batch)
                    if succ:
                        get_vision_engine().reload_model()
                        st.toast("YOLO model successfully fine-tuned!", icon="✅")
                        st.success(msg_train)
                        st.rerun()
                    else:
                        st.error(msg_train)

        with col_t2:
            st.markdown("#### 🔄 Model Management")
            st.caption("Revert to the official YOLOv8 base model at any time:")
            if st.button("🔄 Reset to Base Model (yolov8n.pt)", use_container_width=True, key="btn_reset_yolo_model"):
                succ, msg_rst = reset_to_base_yolo_model()
                get_vision_engine().reload_model()
                st.toast("Reset to base YOLO model", icon="🔄")
                st.info(msg_rst)
                st.rerun()


# ---------------------------------------------------------------------------
# TAB 5: MEMORY & LEARNING HUB
# ---------------------------------------------------------------------------
with tab_mem:
    sub_tab_mem, sub_tab_learn, sub_tab_profile = st.tabs([
        "🗄️ Memory Bank",
        "🎯 Active Learning",
        "👤 Settings & Telemetry"
    ])

    with sub_tab_mem:
        col_m_teach, col_m_list = st.columns([1.0, 1.2], gap="large")

        with col_m_teach:
            st.markdown("#### ➕ Add New Fact")
            new_fact_input = st.text_input("Fact:", placeholder="e.g. My favorite fruit is Mango", key="in_new_teach_fact")
            fact_category = st.selectbox(
                "Category:",
                ["User Profile", "Personal Attribute", "Preferences", "Contact Info", "Education", "Work / Projects", "General"],
                key="sel_new_fact_cat"
            )
            if st.button("Teach Fact", type="primary", use_container_width=True, key="btn_teach_fact"):
                if new_fact_input.strip():
                    teach_memory(new_fact_input.strip(), category=fact_category)
                    brain = get_neural_brain()
                    if brain:
                        brain.learn_fact(new_fact_input.strip())
                    st.toast("Fact learned!", icon="🧠")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"🧠 **Learned new fact:** *\"{new_fact_input.strip()}\"* [{fact_category}]",
                        "timestamp": datetime.datetime.now().strftime("%H:%M:%S")
                    })
                    save_chat_history(st.session_state.messages)
                    st.rerun()

        with col_m_list:
            st.markdown("#### 📜 Stored Facts")
            mem_filter = st.text_input("Search:", placeholder="Filter facts...", key="in_mem_search")
            all_mems = get_all_memories_list()
            if mem_filter.strip():
                all_mems = [m for m in all_mems if mem_filter.lower() in m.get("fact", "").lower() or mem_filter.lower() in m.get("category", "").lower()]

            if all_mems:
                for m in all_mems[-8:]:
                    with st.container():
                        c_txt, c_del = st.columns([0.88, 0.12])
                        with c_txt:
                            st.markdown(f"""
                                <div class="memory-card">
                                    <span class="memory-cat-badge">{m.get('category', 'Fact')}</span>
                                    <div class="memory-text">{m.get('fact')}</div>
                                    <div class="memory-time">{m.get('timestamp')}</div>
                                </div>
                            """, unsafe_allow_html=True)
                        with c_del:
                            if st.button("🗑️", key=f"del_mem_{m.get('id')}", help="Delete"):
                                delete_memory(m.get("id"))
                                st.toast("Fact deleted", icon="🗑️")
                                st.rerun()
            else:
                st.caption("No facts found.")

    with sub_tab_learn:
        col_l1, col_l2 = st.columns([1.0, 1.0], gap="large")

        with col_l1:
            st.markdown("#### 🎯 Train New Pattern")
            p_trig = st.text_input("Trigger Command:", placeholder="e.g. open my project workspace", key="in_train_trig")
            p_resp = st.text_area("Response / Action:", placeholder="e.g. Opened workspace and launched development tools.", key="in_train_resp", height=85)
            p_cat = st.selectbox("Category:", ["Workspace Automation", "System Control", "File Automation", "Productivity", "Custom Response"], key="in_train_cat")

            if st.button("Train Pattern", type="primary", use_container_width=True, key="btn_train_pattern"):
                if p_trig.strip() and p_resp.strip():
                    train_new_pattern(p_trig.strip(), custom_response=p_resp.strip(), category=p_cat)
                    brain = get_neural_brain()
                    if brain:
                        try:
                            brain.train(epochs=35, verbose=False)
                        except Exception:
                            pass
                    st.toast("Trained pattern!", icon="🎯")
                    st.rerun()

        with col_l2:
            st.markdown("#### 🧪 Test Pattern Matcher")
            test_query = st.text_input("Test Trigger:", placeholder="Type variation...", key="in_test_query")
            if test_query:
                is_m, pat, score = match_learned_intent(test_query)
                if is_m and pat:
                    st.markdown(f"""
                        <div style="background:#052e16; border:1px solid #16a34a; border-radius:10px; padding:12px; margin-top:8px;">
                            <div style="color:#86efac; font-weight:600; font-size:13px;">Match Found ({int(score*100)}% Confidence)</div>
                            <div style="font-size:12px; color:#f0fdf4; margin:4px 0;"><b>Matched:</b> "{pat.get('trigger')}"</div>
                            <div style="font-size:12.5px; color:#cbd5e1;"><b>Response:</b> "{pat.get('custom_response')}"</div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.warning(f"No direct trigger match for '{test_query.strip()}'.")

        st.markdown("<div style='margin-bottom:14px;'></div>", unsafe_allow_html=True)
        st.markdown("#### Active Patterns")
        all_pats = get_all_learned_patterns()
        if all_pats:
            for pat in all_pats[-5:]:
                with st.container():
                    c_ptxt, c_pdel = st.columns([0.88, 0.12])
                    with c_ptxt:
                        st.markdown(f"""
                            <div class="memory-card">
                                <span class="memory-cat-badge">{pat.get('category', 'Automation')}</span>
                                <div class="memory-text">"{pat.get('trigger')}" → {pat.get('action')}</div>
                                <div class="memory-time">{pat.get('custom_response')}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    with c_pdel:
                        if st.button("🗑️", key=f"del_pat_{pat.get('pattern_id')}", help="Delete"):
                            delete_learned_pattern(pat.get("pattern_id"))
                            st.toast("Pattern deleted", icon="🗑️")
                            st.rerun()

    with sub_tab_profile:
        col_p1, col_p2 = st.columns([1.0, 1.0], gap="large")

        with col_p1:
            st.markdown("#### 👤 Operator Settings")
            new_uname = st.text_input("Operator Name:", value=active_user, key="in_prof_uname")
            if st.button("Save Name", use_container_width=True, key="btn_save_profile"):
                if new_uname.strip():
                    up_name = set_active_user_name(new_uname.strip())
                    st.toast(f"Profile updated to '{up_name}'", icon="👤")
                    st.rerun()

            lang_opts = list(config.SUPPORTED_LANGUAGES.keys())
            lang_labels = [config.SUPPORTED_LANGUAGES[k] for k in lang_opts]
            curr_idx = lang_opts.index(st.session_state.selected_language) if st.session_state.selected_language in lang_opts else 0

            sel_lang_lbl = st.selectbox("Language:", options=lang_labels, index=curr_idx, key="sel_profile_lang")
            for k, v in config.SUPPORTED_LANGUAGES.items():
                if v == sel_lang_lbl:
                    st.session_state.selected_language = k
                    break

            api_key_in = st.text_input(
                "LLM API Key (Gemini / Groq):",
                value=st.session_state.custom_llm_api_key,
                type="password",
                key="in_profile_api_key"
            )
            if api_key_in != st.session_state.custom_llm_api_key:
                st.session_state.custom_llm_api_key = api_key_in
                os.environ["GEMINI_API_KEY"] = api_key_in
                os.environ["GROQ_API_KEY"] = api_key_in
                st.toast("API Key updated", icon="🔑")

        with col_p2:
            st.markdown("#### 📊 Telemetry")
            render_telemetry_summary(telemetry)

            st.markdown("#### 📜 Activity Logs")
            render_activity_logs(st.session_state.logs)

            col_hp1, col_hp2 = st.columns(2)
            with col_hp1:
                if st.button("🗑️ Clear Chat History", use_container_width=True, key="btn_prof_clear_chat"):
                    st.session_state.messages = []
                    clear_chat_history()
                    st.toast("Chat history cleared", icon="🗑️")
                    st.rerun()
            with col_hp2:
                chat_data_str = json.dumps(st.session_state.messages, indent=2)
                st.download_button(
                    label="💾 Export Chat",
                    data=chat_data_str,
                    file_name=f"chat_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    use_container_width=True,
                    key="btn_download_chat"
                )


# ===========================================================================
# 6. STICKING BOTTOM CHAT INPUT (Fixed at the very bottom of the page)
# ===========================================================================
user_prompt = st.chat_input("Type a message or command...")
if user_prompt:
    run_query(user_prompt)

# Execute pending submitted query (e.g. from Voice Studio or Web Speech API)
if st.session_state.pending_query:
    q_run = st.session_state.pending_query
    st.session_state.pending_query = None
    run_query(q_run)
