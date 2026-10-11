import streamlit as st
import streamlit.components.v1 as components
import requests
import datetime
import math
from pathlib import Path

st.set_page_config(
    page_title="HeatLine | Field Safety Operating System",
    page_icon="🌡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

API_URL = "https://e2zksw0bjh.execute-api.ap-southeast-2.amazonaws.com/default/heatline-api"
PHONE_DEMO_FILE = Path(__file__).parent / "heatline-phone-demo.html"

WORK_TYPES = ["Construction", "Delivery", "Waste collection", "Street vending", "Agriculture", "Factory work", "Other"]
ORGANIZATION_TYPES = ["Student group", "NGO", "Worker union", "Community organization", "Company / employer", "Government department", "Other"]
ACTION_OPTIONS = [
    "Provide drinking water", "Provide shade or rest area", "Allow rest breaks",
    "Check worker health symptoms", "Reduce work during peak heat", "Escalate to supervisor", "Other action needed"
]
PROBLEM_OPTIONS = [
    "Heavy work during the hottest hours",
    "Long shifts or overtime in the heat",
    "Supervisor refuses or discourages breaks",
    "No toilet access, so workers drink less",
    "No first aid or cooling available",
    "Poor ventilation (indoor or enclosed work)",
    "No hat, light clothing or suitable gear",
    "New workers thrown into heat with no easing in",
    "No heat safety training or warnings",
    "Other (describe)",
]

if "submission_history" not in st.session_state:
    st.session_state.submission_history = []
if "total_audits" not in st.session_state:
    st.session_state.total_audits = 0
if "high_risk_count" not in st.session_state:
    st.session_state.high_risk_count = 0

# ---------------------------------------------------------------
# Design tokens: ink #14181F, slate #5B6472, line #E3E6EB,
# surface #FFFFFF, canvas #F6F7F9, brand #1F3A5F, heat #D9480F
# ---------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&family=Silkscreen:wght@700&display=swap');
    :root {
        --ink:#0A1640; --slate:#5A6685; --mute:#8D98B5; --line:#DDE3F5; --surface:#FFFFFF; --navy:#0A1640; --navy2:#101F5C;
        --blue:#3B63F5; --peri:#E4EAFF; --bg:#F5F7FF; --ok:#1B7F4B; --ok-bg:#E6F5EC;
        --scale:linear-gradient(90deg,#FFD166 0%,#FF9F43 35%,#E8481C 70%,#9F1521 100%);
    }
    html, body, [class*="css"], .stApp { font-family:'Inter',-apple-system,sans-serif; cursor:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='10' fill='%23FFFFFF' fill-opacity='.96' stroke='%230A1640' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='7' fill='none' stroke='%23FFFFFF' stroke-width='2'/%3E%3Ccircle cx='16' cy='16' r='2.5' fill='%23E8481C' stroke='%23FFFFFF' stroke-width='1.5'/%3E%3C/svg%3E") 16 16, auto; }
    .stApp { background:linear-gradient(180deg,#F9FAFF 0%,#EEF1FF 55%,#DCE4FF 100%); color:var(--ink); }
    .stApp::before { content:""; position:fixed; inset:0; pointer-events:none; z-index:0;
        background-image:radial-gradient(rgba(59,99,245,0.16) 1.4px, transparent 1.6px); background-size:26px 26px;
        -webkit-mask-image:linear-gradient(180deg,#000 0%,transparent 55%); mask-image:linear-gradient(180deg,#000 0%,transparent 55%); }
    .stApp::after { content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:0.1;
        background:radial-gradient(ellipse at 12% 18%,rgba(59,99,245,0.24),transparent 36%),radial-gradient(ellipse at 88% 72%,rgba(232,72,28,0.12),transparent 34%); }
    #MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] { visibility:hidden; }
    header[data-testid="stHeader"] { background:transparent; pointer-events:none; }
    .block-container { max-width:1180px; padding-top:1.2rem; padding-bottom:4rem; position:relative; z-index:1; }
    h1,h2,h3,h4,h5 { color:var(--ink); letter-spacing:-0.02em; }
    h4 { font-size:1.35rem !important; font-weight:600 !important; }
    h5 { font-size:0.95rem !important; font-weight:600 !important; }
    [data-testid="stCaptionContainer"] p { color:var(--slate) !important; font-size:0.92rem; }

    /* Sidebar */
    section[data-testid="stSidebar"] { background:var(--navy); }
    section[data-testid="stSidebar"] * { color:#D5DEF7; }
    section[data-testid="stSidebar"] h3 { color:#FFFFFF !important; font-size:1.05rem !important; }
    section[data-testid="stSidebar"] h4 { color:#8FA0D0 !important; font-size:0.8rem !important; font-weight:500 !important; margin-top:1.2rem; }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p { color:#8FA0D0 !important; }
    section[data-testid="stSidebar"] [data-testid="stMetric"] { background:rgba(255,255,255,0.06); border:1px solid rgba(140,165,255,0.2); border-radius:14px; padding:0.8rem 1rem; }
    section[data-testid="stSidebar"] [data-testid="stMetricValue"] { color:#FFFFFF !important; font-weight:600; }
    section[data-testid="stSidebar"] li { font-size:0.88rem; line-height:1.5; margin-bottom:0.4rem; }
    section[data-testid="stSidebar"] strong { color:#FFFFFF; }

    /* Nav */
    .topbar { display:flex; justify-content:space-between; align-items:center; background:rgba(255,255,255,0.8); backdrop-filter:blur(8px); border:1px solid var(--line); border-radius:16px; padding:0.65rem 0.9rem 0.65rem 1rem; margin-bottom:2.4rem; }
    .brand { display:flex; align-items:center; gap:10px; }
    .brand-mark { width:30px; height:30px; border-radius:9px; background:linear-gradient(145deg,#3B63F5,#0A1640); display:flex; align-items:center; justify-content:center; font-size:15px; box-shadow:0 4px 12px rgba(59,99,245,0.4); }
    .brand-name { font-weight:700; font-size:1.02rem; color:var(--ink); letter-spacing:-0.02em; }
    .brand-sub { color:var(--slate); font-size:0.86rem; padding-left:12px; margin-left:4px; border-left:1px solid var(--line); }
    .pill { display:inline-flex; align-items:center; gap:7px; font-size:0.8rem; font-weight:500; padding:6px 14px; border-radius:999px; background:var(--navy); color:#FFFFFF; }
    .dot { width:7px; height:7px; border-radius:50%; background:#5CE29A; }

    /* Hero */
    .hero { text-align:center; padding:0 0 2.2rem 0; }
    .chip { display:inline-flex; align-items:center; gap:8px; font-size:0.82rem; font-weight:500; color:var(--ink); background:#FFFFFF; border:1px solid var(--line); padding:5px 14px 5px 8px; border-radius:999px; margin-bottom:1.3rem; }
    .chip-dot { width:18px; height:18px; border-radius:6px; background:var(--blue); display:inline-block; }
    .hero h1 { font-weight:600; font-size:3.4rem; line-height:1.06; letter-spacing:-0.04em; color:var(--ink); margin:0 auto 1rem auto; max-width:760px; }
    .hero p { color:var(--slate); font-size:1.08rem; line-height:1.6; max-width:560px; margin:0 auto 2.2rem auto; }
    .term { max-width:760px; margin:0 auto; text-align:left; border-radius:22px; background:linear-gradient(180deg,#14246B 0%,#0A1640 100%); border:1px solid rgba(140,165,255,0.25); box-shadow:0 30px 60px -20px rgba(20,36,107,0.55), 0 0 0 8px rgba(59,99,245,0.08); overflow:hidden; }
    .term-bar { display:flex; align-items:center; gap:7px; padding:0.8rem 1.1rem; border-bottom:1px solid rgba(140,165,255,0.15); color:#8FA0D0; font:400 0.76rem 'JetBrains Mono',monospace; }
    .term-bar i { width:10px; height:10px; border-radius:50%; background:rgba(143,160,208,0.4); display:inline-block; }
    .term-bar span { margin-left:8px; }
    .term-body { padding:1.6rem 1.8rem 1.8rem 1.8rem; }
    .term-title { font-family:'Silkscreen',monospace; font-weight:700; font-size:2.6rem; letter-spacing:0.04em; color:#FFFFFF; text-shadow:0 0 24px rgba(120,150,255,0.6); line-height:1; margin-bottom:1.3rem; }
    .term-line { font:400 0.84rem/1.9 'JetBrains Mono',monospace; color:#9FB0DC; }
    .term-line b { color:#FFFFFF; font-weight:500; display:inline-block; width:64px; }
    .term-line em { font-style:normal; color:#7FA0FF; }
    .scale-bar { position:relative; height:10px; border-radius:999px; background:var(--scale); margin-top:1.3rem; }
    .scale-bar.sm { height:8px; margin-top:0; }
    .scale-marker { position:absolute; top:-5px; left:66%; width:4px; height:20px; border-radius:2px; background:#FFFFFF; box-shadow:0 0 0 3px rgba(255,255,255,0.2); }
    .scale-note { margin-top:1rem; font:400 0.78rem 'JetBrains Mono',monospace; color:#8FA0D0; }
    .scale-note b { color:#FFB27A; font-weight:500; }

    /* Cards */
    .cards { display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin:2.6rem 0 2.2rem 0; }
    .card { background:linear-gradient(180deg,#FFFFFF 0%,#F1F4FF 100%); border:1px solid var(--line); border-radius:22px; padding:1.4rem 1.4rem 1.5rem 1.4rem; box-shadow:0 10px 30px -18px rgba(20,36,107,0.35); }
    .card-icon { width:40px; height:40px; border-radius:12px; display:flex; align-items:center; justify-content:center; margin-bottom:1.6rem; background:linear-gradient(145deg,#3B63F5,#1B2F8F); color:#FFFFFF; box-shadow:0 6px 14px -4px rgba(59,99,245,0.55); }
    .card-icon svg { width:20px; height:20px; fill:none; stroke:currentColor; stroke-width:1.8; stroke-linecap:round; stroke-linejoin:round; }
    .card-title { font-weight:600; font-size:1rem; color:var(--ink); letter-spacing:-0.01em; }
    .card-text { color:var(--slate); font-size:0.86rem; margin-top:4px; line-height:1.5; }
    .card.stat { background:linear-gradient(180deg,#14246B 0%,#0A1640 100%); border-color:rgba(140,165,255,0.25); }
    .card.stat .card-title { color:#FFFFFF; font-size:2.6rem; font-weight:600; line-height:1; margin-top:1.4rem; }
    .card.stat .card-text { color:#8FA0D0; margin-top:0.6rem; }
    .stat-label { color:#B9C7F5; font-size:0.84rem; font-weight:500; }
    @media (max-width:900px) { .cards { grid-template-columns:1fr 1fr; } .hero h1 { font-size:2.2rem; } }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap:4px; background:rgba(255,255,255,0.75); border:1px solid var(--line); padding:5px; border-radius:999px; width:fit-content; }
    .stTabs [data-baseweb="tab"] { height:40px; padding:0 20px; border-radius:999px; background:transparent; }
    .stTabs [data-baseweb="tab"] p { color:var(--slate) !important; font-weight:500; font-size:0.92rem; }
    .stTabs [aria-selected="true"] { background:var(--navy) !important; }
    .stTabs [aria-selected="true"] p { color:#FFFFFF !important; font-weight:600; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }
    .stTabs [data-baseweb="tab-panel"] { padding-top:1.8rem; }

    /* Form */
    div[data-testid="stForm"] { background:#FFFFFF; border:1px solid var(--line); border-radius:24px; padding:2rem 2.2rem; box-shadow:0 24px 50px -28px rgba(20,36,107,0.4); }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div { background:#FFFFFF !important; border:1px solid #D3DAF0 !important; border-radius:12px !important; font-size:0.93rem !important; color:var(--ink) !important; }
    div[data-testid="stTextInput"] input::placeholder, div[data-testid="stTextArea"] textarea::placeholder { color:var(--slate) !important; opacity:1; }
    div[data-testid="stNumberInput"] > div > div { background:#FFFFFF !important; border-radius:12px; }
    div[data-testid="stTextInput"] input:focus, div[data-testid="stTextArea"] textarea:focus { border-color:var(--blue) !important; box-shadow:0 0 0 4px rgba(59,99,245,0.15) !important; }
    label p { font-size:0.88rem !important; color:var(--ink) !important; font-weight:500 !important; }
    div[data-testid="stRadio"] label p { font-weight:400 !important; }
    div[data-testid="stCheckbox"] label p { font-weight:400 !important; }
    div[data-testid="stTextInput"] label, div[data-testid="stNumberInput"] label, div[data-testid="stTextArea"] label { color:var(--ink) !important; }
    div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input, div[data-testid="stTextArea"] textarea { -webkit-text-fill-color:var(--ink) !important; }
    hr.divider { margin:1.6rem 0; border:none; border-top:1px solid var(--line); }
    .sec { display:flex; align-items:center; gap:10px; font-weight:600; font-size:1rem; margin:0.2rem 0 0.8rem 0; color:var(--ink); }
    .sec-dot { width:8px; height:8px; border-radius:3px; background:var(--blue); }

    /* Heat readout */
    .readout { background:linear-gradient(180deg,#14246B 0%,#0A1640 100%); border:1px solid rgba(140,165,255,0.25); border-radius:18px; padding:1.2rem 1.5rem 1.3rem 1.5rem; margin:0.6rem 0 1.4rem 0; }
    .readout-top { display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:1rem; }
    .readout-num { font-family:'Silkscreen',monospace; font-size:2.2rem; line-height:1; color:#FFFFFF; text-shadow:0 0 20px rgba(120,150,255,0.55); }
    .readout-label { color:#8FA0D0; font-size:0.8rem; margin-bottom:6px; }
    .readout-state { font-weight:600; font-size:0.82rem; padding:5px 14px; border-radius:999px; }
    .readout-state.danger { background:rgba(232,72,28,0.22); color:#FFB27A; }
    .readout-state.caution { background:rgba(255,209,102,0.18); color:#FFD166; }
    .readout-text { color:#A9B8E0; font-size:0.84rem; margin-top:0.9rem; }
    .scale-ticks { display:flex; justify-content:space-between; color:#6F82B5; font:400 0.72rem 'JetBrains Mono',monospace; margin-top:7px; }

    /* Buttons */
    .stButton > button, .stFormSubmitButton > button { position:relative; isolation:isolate; overflow:hidden; background:linear-gradient(180deg,#1B2F8F 0%,#0A1640 100%) !important; color:#FFFFFF !important; border:none !important; border-radius:999px !important; padding:0.85rem 1.6rem !important; min-height:48px !important; font-weight:600 !important; font-size:0.97rem !important; width:100% !important; cursor:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='10' fill='%23FFFFFF' fill-opacity='.96' stroke='%230A1640' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='7' fill='none' stroke='%23FFFFFF' stroke-width='2'/%3E%3Ccircle cx='16' cy='16' r='2.5' fill='%23E8481C' stroke='%23FFFFFF' stroke-width='1.5'/%3E%3C/svg%3E") 16 16, pointer !important; box-shadow:inset 0 0 0 1px rgba(120,150,255,0.65) !important; transition:none !important; transform:none !important; }
    .stButton > button::after, .stFormSubmitButton > button::after { content:""; position:absolute; z-index:-1; left:50%; top:50%; width:1.2rem; aspect-ratio:1; border:2px solid rgba(190,205,255,0.9); border-radius:50%; background:radial-gradient(circle,rgba(255,255,255,0.42),transparent 68%); opacity:0; pointer-events:none; transform:translate(-50%,-50%) scale(0.35); }
    .stButton > button:hover, .stFormSubmitButton > button:hover { box-shadow:inset 0 0 0 2px rgba(150,175,255,0.95) !important; transform:none !important; }
    .stFormSubmitButton > button:focus-visible { outline:3px solid rgba(59,99,245,0.45) !important; outline-offset:3px; }
    .stButton > button:focus-visible, .stFormSubmitButton > button:focus-visible { outline:3px solid rgba(59,99,245,0.55) !important; outline-offset:3px; }

    /* Results */
    .confirm { display:flex; align-items:center; gap:10px; background:var(--ok-bg); color:var(--ok); border-radius:14px; padding:0.9rem 1.2rem; font-weight:500; margin:1.2rem 0; }
    .result-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin-bottom:1rem; }
    .result { background:linear-gradient(180deg,#FFFFFF 0%,#F1F4FF 100%); border:1px solid var(--line); border-radius:20px; padding:1.2rem 1.4rem; }
    .result-label { color:var(--slate); font-size:0.83rem; font-weight:500; }
    .result-value { font-size:1.9rem; font-weight:600; margin:0.25rem 0; color:var(--ink); letter-spacing:-0.02em; }
    .result-value.ref { font:500 1.05rem 'JetBrains Mono',monospace; padding-top:0.6rem; }
    .result-note { color:var(--mute); font-size:0.8rem; }
    .tier { display:inline-block; font-size:1.15rem; font-weight:600; padding:3px 14px; border-radius:999px; margin:0.2rem 0; }
    .tier.high { background:#FDEBE3; color:#B93A09; } .tier.low { background:var(--ok-bg); color:var(--ok); }
    @media (max-width:800px) { .result-grid { grid-template-columns:1fr; } }
    .app-footer { display:flex; justify-content:space-between; color:var(--mute); font-size:0.82rem; padding-top:1rem; border-top:1px solid var(--line); margin-top:2.5rem; }
    /* ===== Web-app layer ===== */
    section[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"], [data-testid="collapsedControl"] { display:none !important; }
    .block-container { max-width:1120px; }
    .stButton > button[data-testid="stBaseButton-secondary"] { background:rgba(255,255,255,0.85) !important; color:var(--ink) !important; box-shadow:inset 0 0 0 1px var(--line) !important; padding:0.55rem 1rem !important; font-size:0.9rem !important; font-weight:500 !important; }
    .stButton > button[data-testid="stBaseButton-secondary"]:hover { box-shadow:inset 0 0 0 1px var(--blue) !important; color:var(--blue) !important; }
    .navrow { align-items:center; }
    .wordmark { font-family:'Silkscreen',monospace; font-weight:700; font-size:clamp(3rem,9vw,6rem); color:var(--navy); letter-spacing:0.04em; line-height:1; margin:0.4rem 0 1.1rem 0; text-shadow:0 0 50px rgba(59,99,245,0.35); }
    .tagline { font-weight:600; font-size:clamp(1.5rem,3.2vw,2.3rem); letter-spacing:-0.03em; line-height:1.15; color:var(--ink); max-width:700px; margin:0 auto 1rem auto; }
    .hero { padding:3.2rem 0 1rem 0; }
    .scroll-hint { margin:2.2rem 0 0 0; color:var(--mute); font-size:0.84rem; }
    .section { margin:5.5rem 0 1.8rem 0; text-align:center; }
    .section h2 { font-size:2.3rem; font-weight:600; letter-spacing:-0.03em; margin:0.9rem 0 0.6rem 0; }
    .section p { color:var(--slate); font-size:1.02rem; line-height:1.6; max-width:560px; margin:0 auto; }
    .steps { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }
    .step { background:rgba(255,255,255,0.9); border:1px solid var(--line); border-radius:22px; padding:1.5rem 1.5rem 1.7rem 1.5rem; }
    .step-n { font-family:'Silkscreen',monospace; font-size:2.2rem; color:var(--blue); line-height:1; margin-bottom:1.2rem; }
    .step h3 { font-size:1.05rem !important; font-weight:600; margin:0 0 6px 0; }
    .step p { color:var(--slate); font-size:0.88rem; line-height:1.55; margin:0; }
    div[data-testid="stVerticalBlockBorderWrapper"] { background:linear-gradient(180deg,#FFFFFF 0%,#F1F4FF 100%); border:1px solid var(--line) !important; border-radius:24px !important; padding:0.6rem 0.5rem 0.4rem 0.5rem; box-shadow:0 18px 40px -26px rgba(20,36,107,0.45); }
    .mode-n { color:var(--mute); font-size:0.8rem; font-weight:500; float:right; }
    .mode-need { min-height:5.7em; box-sizing:border-box; margin:1rem 0 0.4rem 0; padding-top:0.9rem; border-top:1px solid var(--line); color:var(--slate); font-size:0.82rem; line-height:1.5; }
    .mode-need b { color:var(--ink); font-weight:600; }
    @media (hover:hover) and (pointer:fine) {
        .stButton > button:not([data-testid="stBaseButton-secondary"]):hover, .stFormSubmitButton > button:hover { background:linear-gradient(180deg,#3556C7 0%,#142A70 100%) !important; box-shadow:inset 0 0 0 2px rgba(190,205,255,0.95) !important; }
        .stButton > button:hover::after, .stFormSubmitButton > button:hover::after { animation:splash-ring 520ms ease-out both; }
        div[data-testid="stTextInput"] input:hover, div[data-testid="stNumberInput"] input:hover,
        div[data-testid="stTextArea"] textarea:hover, div[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color:#718CF2 !important; box-shadow:0 0 0 2px rgba(59,99,245,0.12) !important; }
        .card, .step, .score-card, .level, .node, .result { transition:border-color .15s ease, box-shadow .15s ease; }
        .card:hover, .step:hover, .score-card:hover, .level:hover, .node:hover, .result:hover { border-color:rgba(59,99,245,0.55); box-shadow:0 12px 30px -20px rgba(20,36,107,0.5); }
        .stColumn:has(.st-key-cta_mode1), .stColumn:has(.st-key-cta_mode2), .stColumn:has(.st-key-cta_mode3) { border-radius:24px; transition:box-shadow .15s ease; }
        .stColumn:has(.st-key-cta_mode1):hover, .stColumn:has(.st-key-cta_mode2):hover, .stColumn:has(.st-key-cta_mode3):hover { box-shadow:0 12px 30px -20px rgba(20,36,107,0.5); }
        div[data-testid="stRadio"] label, div[data-testid="stCheckbox"] label { cursor:pointer; }
        div[data-testid="stRadio"] label:hover p, div[data-testid="stCheckbox"] label:hover p { color:var(--blue) !important; }
    }
    @media (prefers-reduced-motion:no-preference) {
        .stApp::after { animation:ambient-glow 18s ease-in-out infinite alternate; }
        @keyframes ambient-glow { from { opacity:0.07; } to { opacity:0.15; } }
        @keyframes splash-ring { 0% { opacity:0.85; transform:translate(-50%,-50%) scale(0.35); } 100% { opacity:0; transform:translate(-50%,-50%) scale(5); } }
        @supports (animation-timeline:view()) {
            .reveal { animation:reveal-in 1ms linear both; animation-timeline:view(); animation-range:entry 0% entry 18%; }
            @keyframes reveal-in { from { opacity:0.78; } to { opacity:1; } }
        }
    }
    .teaser { background:linear-gradient(180deg,#14246B 0%,#0A1640 100%); border:1px solid rgba(140,165,255,0.25); border-radius:26px; padding:2.4rem 2.6rem; display:flex; justify-content:space-between; align-items:center; gap:2rem; margin-top:1rem; }
    .teaser h2 { color:#FFFFFF; font-size:1.8rem; font-weight:600; letter-spacing:-0.03em; margin:0 0 0.5rem 0; }
    .teaser p { color:#A9B8E0; margin:0; max-width:420px; font-size:0.95rem; line-height:1.55; }
    .teaser-stats { display:flex; gap:2.2rem; }
    .teaser-stats div { font-family:'Silkscreen',monospace; font-size:2.6rem; color:#FFFFFF; line-height:1; text-shadow:0 0 20px rgba(120,150,255,0.5); }
    .teaser-stats span { display:block; font:400 0.78rem 'Inter',sans-serif; color:#8FA0D0; margin-top:8px; text-shadow:none; }
    .kpis { display:grid; grid-template-columns:repeat(3,1fr); gap:16px; margin:1.4rem 0; }
    .kpis .card-title { font-size:2.2rem; font-weight:600; margin-top:0.5rem; line-height:1; }
    .page-chip { display:inline-block; font-size:0.8rem; font-weight:500; color:var(--blue); background:var(--peri); padding:4px 12px; border-radius:999px; margin:0.6rem 0 0.4rem 0; }
    @media (max-width:900px) { .steps, .kpis { grid-template-columns:1fr; } .teaser { flex-direction:column; align-items:flex-start; } }
    .score { display:grid; grid-template-columns:1.25fr 1fr; gap:16px; text-align:left; }
    .score-card { background:#FFFFFF; border:1px solid var(--line); border-radius:24px; padding:1.6rem 1.8rem; }
    .score-card h3 { font-size:1.05rem !important; font-weight:600; margin:0 0 0.8rem 0; }
    .score-row { display:flex; justify-content:space-between; font-size:0.9rem; color:var(--ink); margin-top:0.85rem; }
    .pts { font-family:'JetBrains Mono',monospace; font-weight:500; color:var(--blue); }
    .bar { height:5px; border-radius:99px; background:var(--peri); margin-top:6px; }
    .bar i { display:block; height:100%; border-radius:99px; background:var(--blue); }
    .score-card.dark { background:linear-gradient(180deg,#14246B 0%,#0A1640 100%); border-color:rgba(140,165,255,0.25); }
    .score-card.dark h3, .score-card.dark .score-row { color:#FFFFFF; }
    .score-card.dark .pts { color:#9DB4FF; }
    .score-card.dark .sub { color:#8FA0D0; font-size:0.82rem; margin:-0.4rem 0 0.6rem 0; }
    .total { display:flex; justify-content:space-between; align-items:center; margin-top:1.1rem; padding-top:1rem; border-top:1px solid rgba(140,165,255,0.25); color:#FFFFFF; font-weight:600; }
    .total .tier { background:rgba(232,72,28,0.22); color:#FFB27A; margin:0; font-size:0.95rem; }
    .levels { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-top:16px; }
    .level { background:#FFFFFF; border:1px solid var(--line); border-radius:16px; padding:0.9rem 1.1rem; text-align:left; }
    .level b { display:block; font-size:0.95rem; } .level span { font-size:0.8rem; color:var(--slate); }
    .level.alert { border-color:#F5C4A5; background:#FFF7F2; }
    .flow { display:flex; align-items:stretch; gap:8px; flex-wrap:wrap; justify-content:center; }
    .node { background:#FFFFFF; border:1px solid var(--line); border-radius:16px; padding:0.9rem 1.1rem; min-width:150px; flex:1; text-align:left; }
    .node b { display:block; font-size:0.92rem; } .node span { font-size:0.78rem; color:var(--slate); line-height:1.4; display:block; margin-top:3px; }
    .arrow { align-self:center; color:var(--blue); font-weight:600; }
    .road { display:grid; grid-template-columns:repeat(3,1fr); gap:12px; }
    .road div { background:rgba(255,255,255,0.7); border:1px dashed #B9C5EE; border-radius:16px; padding:1rem 1.2rem; font-size:0.9rem; font-weight:500; text-align:left; }
    .road span { display:block; color:var(--slate); font-size:0.8rem; font-weight:400; margin-top:3px; }
    @media (max-width:900px) { .score, .levels, .road { grid-template-columns:1fr; } .arrow { display:none; } }
</style>
""", unsafe_allow_html=True)

DIVIDER = "<hr class='divider'>"


# --- Reusable heat input module ---
def show_heat_inputs(prefix=""):
    st.markdown('<div class="sec"><span class="sec-dot"></span>Heat conditions</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        temperature = st.number_input(
            "Air temperature (°C)", min_value=20, max_value=55, value=38,
            help="Dry-bulb air temperature at worksite", key=f"{prefix}temp"
        )
    with c2:
        humidity = st.number_input(
            "Relative humidity (%)", min_value=0, max_value=100, value=60,
            help="Relative air humidity from sensor or local forecast", key=f"{prefix}hum"
        )

    t = temperature
    rh = humidity
    apparent_t = -8.784 + 1.611*t + 2.338*rh - 0.146*t*rh - 0.0123*(t**2) - 0.0164*(rh**2) + 0.0022*(t**2)*rh + 0.00072*t*(rh**2) - 0.00000358*(t**2)*(rh**2)
    apparent_t = max(t, round(apparent_t, 1))

    if apparent_t >= 51:
        level, label = "danger", "Extreme danger"
    elif apparent_t >= 39:
        level, label = "danger", "Danger"
    elif apparent_t >= 32:
        level, label = "caution", "Extreme caution"
    else:
        level, label = "caution", "Caution"
    text = "For reference only. Your risk level is scored after you submit, using temperature, humidity, water, shade, rest and symptoms."
    pos = max(0, min(100, (apparent_t - 27) / (55 - 27) * 100))

    st.markdown(f"""
    <div class="readout">
        <div class="readout-top">
            <div><div class="readout-label">Feels-like temperature</div><div class="readout-num">{apparent_t}°C</div></div>
            <div class="readout-state {level}">{label}</div>
        </div>
        <div class="scale-bar sm"><div class="scale-marker" style="left:{pos}%;"></div></div>
        <div class="scale-ticks"><span>27°</span><span>32°</span><span>39°</span><span>51°</span></div>
        <div class="readout-text">{text}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="sec"><span class="sec-dot"></span>Water, shade and rest</div>', unsafe_allow_html=True)
    r1, r2 = st.columns(2)
    with r1:
        water = st.radio("Is clean drinking water available on site?", ["Yes", "No"], horizontal=True, key=f"{prefix}water")
        break_taken = st.radio("Has the worker taken a rest break recently?", ["Yes", "No"], horizontal=True, key=f"{prefix}break")
    with r2:
        shade = st.radio("Is shade or a designated rest area accessible?", ["Yes", "No"], horizontal=True, key=f"{prefix}shade")
        symptoms = st.radio("Is the worker feeling dizzy, very tired or unwell?", ["No", "Yes"], horizontal=True, key=f"{prefix}sym")

    st.markdown(
        '<div class="sec" style="margin-top:1.4rem;"><span class="sec-dot"></span>Other problems at this worksite '
        '<span style="color:var(--mute);font-weight:400;">(optional)</span></div>',
        unsafe_allow_html=True,
    )
    p1, p2 = st.columns(2)
    selected_problems = []
    for i, option in enumerate(PROBLEM_OPTIONS):
        with (p1 if i % 2 == 0 else p2):
            if st.checkbox(option, key=f"{prefix}prob{i}"):
                selected_problems.append(option)
    problem_details = st.text_area(
        "Anything else we should know?",
        placeholder="Describe any other problem, especially if you ticked “Other”",
        key=f"{prefix}probtext",
    )

    return {
        "temperature": temperature,
        "humidity": humidity,
        "waterAvailable": water == "Yes",
        "shadeAvailable": shade == "Yes",
        "restBreakTaken": break_taken == "Yes",
        "symptoms": symptoms == "Yes",
        "otherProblems": selected_problems,
        "otherProblemsDetails": problem_details.strip(),
    }


# --- Submission ---
def submit_report(payload):
    with st.spinner("Submitting report..."):
        try:
            response = requests.post(API_URL, json=payload, timeout=20)
            result = response.json()

            if response.status_code == 200:
                risk_level = result.get("riskLevel", "Unknown")
                risk_score = result.get("riskScore", 0)
                report_id = result.get("reportId", "N/A")
                alert_sent = result.get("alertSent", False)

                st.session_state.total_audits += 1
                if risk_level in ["High", "Extreme"]:
                    st.session_state.high_risk_count += 1

                st.session_state.submission_history.insert(0, {
                    "Timestamp": datetime.datetime.now().strftime("%H:%M:%S"),
                    "Report ID": report_id,
                    "Channel": payload.get("channel"),
                    "Work Type": payload.get("workType"),
                    "Location": payload.get("location"),
                    "Risk Level": risk_level,
                    "Risk Score": f"{risk_score}/100"
                })

                tier_class = "high" if risk_level in ["High", "Extreme"] else "low"

                st.markdown("""
                <div class="confirm"><span>✓</span><span>Report saved successfully.</span></div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div class="result-grid">
                    <div class="result">
                        <div class="result-label">Risk level</div>
                        <div class="tier {tier_class}">{risk_level}</div>
                        <div class="result-note">Based on heat, water, shade and symptoms</div>
                    </div>
                    <div class="result">
                        <div class="result-label">Risk score</div>
                        <div class="result-value">{risk_score}<span style="font-size:1rem;color:#8A93A1;"> / 100</span></div>
                        <div class="result-note">Higher means more urgent</div>
                    </div>
                    <div class="result">
                        <div class="result-label">Report ID</div>
                        <div class="result-value ref">{str(report_id)[:14]}</div>
                        <div class="result-note">Quote this when following up</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if alert_sent:
                    st.warning("**This is a high-risk report.** A HeatLine alert has been sent.")
                elif risk_level in ["High", "Extreme"]:
                    st.warning("**This is a high-risk report, but the email alert could not be sent.** The report is saved. Follow up directly.")

                with st.expander("View raw API response"):
                    st.json(result)

            else:
                st.error("Could not submit report. Please try again.")
                st.write(result)

        except Exception as e:
            st.error("Could not submit report. Please try again.")
            st.write(e)


def render_mode1():
    st.markdown("#### Report heat conditions")
    st.caption("For workers with a smartphone who can submit directly from the worksite.")

    with st.form("worker_self_report"):
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            work_type = st.selectbox("Work type", WORK_TYPES, key="w1_type")
        with col_w2:
            location = st.text_input("Worksite location", placeholder="Enter area, city, or worksite name", key="w1_loc")

        heat_data = show_heat_inputs("w1_")

        submitted = st.form_submit_button("Submit my heat report")

    if submitted:
        payload = {
            "channel": "web",
            "reportedBy": "self",
            "workerPhone": "",
            "agentName": "",
            "organization": "",
            "reporterName": "",
            "fixerName": "",
            "fixerContact": "",
            "consentConfirmed": True,
            "actionNeeded": "",
            "workType": work_type,
            "location": location,
            **heat_data
        }
        submit_report(payload)


def render_mode2():
    st.markdown("#### Phone-assisted report")
    st.caption("For workers without a smartphone. They report by calling a number or sending a text, using only their keypad.")

    if not PHONE_DEMO_FILE.exists():
        st.error(f"Could not find {PHONE_DEMO_FILE.name}. Save it in the same folder as this app file.")
        return

    html = PHONE_DEMO_FILE.read_text(encoding="utf-8")
    components.html(html, height=1050, scrolling=True)


def render_mode3():
    st.markdown("#### Escalate unsafe conditions")
    st.caption("For students, NGOs, unions, community groups, or company safety staff who find unsafe heat conditions and need to assign them to someone on site.")

    with st.form("organization_report"):
        st.markdown("##### Reporting organization")
        o1, o2, o3 = st.columns(3)
        with o1:
            organization = st.text_input("Organization or group name", placeholder="Example: Chennai Heat Action Team", key="o3_org")
        with o2:
            reporter_name = st.text_input("Your full name", placeholder="Enter your name", key="o3_repname")
        with o3:
            organization_type = st.selectbox("Organization type", ORGANIZATION_TYPES, key="o3_orgtype")

        st.markdown(DIVIDER, unsafe_allow_html=True)
        st.markdown("##### Worksite")
        o4, o5 = st.columns(2)
        with o4:
            work_type = st.selectbox("Work type", WORK_TYPES, key="o3_worktype")
        with o5:
            location = st.text_input("Location", placeholder="Enter area, city, or worksite name", key="o3_loc")

        heat_data = show_heat_inputs("o3_")

        st.markdown(DIVIDER, unsafe_allow_html=True)
        st.markdown("##### Who should fix this")
        f1, f2 = st.columns(2)
        with f1:
            fixer_name = st.text_input("Responsible person", placeholder="Example: Site supervisor, contractor, ward officer", key="o3_fixer")
        with f2:
            fixer_contact = st.text_input("Their contact (phone or email)", placeholder="Phone number or email", key="o3_fixercontact")

        action_needed = st.selectbox("Action needed most urgently", ACTION_OPTIONS, key="o3_action")

        action_details = st.text_area(
            "Additional details",
            placeholder="Describe the worksite conditions and the steps needed",
            key="o3_details"
        )

        submitted = st.form_submit_button("Submit escalation")

    if submitted:
        if not organization:
            st.error("Please enter the organization or group name.")
        elif not reporter_name:
            st.error("Please enter your name.")
        elif not fixer_name:
            st.error("Please enter the fixer or responsible person.")
        else:
            payload = {
                "channel": "organization",
                "reportedBy": "organization",
                "workerPhone": "",
                "agentName": reporter_name,
                "organization": organization,
                "reporterName": reporter_name,
                "fixerName": fixer_name,
                "fixerContact": fixer_contact,
                "consentConfirmed": True,
                "actionNeeded": action_needed,
                "workType": work_type,
                "location": location,
                **heat_data
            }
            submit_report(payload)


# ==============================================================
# Web-app views
# ==============================================================
MODES = {
    "mode1": {"n": "1", "title": "Worker self-report", "icon": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
              "text": "You are a worker with a smartphone. Report heat conditions yourself, right from the worksite.",
              "need": "<b>You'll need:</b> your work type, location, and the current temperature and humidity.", "cta": "Report as a worker"},
    "mode2": {"n": "2", "title": "Phone-assisted report", "icon": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2z"/>',
              "text": "The worker has a basic phone. They call a number or send a text and answer by keypad. No app or data plan needed.",
              "need": "<b>You'll need:</b> nothing. Try the simulated call and text flow.", "cta": "Try the phone channel"},
    "mode3": {"n": "3", "title": "Organization report", "icon": '<rect x="4" y="3" width="16" height="18" rx="1"/><path d="M9 7h2M13 7h2M9 11h2M13 11h2M10 21v-4h4v4"/>',
              "text": "You are a student, NGO, union or safety officer. Report unsafe conditions and assign a fixer to act on them.",
              "need": "<b>You'll need:</b> your organization, the responsible person, and the action required.", "cta": "Escalate a problem"},
}

def set_view(v):
    st.session_state.view = v

def nav_bar():
    c1, c2, c3 = st.columns([6, 1.2, 1.6])
    with c1:
        st.markdown('<div class="brand" style="padding:0.5rem 0;"><div class="brand-mark">🌡️</div><span class="brand-name">HeatLine</span><span class="brand-sub">Field safety console</span></div>', unsafe_allow_html=True)
    with c2:
        st.button("Home", key="nav_home", on_click=set_view, args=("home",), type="secondary", use_container_width=True)
    with c3:
        st.button("Track reports", key="nav_track", on_click=set_view, args=("tracker",), type="secondary", use_container_width=True)
    st.markdown("<hr class='divider' style='margin:0.4rem 0 0 0;'>", unsafe_allow_html=True)

def render_home():
    st.markdown("""
    <div class="hero">
        <span class="chip"><span class="chip-dot"></span>Heat safety for outdoor workers</span>
        <div class="wordmark">HEATLINE</div>
        <div class="tagline">Spot heat risk before it hurts someone.</div>
        <p>Record temperature and humidity, check whether workers have water, shade and rest,
        and send urgent cases to the people who can fix them.</p>
        <div class="scroll-hint">Scroll to see how it works ↓</div>
    </div>
    <div class="term reveal">
        <div class="term-bar"><i></i><i></i><i></i><span>heatline / risk levels</span></div>
        <div class="term-body">
            <div class="term-line"><b>0–34</b> <em>low</em> · saved</div>
            <div class="term-line"><b>35–54</b> <em>moderate</em> · saved</div>
            <div class="term-line"><b>55–74</b> <em>high</em> · saved + email alert</div>
            <div class="term-line"><b>75+</b> <em>extreme</em> · saved + email alert</div>
            <div class="scale-bar"><div class="scale-marker" style="left:42%;"></div></div>
            <div class="scale-note">risk score 0 to 130 · alert at <b>55 or higher</b></div>
        </div>
    </div>

    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>How it works</span>
        <h2>From a hot worksite to a fix, in three steps.</h2>
        <p>One short report is all it takes to turn a risky afternoon into an action someone is responsible for.</p>
    </div>
    <div class="steps">
        <div class="step reveal"><div class="step-n">01</div><h3>Report conditions</h3><p>Enter work type, location, temperature and humidity, and say whether water, shade, a rest break and symptoms apply.</p></div>
        <div class="step reveal"><div class="step-n">02</div><h3>Get a risk score</h3><p>A transparent point model returns a score and a level: Low, Moderate, High or Extreme.</p></div>
        <div class="step reveal"><div class="step-n">03</div><h3>Store and alert</h3><p>Every report is saved. High and Extreme cases also send an email alert to the HeatLine team.</p></div>
    </div>

    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>Choose your mode</span>
        <h2>Who is reporting?</h2>
        <p>Pick the option that matches your situation. Each one opens its own report.</p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")
    for col, (key, m) in zip(cols, MODES.items()):
        with col:
            with st.container(border=True):
                st.markdown(f"""
                <div style="padding:0.9rem 0.8rem 0 0.8rem;">
                    <span class="mode-n">Mode {m['n']}</span>
                    <div class="card-icon"><svg viewBox="0 0 24 24">{m['icon']}</svg></div>
                    <div class="card-title" style="font-size:1.15rem;">{m['title']}</div>
                    <div class="card-text" style="font-size:0.9rem;min-height:4.4em;">{m['text']}</div>
                    <div class="mode-need">{m['need']}</div>
                </div>
                """, unsafe_allow_html=True)
                st.button(m["cta"], key=f"cta_{key}", on_click=set_view, args=(key,), type="primary", use_container_width=True)

    SCORE_ROWS = [("Temperature 34–36.9°C", 20), ("Temperature 37–39.9°C", 30), ("Temperature 40°C or above", 40),
                  ("Humidity 55–69%", 10), ("Humidity 70% or above", 20), ("No drinking water", 20),
                  ("No shade or rest area", 15), ("No recent rest break", 10), ("Worker reports symptoms", 25)]
    EXAMPLE = [("Temperature 41°C", 40), ("Humidity 75%", 20), ("No water", 20), ("No shade", 15), ("No rest break", 10), ("Symptoms", 25)]
    rows = "".join(f'<div class="score-row"><span>{l}</span><span class="pts">+{p}</span></div><div class="bar"><i style="width:{p/40*100}%"></i></div>' for l, p in SCORE_ROWS)
    ex = "".join(f'<div class="score-row"><span>{l}</span><span class="pts">+{p}</span></div>' for l, p in EXAMPLE)
    st.markdown(f"""
    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>How risk is scored</span>
        <h2>Water. Rest. Shade. Every point is explained.</h2>
        <p>The score checks the protections that prevent heat illness: cool water, shade, and regular breaks. Symptoms count most, because dizziness or fainting can signal heat exhaustion.</p>
    </div>
    <div class="score reveal">
        <div class="score-card"><h3>The scoring model</h3>{rows}</div>
        <div class="score-card dark"><h3>Worked example: a construction worker in Chennai</h3><div class="sub">Dizzy, with no water, shade or break</div>{ex}
            <div class="total"><span>Total score 130</span><span class="tier">Extreme</span></div></div>
    </div>
    <div class="levels reveal">
        <div class="level"><b>Low · 0–34</b><span>Report is saved</span></div>
        <div class="level"><b>Moderate · 35–54</b><span>Report is saved</span></div>
        <div class="level alert"><b>High · 55–74</b><span>Saved and email alert sent</span></div>
        <div class="level alert"><b>Extreme · 75+</b><span>Saved and email alert sent</span></div>
    </div>

    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>Behind the scenes</span>
        <h2>What happens when you press submit.</h2>
    </div>
    <div class="flow reveal">
        <div class="node"><b>Streamlit app</b><span>Sends the report as JSON over HTTPS</span></div><div class="arrow">→</div>
        <div class="node"><b>API Gateway</b><span>Receives the request</span></div><div class="arrow">→</div>
        <div class="node"><b>Lambda</b><span>Validates the report and calculates risk</span></div><div class="arrow">→</div>
        <div class="node"><b>DynamoDB</b><span>Stores every report permanently</span></div><div class="arrow">→</div>
        <div class="node"><b>SNS</b><span>Emails an alert for High or Extreme risk</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>Track</span>
    </div>
    <div class="teaser reveal">
        <div>
            <h2>Every report, in one place.</h2>
            <p>Review each report you submit, with its risk level and score, and filter to the High and Extreme cases that need follow-up.</p>
        </div>
        <div class="teaser-stats">
            <div>{st.session_state.total_audits}<span>reports</span></div>
            <div>{st.session_state.high_risk_count}<span>high or extreme</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.button("Open tracker", key="cta_tracker", on_click=set_view, args=("tracker",), type="primary")
    st.markdown("""
    <div class="section reveal">
        <span class="chip"><span class="chip-dot"></span>Next up</span>
        <h2>Where HeatLine goes from here.</h2>
        <p>The MVP reports, scores, stores and alerts. These are the next steps to close the loop.</p>
    </div>
    <div class="road reveal">
        <div>Fixer dashboard<span>Open High and Extreme reports in one view</span></div>
        <div>Report status<span>Fixers mark reports in progress or resolved</span></div>
        <div>Tamil and Hindi<span>Language support for workers</span></div>
        <div>SMS reporting<span>Basic-phone reporting via AWS End User Messaging</span></div>
        <div>IVR reporting<span>Voice reporting through Amazon Connect</span></div>
        <div>Public heat-risk map<span>Risk by location</span></div>
    </div>
    """, unsafe_allow_html=True)

def mode_header(key):
    m = MODES[key]
    st.button("← All modes", key=f"back_{key}", on_click=set_view, args=("home",), type="secondary")
    st.markdown(f'<span class="page-chip">Mode {m["n"]} of 3</span>', unsafe_allow_html=True)

def render_tracker():
    st.markdown('<span class="page-chip">Tracker</span>', unsafe_allow_html=True)
    st.markdown("#### Track reports")
    st.caption("Every report is stored permanently in DynamoDB. This list shows the reports you submitted in this session.")
    total, high = st.session_state.total_audits, st.session_state.high_risk_count
    st.markdown(f"""
    <div class="kpis">
        <div class="card"><div class="stat-label" style="color:var(--slate);">Reports submitted</div><div class="card-title">{total}</div></div>
        <div class="card stat"><div class="stat-label">High or extreme</div><div class="card-title" style="margin-top:0.5rem;">{high}</div></div>
        <div class="card"><div class="stat-label" style="color:var(--slate);">Share flagged high risk</div><div class="card-title">{round(high / total * 100) if total else 0}%</div></div>
    </div>
    """, unsafe_allow_html=True)

    hist = st.session_state.submission_history
    if not hist:
        st.info("No reports yet. Choose a mode on the home page and submit your first report.")
        st.button("Start a report", key="empty_start", on_click=set_view, args=("home",), type="primary")
    else:
        levels = ["All"] + sorted({h["Risk Level"] for h in hist})
        pick = st.selectbox("Filter by risk level", levels, key="trk_filter")
        rows = hist if pick == "All" else [h for h in hist if h["Risk Level"] == pick]
        st.dataframe(rows, use_container_width=True, hide_index=True)

# ---------------- Router ----------------
if "view" not in st.session_state:
    st.session_state.view = "home"

nav_bar()
view = st.session_state.view

if view == "home":
    render_home()
elif view in MODES:
    mode_header(view)
    {"mode1": render_mode1, "mode2": render_mode2, "mode3": render_mode3}[view]()
else:
    render_tracker()

st.markdown("""
<div class="app-footer">
    <div>Worker self-report · Phone-assisted · Organization escalation</div>
    <div>Prototype</div>
</div>
""", unsafe_allow_html=True)