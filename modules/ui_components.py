"""
=============================================================================
ADHYAKSH AI // Clean Minimalist Executive Design System
Minimal text, high-contrast aesthetics, and refined human-crafted UI/UX
=============================================================================
"""

import streamlit as st
from config import APP_NAME, APP_SUBTITLE, APP_VERSION

def inject_custom_css():
    """Injects high-end, clean obsidian styling across all sections."""
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

        /* 1. Canvas & Root */
        html, body, [data-testid="stAppViewContainer"], .stApp {
            background-color: #09090b !important;
            color: #f4f4f5 !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            -webkit-font-smoothing: antialiased;
        }

        .block-container {
            padding-top: 1.0rem !important;
            padding-bottom: 5.5rem !important;
            max-width: 960px !important;
            margin: 0 auto !important;
        }

        /* Scrollbars */
        ::-webkit-scrollbar { width: 5px; height: 5px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.12); border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.22); }

        /* 2. Chat Bubbles */
        [data-testid="stChatMessage"] {
            background-color: transparent !important;
            border: none !important;
            padding: 12px 16px !important;
            border-radius: 12px !important;
            margin-bottom: 10px !important;
            line-height: 1.6 !important;
            font-size: 14px !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            background-color: #12131a !important;
            border: 1px solid rgba(59, 130, 246, 0.22) !important;
            border-radius: 12px 12px 4px 12px !important;
            margin-left: 2rem !important;
        }

        [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
            background-color: #0e0f14 !important;
            border: 1px solid rgba(255, 255, 255, 0.06) !important;
            border-radius: 12px 12px 12px 4px !important;
            margin-right: 1.5rem !important;
        }

        [data-testid="stChatMessage"] code {
            font-family: 'JetBrains Mono', monospace !important;
            font-size: 12.5px !important;
            background: #181920 !important;
            padding: 2px 6px !important;
            border-radius: 5px !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            color: #67e8f9 !important;
        }

        /* 3. Bottom Sticking Chat Input */
        div[data-testid="stChatInput"] {
            border-radius: 16px !important;
            border: 1px solid rgba(255, 255, 255, 0.14) !important;
            background: #111218 !important;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.6) !important;
            max-width: 960px !important;
            margin: 0 auto !important;
            transition: all 0.2s ease !important;
        }

        div[data-testid="stChatInput"]:focus-within {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.25) !important;
        }

        div[data-testid="stChatInput"] textarea {
            color: #f4f4f5 !important;
            font-size: 14px !important;
        }

        div[data-testid="stChatInput"] button {
            color: #38bdf8 !important;
            border-radius: 10px !important;
        }

        /* 4. Streamlit Tabs */
        div[data-testid="stTabs"] {
            margin-bottom: 16px !important;
        }

        div[data-testid="stTabs"] button[role="tab"] {
            background-color: transparent !important;
            color: #94a3b8 !important;
            font-size: 13.5px !important;
            font-weight: 600 !important;
            padding: 8px 16px !important;
            border: none !important;
            border-bottom: 2px solid transparent !important;
            transition: all 0.15s ease !important;
        }

        div[data-testid="stTabs"] button[role="tab"]:hover {
            color: #f1f5f9 !important;
            background: rgba(255, 255, 255, 0.02) !important;
        }

        div[data-testid="stTabs"] button[aria-selected="true"] {
            color: #38bdf8 !important;
            border-bottom: 2px solid #38bdf8 !important;
            background: rgba(56, 189, 248, 0.05) !important;
        }

        /* 5. Sidebar */
        [data-testid="stSidebar"] {
            background-color: #0b0c10 !important;
            border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        }

        [data-testid="stSidebarContent"] {
            padding: 1.0rem 0.9rem !important;
        }

        /* 6. Buttons */
        div.stButton > button {
            border-radius: 9px !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            background: #13141b !important;
            color: #e4e4e7 !important;
            font-weight: 500 !important;
            font-size: 13px !important;
            padding: 7px 13px !important;
            transition: all 0.15s ease !important;
        }

        div.stButton > button:hover {
            background: #1d1f28 !important;
            border-color: rgba(255, 255, 255, 0.2) !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        div.stButton > button[kind="primary"],
        div.stButton > button[data-testid="baseButton-primary"],
        div.stButton > button[data-testid="stBaseButton-primary"] {
            background: #2563eb !important;
            border: 1px solid #3b82f6 !important;
            color: #ffffff !important;
            font-weight: 600 !important;
        }

        div.stButton > button[kind="primary"]:hover,
        div.stButton > button[data-testid="baseButton-primary"]:hover,
        div.stButton > button[data-testid="stBaseButton-primary"]:hover {
            background: #1d4ed8 !important;
            border-color: #60a5fa !important;
        }

        /* 7. Expanders & Inputs */
        [data-testid="stExpander"] {
            background: #101117 !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 10px !important;
            margin-bottom: 8px !important;
            transition: all 0.2s ease !important;
            overflow: hidden !important;
        }

        [data-testid="stExpander"]:hover {
            border-color: rgba(56, 189, 248, 0.25) !important;
        }

        [data-testid="stExpander"] summary {
            font-size: 13.5px !important;
            font-weight: 600 !important;
            color: #f1f5f9 !important;
            padding: 9px 14px !important;
            border-radius: 9px !important;
            transition: all 0.15s ease !important;
        }

        [data-testid="stExpander"] summary:hover {
            color: #38bdf8 !important;
            background: rgba(56, 189, 248, 0.04) !important;
        }

        [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
            padding: 10px 14px 14px 14px !important;
            border-top: 1px solid rgba(255, 255, 255, 0.06) !important;
        }

        div[data-baseweb="input"] input, 
        div[data-baseweb="textarea"] textarea {
            background-color: #0f1118 !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            color: #f4f4f5 !important;
            border-radius: 9px !important;
            font-size: 13px !important;
        }

        div[data-baseweb="input"]:focus-within,
        div[data-baseweb="textarea"]:focus-within {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.18) !important;
        }

        div[data-baseweb="select"] > div {
            background-color: #0f1118 !important;
            border: 1px solid rgba(255, 255, 255, 0.09) !important;
            color: #f4f4f5 !important;
            border-radius: 9px !important;
            font-size: 13px !important;
        }

        /* 8. Aesthetic Voice Studio Card & Pulse */
        .voice-hero-card {
            background: linear-gradient(135deg, rgba(30, 41, 59, 0.35), rgba(15, 23, 42, 0.5));
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-radius: 14px;
            padding: 22px 20px;
            text-align: center;
            margin-bottom: 16px;
            backdrop-filter: blur(8px);
        }

        .voice-orb-glow {
            width: 52px;
            height: 52px;
            border-radius: 50%;
            background: radial-gradient(circle, #2563eb, #1e1b4b);
            border: 2px solid #38bdf8;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            margin-bottom: 8px;
            animation: pulse-glow 2.5s infinite ease-in-out;
        }

        @keyframes pulse-glow {
            0% { transform: scale(1); box-shadow: 0 0 16px rgba(56, 189, 248, 0.25); }
            50% { transform: scale(1.05); box-shadow: 0 0 28px rgba(56, 189, 248, 0.45); }
            100% { transform: scale(1); box-shadow: 0 0 16px rgba(56, 189, 248, 0.25); }
        }

        .voice-title {
            font-size: 16px;
            font-weight: 700;
            color: #f8fafc;
            margin-bottom: 3px;
        }

        .voice-subtitle {
            font-size: 12px;
            color: #94a3b8;
        }

        /* 9. Components */
        .min-navbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 6px 0 14px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.06);
            margin-bottom: 14px;
        }

        .min-brand {
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .min-brand-title {
            font-size: 16px;
            font-weight: 700;
            letter-spacing: -0.2px;
            color: #f4f4f5;
            margin: 0;
        }

        .status-pill {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 16px;
            padding: 3px 9px;
            font-size: 11px;
            color: #94a3b8;
        }

        .status-dot-green {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            background-color: #10b981;
        }

        .welcome-hero {
            text-align: center;
            padding: 24px 12px 14px 12px;
            margin-bottom: 16px;
        }

        .welcome-icon {
            font-size: 30px;
            margin-bottom: 6px;
            display: inline-block;
        }

        .welcome-title {
            font-size: 20px;
            font-weight: 600;
            letter-spacing: -0.3px;
            color: #f8fafc;
            margin: 0;
        }

        .starter-card-container div.stButton > button {
            background-color: #101117 !important;
            border: 1px solid rgba(255, 255, 255, 0.07) !important;
            border-radius: 10px !important;
            padding: 10px 14px !important;
            text-align: left !important;
            color: #f4f4f5 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            min-height: 48px !important;
            display: flex !important;
            align-items: center !important;
            transition: all 0.15s ease !important;
            width: 100% !important;
        }

        .starter-card-container div.stButton > button:hover {
            background-color: #161720 !important;
            border-color: rgba(56, 189, 248, 0.28) !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
        }

        .confirm-card {
            background: #12131a;
            border: 1px solid rgba(99, 102, 241, 0.35);
            border-radius: 12px;
            padding: 16px 18px;
            margin-bottom: 16px;
        }

        .confirm-title {
            color: #a5b4fc;
            font-size: 14px;
            font-weight: 600;
            margin: 0 0 8px 0;
        }

        .memory-card {
            background: #101117;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 10px;
            padding: 12px 14px;
            margin-bottom: 8px;
            transition: all 0.15s ease;
        }

        .memory-card:hover {
            background: #15161f;
            border-color: rgba(56, 189, 248, 0.2);
        }

        .memory-cat-badge {
            display: inline-block;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.4px;
            background: rgba(56, 189, 248, 0.1);
            color: #38bdf8;
            padding: 2px 6px;
            border-radius: 4px;
            margin-bottom: 4px;
        }

        .memory-text {
            font-size: 13.5px;
            font-weight: 500;
            color: #f1f5f9;
            margin-bottom: 3px;
            line-height: 1.4;
        }

        .memory-time {
            font-size: 10.5px;
            color: #64748b;
            font-family: 'JetBrains Mono', monospace;
        }

        .stat-grid-min {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 6px;
            margin-bottom: 10px;
        }

        .stat-card-min {
            background: #101117;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 8px 10px;
        }

        .stat-val-min {
            font-size: 14px;
            font-weight: 600;
            font-family: 'JetBrains Mono', monospace;
            color: #f4f4f5;
        }

        .stat-lbl-min {
            font-size: 10.5px;
            color: #71717a;
            margin-top: 1px;
        }

        .terminal-box-min {
            background-color: #08090d !important;
            border: 1px solid rgba(255, 255, 255, 0.06);
            border-radius: 8px;
            padding: 10px 12px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 11px;
            color: #94a3b8;
            max-height: 200px;
            overflow-y: auto;
            line-height: 1.5;
        }

        .log-line { margin-bottom: 3px; }
        .log-time { color: #475569; }
        .log-stt { color: #38bdf8; font-weight: 500; }
        .log-nlu { color: #a78bfa; font-weight: 500; }
        .log-exec { color: #34d399; font-weight: 500; }
        .log-vision { color: #38bdf8; font-weight: 500; }

        /* Dynamic Laptop Drive Cards */
        .drive-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
            gap: 10px;
            margin-top: 8px;
            margin-bottom: 14px;
        }

        .drive-card {
            background: #101117;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 12px;
            transition: all 0.15s ease;
        }

        .drive-card:hover {
            border-color: rgba(56, 189, 248, 0.35);
            background: #14161f;
        }

        .drive-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 6px;
        }

        .drive-title {
            font-size: 13px;
            font-weight: 600;
            color: #f8fafc;
        }

        .drive-badge {
            font-size: 10px;
            padding: 2px 6px;
            border-radius: 8px;
            background: rgba(56, 189, 248, 0.12);
            color: #38bdf8;
            font-weight: 500;
        }

        .drive-badge-system {
            background: rgba(168, 85, 247, 0.15);
            color: #c084fc;
        }

        .drive-progress-bg {
            background: #1e2029;
            border-radius: 4px;
            height: 5px;
            overflow: hidden;
            margin: 6px 0;
        }

        .drive-progress-bar {
            height: 100%;
            background: linear-gradient(90deg, #38bdf8, #2563eb);
            border-radius: 4px;
        }

        .drive-progress-bar-warn {
            background: linear-gradient(90deg, #f59e0b, #ef4444);
        }

        .drive-stats {
            display: flex;
            justify-content: space-between;
            font-size: 11px;
            color: #94a3b8;
        }

        #MainMenu, [data-testid="stMainMenu"], [data-testid="stStatusWidget"], footer {
            visibility: hidden !important;
            display: none !important;
        }

        header[data-testid="stHeader"] {
            background: transparent !important;
            height: 2.5rem !important;
            z-index: 99999 !important;
        }

        [data-testid="stToolbar"] {
            visibility: visible !important;
            background: transparent !important;
            height: 2.5rem !important;
            display: flex !important;
            align-items: center !important;
        }

        [data-testid="stToolbarActions"] {
            visibility: hidden !important;
            display: none !important;
        }

        [data-testid="stExpandSidebarButton"],
        [data-testid="stSidebarCollapsedControl"] {
            visibility: visible !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            background: #14151c !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            border-radius: 8px !important;
            padding: 5px 8px !important;
            color: #38bdf8 !important;
            cursor: pointer !important;
            position: fixed !important;
            top: 10px !important;
            left: 12px !important;
            z-index: 999999 !important;
        }
        </style>
    """, unsafe_allow_html=True)


def render_navbar(active_section_name: str = "", fact_count: int = 0, user_name: str = "Neelkanth"):
    """Renders a sleek, clean top navbar without clutter."""
    sec_pill = f'<div class="status-pill" style="border-color:rgba(56,189,248,0.35); color:#38bdf8; font-weight:600;"><span>{active_section_name}</span></div>' if active_section_name else ""
    btn_js = (
        "(function(){"
        "var exp = document.querySelector('[data-testid=\\'stExpandSidebarButton\\']') || document.querySelector('[data-testid=\\'stSidebarCollapsedControl\\']');"
        "var col = document.querySelector('[data-testid=\\'stSidebarCollapseButton\\']');"
        "if (exp) exp.click(); else if (col) col.click();"
        "})()"
    )
    navbar_html = (
        '<div class="min-navbar">'
        '<div class="min-brand">'
        f'<button onclick="{btn_js}" style="background:#13141b; border:1px solid rgba(255,255,255,0.12); border-radius:7px; color:#38bdf8; padding:4px 8px; cursor:pointer; font-size:12px; margin-right:4px;" title="Toggle Sidebar">☰</button>'
        f'<span class="min-brand-title">⚡ {APP_NAME}</span>'
        '</div>'
        '<div style="display:flex; align-items:center; gap:6px;">'
        f'{sec_pill}'
        '<div class="status-pill"><span class="status-dot-green"></span><span>Ready</span></div>'
        f'<div class="status-pill"><span>👤 {user_name}</span></div>'
        f'<div class="status-pill"><span>🧠 {fact_count} Facts</span></div>'
        '</div>'
        '</div>'
    )
    st.markdown(navbar_html, unsafe_allow_html=True)


def render_welcome_hero(user_name: str = "Neelkanth"):
    """Renders a minimal, elegant greeting for fresh sessions."""
    hero_html = f'<div class="welcome-hero"><div class="welcome-icon">⚡</div><div class="welcome-title">Greetings, {user_name}</div></div>'
    st.markdown(hero_html, unsafe_allow_html=True)


def render_activity_logs(logs: list):
    """Renders real-time telemetry logs inside a monospace terminal box."""
    if not logs:
        st.caption("No logs recorded.")
        return
    log_html = '<div class="terminal-box-min">'
    for log in logs[-15:]:
        stage_cls = f"log-{log['stage'].lower()}" if 'stage' in log else ""
        log_html += f'<div class="log-line"><span class="log-time">[{log["time"]}]</span> <span class="{stage_cls}">[{log["stage"]}]</span> {log["msg"]}</div>'
    log_html += '</div>'
    st.markdown(log_html, unsafe_allow_html=True)


def render_telemetry_summary(telemetry: dict):
    """Renders a compact 2x2 telemetry grid."""
    grid_html = (
        '<div class="stat-grid-min">'
        f'<div class="stat-card-min"><div class="stat-val-min">{telemetry.get("cpu_percent", 0)}%</div><div class="stat-lbl-min">CPU</div></div>'
        f'<div class="stat-card-min"><div class="stat-val-min">{telemetry.get("ram_percent", 0)}%</div><div class="stat-lbl-min">RAM</div></div>'
        f'<div class="stat-card-min"><div class="stat-val-min">{telemetry.get("disk_percent", 0)}%</div><div class="stat-lbl-min">Disk</div></div>'
        f'<div class="stat-card-min"><div class="stat-val-min">{telemetry.get("cpu_count", 0)} Cores</div><div class="stat-lbl-min">Cores</div></div>'
        '</div>'
    )
    st.markdown(grid_html, unsafe_allow_html=True)


def render_drives_overview(drives: list):
    """Renders a sleek obsidian card grid of all detected laptop drives."""
    if not drives:
        st.info("No physical drives detected on this machine.")
        return

    cards = []
    for d in drives:
        is_high = d.get("percent_used", 0) > 80
        bar_cls = "drive-progress-bar-warn" if is_high else "drive-progress-bar"
        badge_cls = "drive-badge drive-badge-system" if d.get("is_system") else "drive-badge"
        cards.append(
            '<div class="drive-card">'
            '<div class="drive-header">'
            f'<span class="drive-title">{d.get("icon", "💾")} {d.get("letter")}:\\ ({d.get("label")})</span>'
            f'<span class="{badge_cls}">{d.get("type")}</span>'
            '</div>'
            '<div class="drive-progress-bg">'
            f'<div class="{bar_cls}" style="width: {min(d.get("percent_used", 0), 100)}%;"></div>'
            '</div>'
            '<div class="drive-stats">'
            f'<span>{d.get("free_gb")} GB free</span>'
            f'<span>{d.get("total_gb")} GB ({d.get("percent_used")}%)</span>'
            '</div>'
            '</div>'
        )
    html = f'<div class="drive-grid">{"".join(cards)}</div>'
    st.markdown(html, unsafe_allow_html=True)


# Backwards compatibility wrappers
def render_section_banner(title: str, subtitle: str, icon: str = "⚡", badge: str = "Active"):
    pass

def render_hero_hud():
    render_navbar()

def render_metric_cards(cpu_percent: float, ram_percent: float, learned_count: int, memory_count: int):
    pass

def render_voice_cockpit():
    pass
