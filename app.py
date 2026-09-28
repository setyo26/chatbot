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

st.markdown("""
<style>
/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display: none !important; }

.block-container { padding: 0 !important; max-width: 100% !important; }
.stApp { background: #F0F2F5 !important; overflow: hidden; }

[data-testid="stHorizontalBlock"] {
    height: 100vh !important;
    align-items: stretch !important;
    gap: 0 !important;
}

/* LEFT col — sticky, scrollable internally */
[data-testid="stHorizontalBlock"] > div:first-child {
    height: 100vh !important;
    overflow-y: auto !important;
    background: #FFFFFF !important;
    border-right: 1px solid #EAEAEA !important;
    padding: 20px 12px !important;
    position: sticky !important;
    top: 0 !important;
    flex-shrink: 0 !important;
}

/* RIGHT col — independent scroll */
[data-testid="stHorizontalBlock"] > div:last-child {
    height: 100vh !important;
    overflow-y: auto !important;
    padding: 28px 36px 120px !important;
}

/* ── RADIO as nav menu ── */
/* Hide the actual radio circle */
div[data-testid="stRadio"] > label { display: none !important; }
div[data-testid="stRadio"] > div {
    display: flex !important;
    flex-direction: column !important;
    gap: 2px !important;
}
div[data-testid="stRadio"] > div > label {
    display: flex !important;
    align-items: center !important;
    padding: 9px 12px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    color: #444 !important;
    transition: background .15s, color .15s !important;
    gap: 8px !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: #F0EBFF !important;
    color: #7C3AED !important;
}
/* Hide radio circle dot */
div[data-testid="stRadio"] > div > label > div:first-child {
    display: none !important;
}
/* Selected radio item */
div[data-testid="stRadio"] > div > label[data-baseweb="radio"]:has(input:checked),
div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: #EDE9FE !important;
    color: #7C3AED !important;
    font-weight: 700 !important;
}

/* ── Pinned/History buttons ── */
.nav-label {
    font-size: .7rem; color: #9CA3AF; font-weight: 700;
    text-transform: uppercase; letter-spacing: .07em;
    padding: 10px 0 4px 4px; display: block;
}
.nav-btn {
    display: flex; align-items: center; gap: 8px;
    padding: 8px 12px; border-radius: 8px;
    font-size: .84rem; color: #555;
    cursor: pointer; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
    transition: background .15s;
    text-decoration: none;
}
.nav-btn:hover { background: #F0EBFF; color: #7C3AED; }

/* ── New Chat button ── */
.new-chat-wrap .stButton > button {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 12px !important;
    font-size: .9rem !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(139,92,246,.3) !important;
    width: 100% !important;
}
.new-chat-wrap .stButton > button:hover { opacity: .88 !important; }
.new-chat-wrap .stButton > button p { margin: 0 !important; }

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    border-radius: 18px; padding: 38px 30px; text-align: center;
    color: white; margin-bottom: 24px;
    box-shadow: 0 8px 28px rgba(139,92,246,.28);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content:''; position:absolute; top:-50px; right:-50px;
    width:180px; height:180px; border-radius:50%;
    background:rgba(255,255,255,.09);
}
.hero-title { font-size: 2rem; font-weight: 800; margin: 0 0 8px; }
.hero-sub   { font-size: 1rem; opacity: .85; margin: 0; }

/* ── TOP BAR ── */
.topbar {
    display: flex; justify-content: space-between; align-items: center;
    margin-bottom: 20px;
}
.topbar-title { font-size: 1.5rem; font-weight: 800; color: #1A1A2E; }
.topbar-search {
    background: white; border: 1px solid #E5E7EB; border-radius: 10px;
    padding: 9px 18px; font-size: .85rem; color: #9CA3AF; width: 240px;
}

/* ── MSG CARDS ── */
.chat-count { font-size: .95rem; font-weight: 700; color: #1A1A2E; margin-bottom: 14px; }
.msg-card {
    background: white; border-radius: 14px;
    padding: 16px 20px; margin-bottom: 12px;
    box-shadow: 0 1px 6px rgba(0,0,0,.07);
    border: 1px solid #F0F0F0;
    display: flex; gap: 14px; align-items: flex-start;
    animation: fadeUp .25s ease;
}
@keyframes fadeUp {
    from { opacity:0; transform:translateY(6px); }
    to   { opacity:1; transform:translateY(0); }
}
.msg-avatar {
    width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center; font-size: 15px;
}
.msg-ai   { background: #EDE9FE; }
.msg-user { background: #DBEAFE; }
.msg-body  { flex: 1; min-width: 0; }
.msg-name  { font-weight: 700; font-size: .84rem; color: #1A1A2E; margin-bottom: 5px; }
.msg-text  { font-size: .87rem; color: #4B5563; line-height: 1.65; white-space: pre-wrap; }

/* ── CHAT INPUT ── */
[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    font-size: .9rem !important;
    background: white !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ── STATE ─────────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Halo! Saya Bima, asisten wisata dan kuliner Indonesia Anda.\nAda rencana liburan kemana, atau lagi cari rekomendasi makanan khas daerah? 🏝️"
    }]
if "pinned_click" not in st.session_state:
    st.session_state.pinned_click = None

# ── API & MODEL ───────────────────────────────────────────────────────────────
api_key = os.getenv("GEMINI_API_KEY")
system_instruction = (
    "Kamu adalah AI Asisten pintar bernama Bima. "
    "Tugas utamamu adalah memandu perjalanan wisata dan memberikan rekomendasi kuliner Indonesia. "
    "Jawablah dengan gaya yang modern, profesional namun tetap ramah dan bersahabat."
)
generation_config = {"temperature": 0.75, "top_p": 0.9, "top_k": 50, "max_output_tokens": 1024}

@st.cache_resource
def get_model(key):
    genai.configure(api_key=key)
    return genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

# ── LAYOUT ───────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 3.8])

# ══════════════ LEFT SIDEBAR ══════════════
with col_left:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
        <div style="background:linear-gradient(135deg,#8B5CF6,#3B82F6);color:white;
            font-weight:900;font-size:18px;width:38px;height:38px;border-radius:10px;
            display:flex;align-items:center;justify-content:center;">N</div>
        <div style="font-size:1.1rem;font-weight:800;color:#1A1A2E;">Nusantara AI</div>
    </div>
    <div style="background:#F4F5F7;border:1px solid #E5E7EB;border-radius:8px;
        padding:9px 14px;margin-bottom:16px;font-size:.84rem;color:#9CA3AF;">
        🔍&nbsp; Search for chats...
    </div>
    """, unsafe_allow_html=True)

    # Navigation via radio (reliable left-align)
    menu = st.radio(
        "menu",
        ["💬  Chats", "📚  Library", "🧩  Apps"],
        label_visibility="collapsed"
    )
    active_menu = menu.split("  ")[1]

    # Pinned
    st.markdown('<span class="nav-label">Pinned</span>', unsafe_allow_html=True)
    pinned_items = [
        ("🗺️", "Wisata Lombok terbaik"),
        ("🍜", "Kuliner terbaik Jogja"),
        ("🏖️", "Itinerary 5 hari Bali"),
    ]
    for icon, text in pinned_items:
        if st.button(f"{icon}  {text}...", key=f"p_{text}", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": f"Halo! Kamu ingin tahu soal **{text}**? Yuk ceritakan lebih lanjut! 😊"}]
            st.rerun()

    # History
    st.markdown('<span class="nav-label">Chat History</span>', unsafe_allow_html=True)
    history_items = [
        ("💬", "Hidden gems Raja Ampat"),
        ("💬", "Makanan khas Padang"),
        ("💬", "Camping di Dieng"),
    ]
    for icon, text in history_items:
        if st.button(f"{icon}  {text}...", key=f"h_{text}", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": f"Halo! Melanjutkan topik **{text}** ya? 😊"}]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # New Chat
    st.markdown('<div class="new-chat-wrap">', unsafe_allow_html=True)
    if st.button("＋  Start New Chat", key="new_chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya Bima, asisten wisata dan kuliner Indonesia Anda.\nAda rencana liburan kemana, atau lagi cari rekomendasi makanan khas daerah? 🏝️"}]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════ RIGHT PANEL ══════════════
with col_right:
    st.markdown(f"""
    <div class="topbar">
        <div class="topbar-title">{active_menu}</div>
        <div class="topbar-search">🔍&nbsp; Search for chats...</div>
    </div>
    <div class="hero-banner">
        <div class="hero-title">Welcome to Nusantara Guide ✨</div>
        <div class="hero-sub">Search or ask AI for anything you want to know about Indonesia</div>
    </div>
    """, unsafe_allow_html=True)

    if active_menu == "Chats":
        if not api_key:
            st.warning("⚠️ API Key tidak ditemukan.")
            api_key = st.text_input("Gemini API Key", type="password")
            if not api_key:
                st.stop()

        model = get_model(api_key)

        user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
        st.markdown(f'<div class="chat-count">Chats ({user_count})</div>', unsafe_allow_html=True)

        for msg in st.session_state.messages:
            is_user = msg["role"] == "user"
            avatar = "👤" if is_user else "✨"
            name   = "You" if is_user else "Bima AI"
            cls    = "msg-user" if is_user else "msg-ai"
            content = msg["content"].replace("<", "&lt;").replace(">", "&gt;")
            st.markdown(f"""
            <div class="msg-card">
                <div class="msg-avatar {cls}">{avatar}</div>
                <div class="msg-body">
                    <div class="msg-name">{name}</div>
                    <div class="msg-text">{content}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

        if prompt := st.chat_input("Tanya AI tentang wisata atau kuliner..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            history = [
                {"role": "model" if m["role"] == "assistant" else "user", "parts": [m["content"]]}
                for m in st.session_state.messages[:-1]
            ]
            try:
                chat = model.start_chat(history=history)
                with st.spinner("Bima sedang mengetik..."):
                    resp = chat.send_message(prompt)
                st.session_state.messages.append({"role": "assistant", "content": resp.text})
            except Exception as e:
                st.session_state.messages.append({"role": "assistant", "content": f"❌ Kesalahan: {e}"})
            st.rerun()

    elif active_menu == "Library":
        st.markdown("""
        <div class="msg-card" style="flex-direction:column;align-items:center;padding:50px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:14px;">📚</div>
            <div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;margin-bottom:8px;">Library</div>
            <div style="font-size:.9rem;color:#6B7280;">Tempat menyimpan artikel & rekomendasi wisata favorit.<br>Fitur segera hadir!</div>
        </div>""", unsafe_allow_html=True)

    elif active_menu == "Apps":
        st.markdown("""
        <div class="msg-card" style="flex-direction:column;align-items:center;padding:50px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:14px;">🧩</div>
            <div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;margin-bottom:8px;">Apps</div>
            <div style="font-size:.9rem;color:#6B7280;">Integrasi dengan peta, booking hotel, dan lainnya.<br>Fitur segera hadir!</div>
        </div>""", unsafe_allow_html=True)
