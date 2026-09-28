import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="Nusantara Guide AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* ── Reset default Streamlit UI ── */
#MainMenu, footer, header,
[data-testid="stToolbar"]          { display: none !important; }
[data-testid="collapsedControl"]   { display: none !important; }

/* ── Page background ── */
.stApp { background: #F0F2F5 !important; }
.block-container { padding: 2rem 2rem 4rem !important; max-width: 100% !important; }

/* ── SIDEBAR CONTAINER ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #EAEAEA !important;
    min-width: 240px !important;
    max-width: 260px !important;
    padding: 0 !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 20px 14px !important;
    display: flex;
    flex-direction: column;
    height: 100vh;
}

/* ── ALL BUTTONS IN SIDEBAR → nav style ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #444 !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    font-weight: 500 !important;
    font-size: 0.87rem !important;
    padding: 8px 12px !important;
    width: 100% !important;
    box-shadow: none !important;
    transition: background .15s, color .15s;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #F0EBFF !important;
    color: #7C3AED !important;
}

/* ── Primary (New Chat) button ── */
[data-testid="stSidebar"] .btn-primary .stButton > button {
    background: linear-gradient(135deg, #8B5CF6, #3B82F6) !important;
    color: white !important;
    font-weight: 700 !important;
    border-radius: 10px !important;
    padding: 12px 16px !important;
    font-size: 0.9rem !important;
    box-shadow: 0 4px 14px rgba(139,92,246,0.35) !important;
    justify-content: center !important;
}
[data-testid="stSidebar"] .btn-primary .stButton > button:hover {
    opacity: 0.88 !important;
    color: white !important;
}

/* ── Active nav item ── */
[data-testid="stSidebar"] .nav-active .stButton > button {
    background: #EDE9FE !important;
    color: #7C3AED !important;
    font-weight: 700 !important;
}

/* ── Nav section label ── */
.nav-label {
    font-size: 0.7rem; color: #9CA3AF;
    font-weight: 700; text-transform: uppercase;
    letter-spacing: .07em; margin: 12px 0 4px 12px;
}

/* ── HERO BANNER ── */
.hero-banner {
    background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
    border-radius: 18px; padding: 38px 30px;
    text-align: center; color: white;
    margin-bottom: 26px;
    box-shadow: 0 8px 28px rgba(139,92,246,0.30);
    position: relative; overflow: hidden;
}
.hero-banner::before {
    content:''; position:absolute; top:-50px; right:-50px;
    width:180px; height:180px; border-radius:50%;
    background:rgba(255,255,255,.09);
}
.hero-banner::after {
    content:''; position:absolute; bottom:-70px; left:-30px;
    width:220px; height:220px; border-radius:50%;
    background:rgba(255,255,255,.06);
}
.hero-title { font-size:2rem; font-weight:800; margin:0 0 8px; }
.hero-sub   { font-size:1rem; opacity:.85; margin:0; }

/* ── TOP BAR ── */
.topbar {
    display:flex; justify-content:space-between; align-items:center;
    margin-bottom: 20px;
}
.topbar-title { font-size:1.5rem; font-weight:800; color:#1A1A2E; }
.topbar-search {
    background:white; border:1px solid #E5E7EB; border-radius:10px;
    padding: 9px 18px; font-size:.85rem; color:#9CA3AF; width:240px;
}

/* ── CHAT MSG CARDS ── */
.chat-count {
    font-size:.95rem; font-weight:700; color:#1A1A2E; margin-bottom:14px;
}
.msg-card {
    background:white; border-radius:14px;
    padding:16px 20px; margin-bottom:12px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.07);
    border: 1px solid #F0F0F0;
    display:flex; gap:14px; align-items:flex-start;
    animation: fadeIn .25s ease;
}
@keyframes fadeIn { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
.msg-avatar {
    width:36px; height:36px; border-radius:50%; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    font-size:15px;
}
.msg-ai   { background:#EDE9FE; }
.msg-user { background:#DBEAFE; }
.msg-body { flex:1; min-width:0; }
.msg-name { font-weight:700; font-size:.84rem; color:#1A1A2E; margin-bottom:5px; }
.msg-text { font-size:.87rem; color:#4B5563; line-height:1.65; white-space:pre-wrap; }

/* ── CHAT INPUT OVERRIDE ── */
[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 2px solid #E5E7EB !important;
    font-size: .9rem !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #8B5CF6 !important;
    box-shadow: 0 0 0 3px rgba(139,92,246,.15) !important;
}
</style>
""", unsafe_allow_html=True)

# ── STATE ────────────────────────────────────────────────────────────────────
if "active_menu" not in st.session_state:
    st.session_state.active_menu = "Chats"
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Halo! Saya Bima, asisten wisata dan kuliner Indonesia Anda.\nAda rencana liburan kemana, atau lagi cari rekomendasi makanan khas daerah? 🏝️"
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

# ── SIDEBAR (native Streamlit → always fixed on left) ────────────────────────
with st.sidebar:
    # Brand
    st.markdown("""
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:18px;">
        <div style="background:linear-gradient(135deg,#8B5CF6,#3B82F6);color:white;
                    font-weight:900;font-size:18px;width:38px;height:38px;
                    border-radius:10px;display:flex;align-items:center;justify-content:center;">N</div>
        <div style="font-size:1.15rem;font-weight:800;color:#1A1A2E;">Nusantara AI</div>
    </div>
    <div style="background:#F4F5F7;border:1px solid #E5E7EB;border-radius:8px;
                padding:9px 14px;margin-bottom:16px;font-size:.84rem;color:#9CA3AF;">
        🔍&nbsp; Search for chats...
    </div>
    """, unsafe_allow_html=True)

    # Navigation
    nav_items = [("💬", "Chats"), ("📚", "Library"), ("🧩", "Apps")]
    for icon, label in nav_items:
        active = st.session_state.active_menu == label
        if active:
            st.markdown('<div class="nav-active">', unsafe_allow_html=True)
        if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.active_menu = label
            st.rerun()
        if active:
            st.markdown('</div>', unsafe_allow_html=True)

    # Pinned
    st.markdown('<div class="nav-label">Pinned</div>', unsafe_allow_html=True)
    pinned = [("🗺️", "Wisata Lombok terbaik"), ("🍜", "Kuliner terbaik di Jogja"), ("🏖️", "Itinerary 5 hari Bali")]
    for icon, text in pinned:
        if st.button(f"{icon}  {text}...", key=f"pin_{text}", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": f"Halo! Kamu ingin tahu soal **{text}**? Yuk, ceritakan lebih lanjut! 😊"}]
            st.session_state.active_menu = "Chats"
            st.rerun()

    # History
    st.markdown('<div class="nav-label">Chat History</div>', unsafe_allow_html=True)
    history = [("💬", "Hidden gems Raja Ampat"), ("💬", "Makanan khas Padang"), ("💬", "Camping di Dieng")]
    for icon, text in history:
        if st.button(f"{icon}  {text}...", key=f"hist_{text}", use_container_width=True):
            st.session_state.messages = [{"role": "assistant", "content": f"Halo! Melanjutkan topik **{text}** ya? Ada yang ingin kamu tanyakan? 😊"}]
            st.session_state.active_menu = "Chats"
            st.rerun()

    # Spacer + New Chat
    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
    if st.button("＋  Start New Chat", key="new_chat", use_container_width=True):
        st.session_state.messages = [{"role": "assistant", "content": "Halo! Saya Bima, asisten wisata dan kuliner Indonesia Anda.\nAda rencana liburan kemana, atau lagi cari rekomendasi makanan khas daerah? 🏝️"}]
        st.session_state.active_menu = "Chats"
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── MAIN CONTENT ─────────────────────────────────────────────────────────────
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

# ── Menu Pages ────────────────────────────────────────────────────────────────
if st.session_state.active_menu == "Chats":
    if not api_key:
        st.warning("⚠️ API Key tidak ditemukan. Masukkan API Key Anda:")
        api_key = st.text_input("Gemini API Key", type="password", key="api_input")
        if not api_key:
            st.stop()

    model = get_model(api_key)

    user_count = len([m for m in st.session_state.messages if m["role"] == "user"])
    st.markdown(f'<div class="chat-count">Chats ({user_count})</div>', unsafe_allow_html=True)

    # Render message cards
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        avatar = "👤" if is_user else "✨"
        name = "You" if is_user else "Bima AI"
        cls = "msg-user" if is_user else "msg-ai"
        content = msg["content"]
        st.markdown(f"""
        <div class="msg-card">
            <div class="msg-avatar {cls}">{avatar}</div>
            <div class="msg-body">
                <div class="msg-name">{name}</div>
                <div class="msg-text">{content}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Chat input
    if prompt := st.chat_input("Tanya AI tentang wisata atau kuliner..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        gemini_history = []
        for m in st.session_state.messages[:-1]:
            role = "model" if m["role"] == "assistant" else "user"
            gemini_history.append({"role": role, "parts": [m["content"]]})
        try:
            chat = model.start_chat(history=gemini_history)
            with st.spinner("Bima sedang mengetik..."):
                response = chat.send_message(prompt)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"❌ Kesalahan: {e}"})
        st.rerun()

elif st.session_state.active_menu == "Library":
    st.markdown("""
    <div class="msg-card" style="flex-direction:column;align-items:center;padding:40px;text-align:center;">
        <div style="font-size:3rem;margin-bottom:16px;">📚</div>
        <div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;margin-bottom:8px;">Library</div>
        <div style="font-size:.9rem;color:#6B7280;">Tempat menyimpan rekomendasi & artikel wisata favorit Anda.<br>Fitur segera hadir!</div>
    </div>
    """, unsafe_allow_html=True)

elif st.session_state.active_menu == "Apps":
    st.markdown("""
    <div class="msg-card" style="flex-direction:column;align-items:center;padding:40px;text-align:center;">
        <div style="font-size:3rem;margin-bottom:16px;">🧩</div>
        <div style="font-size:1.1rem;font-weight:700;color:#1A1A2E;margin-bottom:8px;">Apps</div>
        <div style="font-size:.9rem;color:#6B7280;">Integrasi dengan aplikasi peta, booking hotel, dan lainnya.<br>Fitur segera hadir!</div>
    </div>
    """, unsafe_allow_html=True)
