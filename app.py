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
    layout="centered"
)

# Customizing the UI Header
st.title("🏝️ Nusantara Guide AI")
st.caption("Asisten Pintar untuk Penjelajahan Wisata dan Kuliner di Indonesia! 🇮🇩")

# Check for API Key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.warning("⚠️ API Key tidak ditemukan! Silakan masukkan GEMINI_API_KEY di sidebar untuk memulai.")
    api_key_input = st.sidebar.text_input("Gemini API Key", type="password")
    if api_key_input:
        api_key = api_key_input
        genai.configure(api_key=api_key)
else:
    genai.configure(api_key=api_key)

# Configure the AI Model and Parameters
# Parameter Kreatif: Persona Asisten Wisata yang "Santai dan Asyik"
system_instruction = (
    "Kamu adalah 'Bima', seorang asisten virtual spesialis pariwisata dan kuliner Indonesia. "
    "Gaya bahasamu santai, asyik, dan ramah seperti teman sendiri (gunakan kata ganti 'aku' dan 'kamu'). "
    "Kamu sangat berpengetahuan tentang destinasi wisata tersembunyi (hidden gems), "
    "sejarah lokal, dan rekomendasi kuliner otentik di berbagai daerah di Indonesia. "
    "Selalu berikan tips praktis atau rekomendasi tambahan di akhir jawabanmu."
)

generation_config = {
    "temperature": 0.75, # Cukup kreatif namun tetap relevan
    "top_p": 0.9,
    "top_k": 50,
    "max_output_tokens": 1024,
}

@st.cache_resource
def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        system_instruction=system_instruction
    )

if api_key:
    model = get_model()
    
    # Initialize Chat History in Memory
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
        # Initial greeting from bot
        greeting = "Halo! Aku Bima, teman jalan-jalanmu di Indonesia. Mau cari rekomendasi liburan kemana hari ini, atau mau hunting makanan enak apa?"
        st.session_state.messages.append({"role": "assistant", "content": greeting})

    # Display Chat History
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # User Input
    if prompt := st.chat_input("Tanya Bima soal wisata atau kuliner..."):
        # Append user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate AI Response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Format history for Gemini API
            gemini_history = []
            for msg in st.session_state.messages[:-1]: # exclude the latest prompt
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
                
                # Append assistant response to history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            except Exception as e:
                st.error(f"Terjadi kesalahan: {e}")
