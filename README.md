# Nusantara Guide AI 🏝️

Nusantara Guide AI adalah chatbot interaktif yang berfungsi sebagai **Asisten Perjalanan & Kuliner Indonesia**. Dibangun menggunakan **Streamlit** dan **Google Gemini AI**, chatbot ini siap membantu Anda merencanakan liburan, menemukan hidden gems, dan merekomendasikan kuliner otentik di seluruh pelosok negeri.

## Fitur & Parameter Kreatif
- **Use Case:** Asisten Wisata & Kuliner Nusantara (Travel & Culinary Assistant).
- **Model AI:** Google Gemini (1.5 Flash).
- **Gaya Bahasa:** "Bima", seorang guide lokal yang memiliki bahasa ramah, santai, dan asyik seperti teman sendiri.
- **Konfigurasi Suhu (Temperature):** `0.75` (Memberikan tingkat kreativitas yang seimbang antara fakta dan gaya penceritaan yang menarik).
- **Memory:** Menggunakan `st.session_state` Streamlit untuk menyimpan konteks percakapan secara terus-menerus selama sesi aktif, sehingga bot mengingat pertanyaan sebelumnya.
- **System Instruction:** Diinstruksikan secara khusus dengan parameter LLM system prompt untuk menjadi guide wisata yang berpengetahuan luas tentang Indonesia.

## Cara Instalasi & Menjalankan Aplikasi

1. Clone repositori ini:
   ```bash
   git clone <URL_REPOSITORI_ANDA>
   cd chatbot
   ```

2. Buat Virtual Environment (opsional namun disarankan):
   ```bash
   python -m venv venv
   # Di Windows:
   venv\Scripts\activate
   # Di Mac/Linux:
   source venv/bin/activate
   ```

3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```

4. Konfigurasi API Key:
   - Buat file `.env` (atau rename `.env.example` menjadi `.env`).
   - Masukkan Google Gemini API Key Anda:
     ```
     GEMINI_API_KEY=api_key_anda_disini
     ```
   *(Alternatif: Anda bisa langsung memasukkan API Key di sidebar ketika aplikasi berjalan)*

5. Jalankan aplikasi Streamlit:
   ```bash
   streamlit run app.py
   ```

## Cuplikan Layar (Screenshot)
*(Screenshot disertakan di folder dokumentasi atau lihat langsung di web app)*

---
*Dibuat untuk memenuhi proyek pembuatan Chatbot berbasis AI.*
