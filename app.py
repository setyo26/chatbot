import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup UI Configuration
st.set_page_config(
    page_title="Nusantara Guide AI",
    page_icon="🏝️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful UI
st.markdown("""
<style>
    /* Sembunyikan menu bawaan Streamlit agar lebih bersih */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Desain Header Utama */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        color: #2E7D32; /* Hijau Tropis */
        text-align: center;
        margin-bottom: 0px;
        padding-top: 20px;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #555;
        text-align: center;
        margin-bottom: 2rem;
        font-style: italic;
    }
</style>
""", unsafe_allow_html=True)

# Main Header
st.markdown('<p class="main-header">🏝️ Nusantara Guide AI</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Teman Pintar Jelajah Wisata & Kuliner Indonesia 🇮🇩</p>', unsafe_allow_html=True)
st.divider()

# Sidebar Beautification
with st.sidebar:
    # Menambahkan gambar ilustrasi wisata di sidebar
    st.image(
        "https://images.unsplash.com/photo-1537996194471-e657df975ab4?q=80&w=600&auto=format&fit=crop", 
        caption="Pesona Bali, Indonesia"
    )
    
    st.markdown("### ⚙️ Pengaturan")
    
    # Cek API Key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.text_input("🔑 Masukkan Gemini API Key", type="password")
        
    st.markdown("---")
    st.markdown("### 💡 Tentang Bima")
    st.info(
        "**Bima** adalah asisten AI yang dirancang khusus untuk memandu perjalanan wisata Anda "
        "dan memberikan rekomendasi kuliner otentik terbaik di seluruh pelosok Nusantara."
    )
    st.caption("Ditenagai oleh Google Gemini ⚡")

# Stop jika tidak ada API key
if not api_key:
    st.warning("⚠️ Masukkan API Key di sidebar sebelah kiri untuk mulai mengobrol.")
    st.stop()

# Konfigurasi API
genai.configure(api_key=api_key)

# Konfigurasi Parameter AI
system_instruction = (
    "Kamu adalah 'Bima', seorang asisten virtual spesialis pariwisata dan kuliner Indonesia. "
    "Gaya bahasamu santai, asyik, dan ramah seperti teman sendiri (gunakan kata ganti 'aku' dan 'kamu'). "
    "Kamu sangat berpengetahuan tentang destinasi wisata tersembunyi (hidden gems), "
    "sejarah lokal, dan rekomendasi kuliner otentik di berbagai daerah di Indonesia. "
    "Selalu berikan tips praktis atau rekomendasi tambahan di akhir jawabanmu."
)

generation_config = {
    "temperature": 0.75,
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
if "messages" not in st.session_state:
    st.session_state.messages = []
    
    # Pesan pertama dari Bima
    greeting = (
        "Halo! Aku **Bima**, teman jalan-jalanmu di Indonesia. 🎒\n\n"
        "Mau cari rekomendasi liburan kemana hari ini, atau lagi *ngidam* makanan khas daerah apa nih?"
    )
    st.session_state.messages.append({"role": "assistant", "content": greeting})

# Menampilkan riwayat chat
for message in st.session_state.messages:
    # Menggunakan Avatar kustom: User = 👤, Bima = 🌴
    avatar = "👤" if message["role"] == "user" else "🌴"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Input Pengguna
if prompt := st.chat_input("Tanya Bima soal wisata atau kuliner..."):
    # Tampilkan input user
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Proses respons AI
    with st.chat_message("assistant", avatar="🌴"):
        message_placeholder = st.empty()
        
        # Siapkan history untuk Gemini
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
                # Efek mengetik (streaming)
                message_placeholder.markdown(full_response + "▌")
            
            # Tampilkan respons akhir penuh
            message_placeholder.markdown(full_response)
            
            # Simpan ke memori
            st.session_state.messages.append({"role": "assistant", "content": full_response})
        except Exception as e:
            st.error(f"Terjadi kesalahan saat menghubungi Bima: {e}")
