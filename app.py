import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup UI Configuration (Wide layout to mimic dashboard)
st.set_page_config(
    page_title="Nusantara Guide AI",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to mimic the modern purple dashboard UI
st.markdown("""
<style>
    /* Sembunyikan elemen bawaan */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Background utama aplikasi putih bersih */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #EAEAEA;
    }
    
    /* Tombol-tombol di sidebar */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #8B5CF6;
        color: white;
        border: none;
        padding: 10px;
        font-weight: 600;
    }
    .stButton>button:hover {
        background-color: #7C3AED;
        color: white;
    }
    
    /* Gradient Banner ala gambar referensi */
    .hero-banner {
        background: linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%);
        padding: 40px 20px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    .hero-banner h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .hero-banner p {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* Styling Chat Container */
    .stChatMessage {
        background-color: #FFFFFF;
        border: 1px solid #F3F4F6;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Menu (Mencoba meniru struktur sidebar referensi)
with st.sidebar:
    # Profil Tiru-tiruan
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #8B5CF6; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold;">US</div>
            <div>
                <div style="font-weight: bold; font-size: 1.1rem;">User Explorer</div>
                <div style="font-size: 0.8rem; color: #666;">Free Plan</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Cek API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("🔑 Masukkan Gemini API Key", type="password")
    
    st.markdown("---")
    
    st.markdown("📂 **Menu**")
    st.markdown("💬 Chats")
    st.markdown("📚 Library")
    st.markdown("🧩 Apps")
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("＋ New Chat"):
        st.session_state.messages = []
        st.rerun()

# Stop jika tidak ada API key
if not api_key:
    st.warning("⚠️ Masukkan API Key di sidebar sebelah kiri untuk mulai mengobrol.")
    st.stop()

# Banner Utama (Meniru Gradient Ungu/Biru)
st.markdown("""
    <div class="hero-banner">
        <h1>Welcome to Nusantara Guide ✨</h1>
        <p>Search or ask AI for anything you want to know about Indonesia</p>
    </div>
""", unsafe_allow_html=True)

# Konfigurasi API & Model
genai.configure(api_key=api_key)

system_instruction = (
    "Kamu adalah AI Asisten pintar bernama Bima. "
    "Tugas utamamu adalah memandu perjalanan wisata dan memberikan rekomendasi kuliner Indonesia. "
    "Jawablah dengan gaya yang modern, profesional namun tetap ramah."
)

generation_config = {
    "temperature": 0.7,
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 1024,
}

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-flash-latest",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

model = get_model()

# Inisialisasi Chat History
if "messages" not in st.session_state or len(st.session_state.messages) == 0:
    st.session_state.messages = []
    st.session_state.messages.append({
        "role": "assistant", 
        "content": "Halo! Saya siap membantu Anda merencanakan perjalanan atau mencari referensi kuliner di Indonesia. Ada yang ingin ditanyakan hari ini?"
    })

# Kontainer Chat di Tengah (Mirip desain feed)
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        # Avatar custom: Streva logo tiruan untuk asisten
        avatar = "👤" if message["role"] == "user" else "✨"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# Input Pengguna
if prompt := st.chat_input("Tanya AI tentang wisata atau kuliner..."):
    # Tampilkan input user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with chat_container:
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)

        # Proses respons AI
        with st.chat_message("assistant", avatar="✨"):
            message_placeholder = st.empty()
            
            gemini_history = []
            for msg in st.session_state.messages[:-1]:
                role = "model" if msg["role"] == "assistant" else "user"
                gemini_history.append({"role": role, "parts": [msg["content"]]})
            
            try:
                chat = model.start_chat(history=gemini_history)
                response = chat.send_message(prompt, stream=True)
                
                full_response = ""
                for chunk in response:
                    full_response += chunk.text
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
