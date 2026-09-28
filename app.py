import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Nusantara Guide AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide default Streamlit chrome */
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="collapsedControl"] { visibility: hidden !important; display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #F4F5F7 !important; }

/* ── LEFT PANEL ── */
.sidebar-wrapper {
    background: #FFFFFF;
    height: 100vh;
    padding: 20px 14px 14px;
    border-right: 1px solid #EBEBEB;
    display: flex;
    flex-direction: column;
    position: sticky;
    top: 0;
    overflow-y: auto;
}
.brand-logo {
    display: flex; align-items: center; gap: 10px;
    margin-bottom: 18px;
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
    padding: 9px 14px; margin-bottom: 14px;
    font-size: 0.85rem; color: #999;
    border: 1px solid #E5E7EB;
}
.nav-label {
    font-size: 0.72rem; color: #AAA; font-weight: 700;
    text-transform: uppercase; letter-spacing: .06em;
    margin: 10px 0 4px 4px;
}
.pinned-item {
    padding: 7px 10px; font-size: 0.82rem; color: #555;
    border-radius: 6px; cursor: pointer;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.pinned-item:hover { background: #F9FAFB; }

/* ── NAV BUTTONS (override Streamlit button) ── */
div[data-testid="stVerticalBlock"] .stButton > button {
    background: transparent !important;
    color: #444 !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 8px 12px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background .15s;
}
div[data-testid="stVerticalBlock"] .stButton > button:hover {
    background: #F0EBFF !important;
    color: #7C3AED !important;
}

/* Active nav button */
.nav-active > div > button {
    background: #F0EBFF !important;
    color: #7C3AED !important;
    font-weight: 700 !important;
}

/* New Chat / Start Chat buttons */
.btn-primary > div > button {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-size: 0.9rem !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(139,92,246,0.35) !important;
}
.btn-primary > div > button:hover {
    opacity: 0.9 !important;
}

/* ── RIGHT / MAIN PANEL ── */
.main-wrapper { padding: 28px 36px; }
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 22px;
}
.topbar-title { font-size: 1.5rem; font-weight: 800; color: #1A1A2E; }
.topbar-search {
    background: white; border-radius: 8px; border: 1px solid #E5E7EB;
    padding: 9px 16px; font-size: 0.85rem; color: #888; width: 240px;
}

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    border-radius: 18px; padding: 38px 24px; text-align: center;
    color: white; margin-bottom: 24px;
    box-shadow: 0 8px 24px rgba(139,92,246,0.28);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content: ''; position: absolute; top: -50px; right: -50px;
    width: 180px; height: 180px; border-radius: 50%;
    background: rgba(255,255,255,0.08);
}
.hero-banner::after {
    content: ''; position: absolute; bottom: -70px; left: -30px;
    width: 220px; height: 220px; border-radius: 50%;
    background: rgba(255,255,255,0.06);
}
.hero-title { font-size: 1.9rem; font-weight: 800; margin: 0 0 8px; }
.hero-sub { font-size: 1rem; opacity: .85; margin: 0; }

/* ── MESSAGE CARDS ── */
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
.msg-name { font-weight: 700; font-size: 0.85rem; color: #1A1A2E; margin-bottom: 4px; }
.msg-text { font-size: 0.88rem; color: #555; line-height: 1.6; }

/* ── CHAT INPUT ── */
.stChatInputContainer {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.07) !important;
    background: white !important;
}
.stChatInputContainer:focus-within {
    border-color: #8B5CF6 !important;
    box-shadow: 0 4px 16px rgba(139,92,246,0.2) !important;
}
</style>
""", unsafe_allow_html=True)

# ── STATE INIT ───────────────────────────────────────────────────────────────
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Chats"
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Halo! Saya **Bima**, asisten wisata dan kuliner Indonesia Anda. Ada yang ingin ditanyakan hari ini? 🏝️"
    }]

# ── API & MODEL ──────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")

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

# ── 2-COLUMN LAYOUT ──────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 3.5])

# ─────────────────────────── LEFT SIDEBAR ────────────────────────────────────
with col_left:
    # Brand
    st.markdown("""
    <div class="brand-logo">
        <div class="brand-icon">N</div>
        <div class="brand-name">Nusantara AI</div>
    </div>
    <div class="search-box">🔍&nbsp; Search for chats...</div>
    """, unsafe_allow_html=True)

    # --- Navigation Menu (Real Streamlit Buttons) ---
    menu_items = [
        ("💬", "Chats", "3"),
        ("📚", "Library", "2"),
        ("🧩", "Apps", "5"),
    ]
    for icon, label, badge in menu_items:
        is_active = st.session_state.active_menu == label
        # Wrap with active class if needed
        if is_active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}  •{badge}", key=f"menu_{label}", use_container_width=True):
            st.session_state.active_menu = label
            st.rerun()
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

    # --- Pinned ---
    st.markdown('<div class="nav-label">Pinned</div>', unsafe_allow_html=True)
    pinned = [
        ("🗺️", "Wisata Lombok terbaik..."),
        ("🍜", "Kuliner terbaik di Jogja..."),
        ("🏖️", "Itinerary 5 hari Bali..."),
    ]
    for icon, text in pinned:
        if st.button(f"{icon}  {text}", key=f"pin_{text}", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Halo! Kamu ingin tahu lebih lanjut soal **{text.replace('...', '')}**? Yuk ceritakan lebih detail apa yang kamu cari! 😊"
            }]
            st.session_state.active_menu = "Chats"
            st.rerun()

    # --- History ---
    st.markdown('<div class="nav-label">Chat History</div>', unsafe_allow_html=True)
    history_items = [
        ("💬", "Hidden gems Raja Ampat..."),
        ("💬", "Makanan khas Padang..."),
        ("💬", "Camping di Dieng..."),
    ]
    for icon, text in history_items:
        if st.button(f"{icon}  {text}", key=f"hist_{text}", use_container_width=True):
            st.session_state.messages = [{
                "role": "assistant",
                "content": f"Halo! Melanjutkan percakapan soal **{text.replace('...', '')}**. Ada yang ingin kamu tanyakan? 😊"
            }]
            st.session_state.active_menu = "Chats"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # New Chat Button
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button("＋  Start New Chat", key="new_chat", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Halo! Saya **Bima**, asisten wisata dan kuliner Indonesia Anda. Ada yang ingin ditanyakan hari ini? 🏝️"
        }]
        st.session_state.active_menu = "Chats"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────── RIGHT PANEL ─────────────────────────────────────
with col_right:
    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # Top Bar
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">{st.session_state.active_menu}</div>
        <div class="topbar-search">🔍&nbsp; Search for chats...</div>
    </div>
    """, unsafe_allow_html=True)

    # Hero Banner
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Welcome to Nusantara Guide ✨</div>
        <div class="hero-sub">Search or ask AI for anything you want to know about Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Tampilan per menu ──
    if st.session_state.active_menu == "Chats":
        # Check API key
        if not api_key:
            st.warning("⚠️ API Key tidak ditemukan. Masukkan API Key Anda:")
            api_key = st.text_input("Gemini API Key", type="password", key="api_input")
            if not api_key:
                st.stop()

        model = get_model(api_key)

        # Message count label
        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f'<div class="chat-section-title">Chats ({user_count})</div>', unsafe_allow_html=True)

        # Render message cards
        for msg in st.session_state.messages:
            is_user = msg["role"] == "user"
            avatar = "👤" if is_user else "✨"
            name = "You" if is_user else "Bima AI"
            avatar_cls = "user" if is_user else ""
            # Render markdown-like bold in HTML
            content = msg["content"].replace("**", "<b>", 1)
            content = content.replace("**", "</b>", 1)
            st.markdown(f"""
            <div class="msg-card">
                <div class="msg-avatar {avatar_cls}">{avatar}</div>
                <div class="msg-body">
                    <div class="msg-name">{name}</div>
                    <div class="msg-text">{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Chat Input
        if prompt := st.chat_input("Tanya AI tentang wisata atau kuliner..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            gemini_history = []
            for m in st.session_state.messages[:-1]:
                role = "model" if m["role"] == "assistant" else "user"
                gemini_history.append({"role": role, "parts": [m["content"]]})
            try:
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Kesalahan: {e}"})
            st.rerun()

    elif st.session_state.active_menu == "Library":
        st.info("📚 **Library** — Tempat menyimpan rekomendasi dan artikel wisata favorit Anda. (Fitur segera hadir!)")

    elif st.session_state.active_menu == "Apps":
        st.info("🧩 **Apps** — Integrasi dengan aplikasi peta, booking, dan lainnya. (Fitur segera hadir!)")

    st.markdown('</div>', unsafe_allow_html=True)
