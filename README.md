# 📊 DataPals: Chatbot Teman Belajar Data Science

Chatbot berbasis LLM (Google Gemini) untuk membantu pelajar Indonesia belajar Data Science. Dibuat dengan Streamlit sebagai final project *LLM-Based Tools and Gemini API Integration for Data Scientists*.

## Use Case
Education bot: menjawab pertanyaan seputar Python, pandas, statistik, machine learning, SQL, dan AI dalam bahasa Indonesia. Pertanyaan di luar domain akan ditolak dengan sopan.

## Fitur Kreatif (Parameter)
| Fitur | Keterangan |
|---|---|
| Gaya bahasa | Santai atau Formal |
| Level pengguna | Pemula (analogi, tanpa jargon) atau Menengah (istilah teknis, contoh kode) |
| Kreativitas | Slider *temperature* 0.0 - 1.5 |
| Memory | Bot mengingat konteks percakapan (bisa dimatikan) |
| Rekomendasi | Saran topik lanjutan di akhir jawaban |
| Domain terbatas | System prompt fokus ke Data Science/AI |
| Streaming | Jawaban muncul bertahap + spinner |

## Cara Menjalankan Lokal
```bash
git clone <url-repo-kamu>
cd <nama-repo>
pip install -r requirements.txt
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml   # lalu isi API key
streamlit run app.py
```
API key Gemini bisa dibuat gratis di [Google AI Studio](https://aistudio.google.com/).

## Deploy ke Streamlit Community Cloud
1. Push repo ini ke GitHub.
2. Buka [share.streamlit.io](https://share.streamlit.io/) dan klik **Create app**.
3. Pilih repo, branch, dan file `app.py`.
4. Di **Advanced settings → Secrets**, isi: `GEMINI_API_KEY = "api_key_kamu"`.
5. Klik **Deploy**.

## Teknologi
Python, Streamlit, Google Gemini API (`google-genai`).
