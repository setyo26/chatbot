import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Nusantara Guide AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Reset & Base */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"] { visibility: hidden !important; display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #F4F5F7 !important; }

/* ── LEFT SIDEBAR ── */
.sidebar-wrapper {
    background: #FFFFFF;
    height: 100vh;
    padding: 20px 14px;
    border-right: 1px solid #EBEBEB;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
}
.brand-logo {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 22px;
}
.brand-icon {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6);
    color: white; font-weight: 900; font-size: 18px;
    width: 38px; height: 38px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
}
.brand-name { font-size: 1.2rem; font-weight: 700; color: #1A1A2E; }

.search-box {
    background: #F4F5F7; border-radius: 8px;
    padding: 9px 14px; margin-bottom: 18px;
    font-size: 0.85rem; color: #999;
    border: 1px solid #E5E7EB;
}
.nav-section { margin-bottom: 18px; }
.nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 9px 12px; border-radius: 8px;
    font-size: 0.9rem; color: #444; cursor: pointer;
    margin-bottom: 4px; font-weight: 500;
}
.nav-item:hover, .nav-item.active {
    background: #F0EBFF; color: #7C3AED;
}
.nav-item .badge {
    margin-left: auto; background: #EDE9FE;
    color: #7C3AED; font-size: 0.7rem;
    padding: 2px 8px; border-radius: 20px; font-weight: 600;
}
.nav-label { font-size: 0.72rem; color: #AAA; font-weight: 600;
    text-transform: uppercase; letter-spacing: .05em;
    margin: 14px 0 6px 12px; }
.pinned-item {
    padding: 7px 12px; font-size: 0.82rem; color: #555;
    border-radius: 6px; cursor: pointer;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pinned-item:hover { background: #F9FAFB; }

.new-chat-btn {
    margin-top: auto;
    background: linear-gradient(135deg, #8B5CF6, #3B82F6);
    color: white; border: none; border-radius: 10px;
    padding: 12px; font-weight: 700; font-size: 0.9rem;
    width: 100%; cursor: pointer; text-align: center;
}

/* ── RIGHT MAIN PANEL ── */
.main-wrapper {
    padding: 28px 36px;
    height: 100vh;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
}
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 22px;
}
.topbar-title { font-size: 1.5rem; font-weight: 800; color: #1A1A2E; }
.topbar-search {
    background: white; border-radius: 8px; border: 1px solid #E5E7EB;
    padding: 9px 16px; font-size: 0.85rem; color: #888; width: 240px;
}
.btn-new {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6);
    color: white; border: none; border-radius: 8px;
    padding: 9px 18px; font-weight: 700; font-size: 0.85rem; cursor: pointer;
}

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    border-radius: 18px; padding: 40px 24px; text-align: center;
    color: white; margin-bottom: 28px;
    box-shadow: 0 8px 24px rgba(139,92,246,0.3);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 160px; height: 160px; border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.hero-banner::after {
    content: ''; position: absolute; bottom: -60px; left: -20px;
    width: 200px; height: 200px; border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.hero-title { font-size: 1.9rem; font-weight: 800; margin: 0 0 8px; }
.hero-sub { font-size: 1rem; opacity: .85; margin: 0; }

/* ── CHAT MESSAGES ── */
.chat-section-title {
    font-size: 1rem; font-weight: 700; color: #1A1A2E;
    margin: 0 0 14px;
}
.msg-card {
    background: white; border-radius: 14px; padding: 16px 20px;
    margin-bottom: 12px; box-shadow: 0 1px 4px rgba(0,0,0,0.07);
    border: 1px solid #F0F0F0; display: flex; gap: 14px; align-items: flex-start;
}
.msg-avatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; background: #EDE9FE;
}
.msg-avatar.user { background: #DBEAFE; }
.msg-body { flex: 1; min-width: 0; }
.msg-header { display: flex; justify-content: space-between;
    align-items: center; margin-bottom: 4px; }
.msg-name { font-weight: 700; font-size: 0.85rem; color: #1A1A2E; }
.msg-time { font-size: 0.75rem; color: #AAA; }
.msg-text { font-size: 0.88rem; color: #555; line-height: 1.55; }
.msg-footer { display: flex; gap: 14px; margin-top: 8px; align-items: center; }
.msg-meta { font-size: 0.74rem; color: #AAA; }

/* Typing indicator */
.typing { display: inline-flex; gap: 4px; padding: 6px 0; }
.typing span {
    width: 7px; height: 7px; border-radius: 50%;
    background: #8B5CF6; animation: bounce 1s infinite;
}
.typing span:nth-child(2) { animation-delay: .2s; }
.typing span:nth-child(3) { animation-delay: .4s; }
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}

/* ── INPUT AREA ── */
.input-area {
    position: sticky; bottom: 0; background: #F4F5F7;
    padding: 14px 0 0;
}

/* Streamlit default chat input override */
.stChatInputContainer {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    background: white !important;
}
.stChatInputContainer:focus-within {
    border-color: #8B5CF6 !important;
    box-shadow: 0 4px 16px rgba(139,92,246,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ── API KEY SETUP ────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")

# ── MODEL SETUP ─────────────────────────────────────────────────────────────
system_instruction = (
    "Kamu adalah AI Asisten pintar bernama Bima. "
    "Tugas utamamu adalah memandu perjalanan wisata dan memberikan rekomendasi kuliner Indonesia. "
    "Jawablah dengan gaya yang modern, profesional namun tetap ramah dan bersahabat."
)
generation_config = {
    "temperature": 0.75, "top_p": 0.9,
    "top_k": 50, "max_output_tokens": 1024,
}

@st.cache_resource
def get_model(key):
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

# ── CHAT HISTORY ─────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Halo! Saya siap membantu Anda merencanakan perjalanan atau mencari referensi kuliner di Indonesia. Ada yang ingin ditanyakan hari ini?"
    }]

# ── 2-COLUMN LAYOUT ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 3.5])

# ──────────────────── LEFT SIDEBAR ──────────────────────────────────────────
with col_left:
    st.markdown("""
    <div class="sidebar-wrapper">
        <div class="brand-logo">
            <div class="brand-icon">N</div>
            <div class="brand-name">Nusantara AI</div>
        </div>
        <div class="search-box">🔍&nbsp; Search for chats...</div>
        <div class="nav-section">
            <div class="nav-item active">💬 Chats <span class="badge">3</span></div>
            <div class="nav-item">📚 Library <span class="badge">2</span></div>
            <div class="nav-item">🧩 Apps <span class="badge">5</span></div>
        </div>
        <div class="nav-label">Pinned</div>
        <div class="pinned-item">🗺️ Rekomendasi Wisata Lombok...</div>
        <div class="pinned-item">🍜 Kuliner terbaik di Jogja...</div>
        <div class="pinned-item">🏖️ Itinerary 5 hari Bali...</div>
        <div class="nav-label">Chat History</div>
        <div class="pinned-item">Hidden gems di Raja Ampat...</div>
        <div class="pinned-item">Makanan khas Padang...</div>
        <div class="pinned-item">Tempat camping Dieng...</div>
    </div>
    """, unsafe_allow_html=True)
    
    # New Chat Button
    if st.button("＋  Start New Chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Halo! Saya siap membantu Anda merencanakan perjalanan atau mencari referensi kuliner di Indonesia. Ada yang ingin ditanyakan hari ini?"
        }]
        st.rerun()

# ──────────────────── RIGHT MAIN PANEL ──────────────────────────────────────
with col_right:
    # Top Bar
    st.markdown("""
    <div class="topbar">
        <div class="topbar-title">Chats</div>
        <div style="display:flex; gap:10px; align-items:center;">
            <div class="topbar-search">🔍&nbsp; Search for chats...</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Welcome to Nusantara Guide ✨</div>
        <div class="hero-sub">Search or ask AI for anything you want to know about Indonesia</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check API key
    if not api_key:
        st.warning("⚠️ API Key tidak ditemukan di file `.env`. Masukkan API Key Anda di bawah:")
        api_key = st.text_input("Gemini API Key", type="password")
        if not api_key:
            st.stop()
    
    model = get_model(api_key)
    
    # Messages Label
    msg_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f'<div class="chat-section-title">Chats ({msg_count})</div>', unsafe_allow_html=True)
    
    # Display Messages as Cards
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        avatar = "👤" if is_user else "✨"
        name = "You" if is_user else "Bima AI"
        avatar_cls = "user" if is_user else ""
        st.markdown(f"""
        <div class="msg-card">
            <div class="msg-avatar {avatar_cls}">{avatar}</div>
            <div class="msg-body">
                <div class="msg-header">
                    <span class="msg-name">{name}</span>
                </div>
                <div class="msg-text">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Chat Input
    st.markdown('<div class="input-area">', unsafe_allow_html=True)
    if prompt := st.chat_input("Tanya AI tentang wisata atau kuliner..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Generate response
        gemini_history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [m["content"]]})
        
        try:
            chat = model.start_chat(history=gemini_history)
            response = chat.send_message(prompt)
            full_response = response.text
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.session_state.messages.append({
                "role": "assistant",
                "content": f"❌ Terjadi kesalahan: {e}"
            })
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
