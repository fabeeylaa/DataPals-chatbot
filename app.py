import os
import time

import streamlit as st
from google import genai
from google.genai import types

# ---------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------
st.set_page_config(page_title="DataPals", page_icon="📊", layout="centered")

# Model utama + cadangan. Kalau model utama sibuk (503) atau tidak tersedia,
# app otomatis mencoba model berikutnya.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash-lite"]
MODELS = [MODEL] + [m for m in FALLBACK_MODELS if m != MODEL]

# (ikon, teks pertanyaan)
QUICK_PROMPTS = [
    ("🧠", "Jelasin beda supervised dan unsupervised learning"),
    ("🗺️", "Kasih roadmap belajar Data Scientist untuk pemula"),
    ("📉", "Apa itu overfitting dan cara mengatasinya?"),
    ("🐼", "Buat 3 soal latihan pandas beserta jawabannya"),
]

# ---------------------------------------------------------------
# Tampilan (CSS)
# ---------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --primary: #E8478B;
  --primary-soft: #EEEEFF;
  --accent: #14B8A6;
  --ink: #1F2340;
  --muted: #6B7090;
  --line: #E4E6F2;
  --card: #FFFFFF;
}

html, body, [class*="css"], [data-testid="stAppViewContainer"] {
  font-family: 'Plus Jakarta Sans', sans-serif;
}

/* Latar halaman: gradasi lembut */
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(900px 400px at 85% -10%, rgba(91,91,214,0.13), transparent 60%),
    radial-gradient(700px 360px at -10% 0%, rgba(20,184,166,0.10), transparent 55%),
    #F6F7FB;
}
[data-testid="stHeader"] { background: transparent; }
footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 760px; }

/* Sidebar */
[data-testid="stSidebar"] {
  background: #FFFFFF;
  border-right: 1px solid var(--line);
}
[data-testid="stSidebar"] h2 { font-weight: 800; color: var(--ink); }

/* Hero */
.hero { text-align: center; padding: 1.2rem 0 0.4rem; }
.hero-badge {
  display: inline-block; padding: 0.3rem 0.85rem; border-radius: 999px;
  background: var(--primary-soft); color: var(--primary);
  font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em;
}
.hero h1 {
  margin: 0.7rem 0 0.2rem; font-size: 3.1rem; line-height: 1.05; font-weight: 800;
  background: linear-gradient(90deg, #E8478B 0%, #14B8A6 100%);
  -webkit-background-clip: text; background-clip: text; color: transparent;
}
.hero p { color: var(--muted); font-size: 1.02rem; margin: 0.4rem auto 0; max-width: 520px; }

/* Header kecil setelah chat dimulai */
.mini { display: flex; align-items: center; gap: 0.6rem; margin-bottom: 0.2rem; }
.mini .logo {
  width: 38px; height: 38px; border-radius: 12px; display: grid; place-items: center;
  background: linear-gradient(135deg, #E8478B, #14B8A6); font-size: 1.15rem;
}
.mini .name { font-size: 1.5rem; font-weight: 800; color: var(--ink); }

/* Chip status parameter */
.chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.4rem; margin: 0.9rem 0 1.2rem; }
.mini + .chips { justify-content: flex-start; margin-top: 0.6rem; }
.chip {
  padding: 0.25rem 0.7rem; border-radius: 999px; font-size: 0.78rem; font-weight: 600;
  background: var(--card); border: 1px solid var(--line); color: var(--ink);
}

.section-label { color: var(--muted); font-size: 0.85rem; font-weight: 600; margin: 0.4rem 0 0.5rem; }

/* Kartu pertanyaan cepat (tombol di area utama) */
[data-testid="stMain"] .stButton > button,
section.main .stButton > button {
  width: 100%; min-height: 78px; padding: 0.9rem 1rem;
  background: var(--card); border: 1px solid var(--line); border-radius: 16px;
  color: var(--ink); text-align: left; justify-content: flex-start;
  box-shadow: 0 1px 2px rgba(31,35,64,0.04);
  transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
}
[data-testid="stMain"] .stButton > button:hover,
section.main .stButton > button:hover {
  transform: translateY(-2px); border-color: var(--primary);
  box-shadow: 0 8px 20px rgba(91,91,214,0.14); color: var(--ink);
}
[data-testid="stMain"] .stButton > button p,
section.main .stButton > button p { font-weight: 600; font-size: 0.92rem; text-align: left; }

/* Tombol di sidebar tetap sederhana */
[data-testid="stSidebar"] .stButton > button {
  border-radius: 12px; border: 1px solid var(--line); font-weight: 600;
}

/* Bubble chat */
[data-testid="stChatMessage"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 18px;
  padding: 0.9rem 1.05rem; margin-bottom: 0.7rem;
  box-shadow: 0 1px 2px rgba(31,35,64,0.04);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
  background: var(--primary-soft); border-color: #DADAF8;
}
[data-testid="stChatMessageAvatarUser"] { background: var(--primary); }
[data-testid="stChatMessageAvatarAssistant"],
[data-testid="stChatMessageAvatarCustom"] {
  background: linear-gradient(135deg, #E8478B, #14B8A6);
}

/* Kolom input chat */
[data-testid="stChatInput"] {
  border-radius: 18px; border: 1px solid var(--line); background: var(--card);
  box-shadow: 0 6px 24px rgba(31,35,64,0.07);
}
[data-testid="stChatInput"]:focus-within { border-color: var(--primary); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------
# Helper
# ---------------------------------------------------------------
def get_api_key() -> str:
    """Ambil API key dari st.secrets, lalu environment variable."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    return os.getenv("GEMINI_API_KEY", "")


def build_system_prompt(gaya: str, level: str, rekomendasi: bool) -> str:
    gaya_text = {
        "Santai": "Gunakan bahasa Indonesia yang santai, ramah, seperti kakak tingkat yang sabar. Boleh pakai emoji secukupnya.",
        "Formal": "Gunakan bahasa Indonesia yang formal, rapi, dan profesional. Jangan pakai emoji.",
    }[gaya]
    level_text = {
        "Pemula": "Anggap pengguna baru belajar. Hindari jargon, pakai analogi sehari-hari, jelaskan istilah teknis.",
        "Menengah": "Anggap pengguna sudah paham dasar. Boleh pakai istilah teknis dan contoh kode ringkas.",
    }[level]
    rekom_text = (
        "Di akhir jawaban, berikan 2-3 rekomendasi topik lanjutan yang bisa dipelajari berikutnya."
        if rekomendasi
        else "Tidak perlu memberikan rekomendasi topik lanjutan kecuali diminta."
    )
    return f"""Kamu adalah DataPals, asisten belajar Data Science untuk pelajar Indonesia.
Domain pengetahuanmu: Python, pandas, statistik, visualisasi data, machine learning, SQL, dan LLM/AI.
{gaya_text}
{level_text}
{rekom_text}
Aturan:
- Jika pertanyaan di luar domain Data Science/AI, tolak dengan sopan dan arahkan kembali ke topik belajar.
- Jawaban singkat dan terstruktur. Gunakan contoh kode dalam blok kode jika membantu.
- Jika tidak yakin, katakan terus terang, jangan mengarang."""


def to_contents(messages):
    """Ubah riwayat chat Streamlit ke format Gemini."""
    return [
        types.Content(role=m["role"], parts=[types.Part(text=m["content"])])
        for m in messages
    ]


def stream_reply(client, model, contents, system_prompt, temperature):
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=temperature,
    )
    for chunk in client.models.generate_content_stream(
        model=model, contents=contents, config=config
    ):
        if chunk.text:
            yield chunk.text


def stream_with_fallback(client, contents, system_prompt, temperature):
    """Coba tiap model (1x ulang jika gagal). Return (model, potongan_pertama, generator)."""
    last_err = None
    for model in MODELS:
        for attempt in range(2):
            try:
                gen = stream_reply(client, model, contents, system_prompt, temperature)
                first = next(gen, "")
                return model, first, gen
            except Exception as e:
                last_err = e
                msg = str(e)
                # Error yang tidak akan sembuh dengan mencoba model lain
                if any(k in msg for k in ("API key", "API_KEY", "PERMISSION_DENIED", "INVALID_ARGUMENT")):
                    raise
                if attempt == 0:
                    time.sleep(2)
    raise last_err


# ---------------------------------------------------------------
# Sidebar: parameter kreatif
# ---------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Pengaturan")

    api_key = get_api_key()
    if not api_key:
        api_key = st.text_input("Gemini API Key", type="password")
        st.caption("Dapatkan gratis di Google AI Studio.")

    gaya = st.radio("Gaya bahasa", ["Santai", "Formal"], horizontal=True)
    level = st.selectbox("Level kamu", ["Pemula", "Menengah"])
    temperature = st.slider("Kreativitas (temperature)", 0.0, 1.5, 0.7, 0.1)
    use_memory = st.toggle("Ingat percakapan (memory)", value=True)
    rekomendasi = st.toggle("Rekomendasi topik lanjutan", value=True)

    if st.button("🗑️ Reset percakapan", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.divider()
    st.caption(f"Model: `{MODEL}`")

# ---------------------------------------------------------------
# Halaman utama
# ---------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

memory_chip = "🧠 Memory aktif" if use_memory else "💤 Memory mati"
chips_html = (
    '<div class="chips">'
    f'<span class="chip">🗣️ {gaya}</span>'
    f'<span class="chip">🎓 {level}</span>'
    f'<span class="chip">🌡️ Kreativitas {temperature:.1f}</span>'
    f'<span class="chip">{memory_chip}</span>'
    "</div>"
)

if not st.session_state.messages:
    # Tampilan sambutan (chat masih kosong)
    st.markdown(
        '<div class="hero">'
        '<span class="hero-badge">✨ Ditenagai Gemini</span>'
        "<h1>DataPals</h1>"
        "<p>Teman belajar Data Science kamu. Tanya apa saja, dari pandas sampai machine learning.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    st.markdown(chips_html, unsafe_allow_html=True)
    st.markdown('<div class="section-label">Coba tanya salah satu ini</div>', unsafe_allow_html=True)
    cols = st.columns(2)
    for i, (icon, q) in enumerate(QUICK_PROMPTS):
        if cols[i % 2].button(f"{icon}  {q}", key=f"quick_{i}", use_container_width=True):
            st.session_state.pending = q
            st.rerun()
else:
    # Header ringkas (chat sudah berjalan)
    st.markdown(
        '<div class="mini"><span class="logo">📊</span><span class="name">DataPals</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(chips_html, unsafe_allow_html=True)

# Tampilkan riwayat chat
for m in st.session_state.messages:
    with st.chat_message("user" if m["role"] == "user" else "assistant"):
        st.markdown(m["content"])

prompt = st.chat_input("Tanya apa saja soal Data Science...")
if "pending" in st.session_state:
    prompt = st.session_state.pop("pending")

if prompt:
    if not api_key:
        st.warning("Masukkan Gemini API Key dulu di sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    client = genai.Client(api_key=api_key)
    system_prompt = build_system_prompt(gaya, level, rekomendasi)
    history = st.session_state.messages if use_memory else st.session_state.messages[-1:]

    with st.chat_message("assistant"):
        try:
            with st.spinner("DataPals lagi mikir..."):
                used_model, first, gen = stream_with_fallback(
                    client, to_contents(history), system_prompt, temperature
                )

            def full_stream():
                yield first
                yield from gen

            reply = st.write_stream(full_stream())
            st.session_state.messages.append({"role": "model", "content": reply})
            if used_model != MODEL:
                st.caption(f"ℹ️ Dijawab oleh model cadangan: `{used_model}`")
        except Exception as e:
            st.error(f"Terjadi error saat memanggil Gemini: {e}")
            st.session_state.messages.pop()