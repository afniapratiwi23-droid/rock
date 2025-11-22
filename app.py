import streamlit as st
import os
from dotenv import load_dotenv
import time
from generator import configure_genai, generate_outline, generate_chapter, generate_ebook_metadata
from document_maker import create_ebook
from io import BytesIO

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Ebook Generator Gemini AI", layout="centered", page_icon="📚", initial_sidebar_state="collapsed")

# Custom CSS for better UI
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
    }
    .main-header {
        font-size: 2em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1em;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "topic": "",
        "target_audience": "",
        "num_chapters": 6,
        "word_count": 1500,
        "tone": "Lucu, Santai, dan Mengena",
        "perspective": "Otomatis (disarankan)",
        "core_problem": "",
        "core_message": "",
        "case_study_type": "Kantoran umum (HR, atasan, tim)",
        "emotional_tone": "Satir tajam (menyindir realitas)"
    }

if "outline" not in st.session_state:
    st.session_state.outline = []
if "ebook_buffer" not in st.session_state:
    st.session_state.ebook_buffer = None

# Sidebar for API Key
with st.sidebar:
    st.header("🔑 Konfigurasi API")
    
    # Helper function to save keys
    def save_keys_to_env(keys):
        env_content = ""
        # Read existing env to preserve other vars if needed (simple append/overwrite for now)
        for i, key in enumerate(keys):
            if key:
                env_content += f"GEMINI_API_KEY_{i+1}={key}\n"
        
        with open(".env", "w") as f:
            f.write(env_content)
        st.toast("✅ API Key tersimpan! Tidak perlu input ulang nanti.", icon="💾")

    # Multiple API Keys for Rotation
    api_keys = []
    # Auto-collapse if key 1 is present
    is_expanded = not bool(os.getenv("GEMINI_API_KEY_1"))
    with st.sidebar.expander("Pengaturan API Key (Rotasi Otomatis)", expanded=is_expanded):
        st.info("Masukkan hingga 4 API Key. Sistem akan otomatis ganti key jika kuota habis.")
        
        # Load from env
        default_k1 = os.getenv("GEMINI_API_KEY_1", "")
        default_k2 = os.getenv("GEMINI_API_KEY_2", "")
        default_k3 = os.getenv("GEMINI_API_KEY_3", "")
        default_k4 = os.getenv("GEMINI_API_KEY_4", "")

        key1 = st.text_input("Google Gemini API Key 1 (Utama)", value=default_k1, type="password")
        key2 = st.text_input("Google Gemini API Key 2 (Cadangan 1)", value=default_k2, type="password")
        key3 = st.text_input("Google Gemini API Key 3 (Cadangan 2)", value=default_k3, type="password")
        key4 = st.text_input("Google Gemini API Key 4 (Cadangan 3)", value=default_k4, type="password")
        
        if key1: api_keys.append(key1)
        if key2: api_keys.append(key2)
        if key3: api_keys.append(key3)
        if key4: api_keys.append(key4)
        
        if st.button("💾 Simpan API Key Permanen"):
            save_keys_to_env([key1, key2, key3, key4])

    if not api_keys:
        st.warning("⚠️ Masukkan setidaknya satu API Key untuk memulai.")
        st.stop()

    # Configure Gemini with list of keys
    if configure_genai(api_keys):
        st.sidebar.success(f"✅ {len(api_keys)} API Key Terhubung!")
    else:
        st.sidebar.error("❌ Gagal menghubungkan API Key.")

# Main UI
st.markdown('<div class="main-header">Ebook Generator Gemini AI</div>', unsafe_allow_html=True)

# Top section: Topic and Auto-fill
col1, col2 = st.columns([3, 1])
with col1:
    topic = st.text_input("Tempel atau tulis judul/topik di sini", value=st.session_state.form_data["topic"], placeholder="Contoh: Cara Bangun Pagi Tanpa Drama")
with col2:
    st.write("") # Spacer
    st.write("") # Spacer
    if st.button("✨ Isi Otomatis"):
        if not topic:
            st.warning("Isi topik dulu!")
        elif not api_keys:
            st.error("Masukkan API Key di sidebar!")
        else:
            with st.spinner("Menganalisis topik..."):
                metadata = generate_ebook_metadata(topic)
                if metadata:
                    st.session_state.form_data.update(metadata)
                    st.session_state.form_data["topic"] = topic
                    st.rerun()

st.caption("AI akan mengisi otomatis target audiens, jumlah bab, target kata, gaya, sudut pandang, pesan, dan lainnya.")

# Form Inputs
st.session_state.form_data["topic"] = topic
st.session_state.form_data["target_audience"] = st.text_input("Target Pembaca", value=st.session_state.form_data["target_audience"])

c1, c2 = st.columns(2)
with c1:
    st.session_state.form_data["num_chapters"] = st.number_input("Jumlah Bab", min_value=1, max_value=20, value=st.session_state.form_data["num_chapters"])
with c2:
    st.session_state.form_data["word_count"] = st.number_input("Target Kata per Bab", min_value=500, max_value=5000, value=st.session_state.form_data["word_count"], help="Saran: 1500-2000 kata untuk pembahasan mendalam.")

st.session_state.form_data["tone"] = st.selectbox("Gaya Bahasa", 
    ["Lucu, Santai, dan Mengena", "Formal & Profesional", "Motivasi Menggebu-gebu", "Sarkas & Humoris", "Empatik & Lembut"], 
    index=0 if st.session_state.form_data["tone"] not in ["Lucu, Santai, dan Mengena", "Formal & Profesional", "Motivasi Menggebu-gebu", "Sarkas & Humoris", "Empatik & Lembut"] else ["Lucu, Santai, dan Mengena", "Formal & Profesional", "Motivasi Menggebu-gebu", "Sarkas & Humoris", "Empatik & Lembut"].index(st.session_state.form_data["tone"])
)

# Advanced Settings
with st.expander("⚙️ Penguat Kualitas Naskah", expanded=True):
    st.session_state.form_data["perspective"] = st.selectbox("Sudut Pandang / Perspektif", ["Otomatis (disarankan)", "Orang Pertama (Saya)", "Orang Kedua (Anda)", "Orang Ketiga (Dia)"], index=0)
    
    st.session_state.form_data["core_problem"] = st.text_area("Masalah Utama", value=st.session_state.form_data["core_problem"], placeholder="Opsional: 1-2 kalimat masalah inti.", height=68)
    
    st.session_state.form_data["core_message"] = st.text_input("Pesan Utama Ebook", value=st.session_state.form_data["core_message"], placeholder="Opsional: 1 kalimat inti besar ebook.")
    
    ac1, ac2 = st.columns(2)
    with ac1:
        st.session_state.form_data["case_study_type"] = st.selectbox("Jenis Studi Kasus", ["Kantoran umum (HR, atasan, tim)", "Bisnis Online / UMKM", "Kehidupan Rumah Tangga", "Mahasiswa / Akademik", "Freelancer / Remote Work"], index=0)
    with ac2:
        st.session_state.form_data["emotional_tone"] = st.selectbox("Nada Emosional Dominan", ["Satir tajam (menyindir realitas)", "Optimis & Membangun", "Realistis & Logis", "Provokatif & Menantang"], index=0)

# Action Buttons
b1, b2 = st.columns([3, 1])
with b1:
    if st.button("🚀 Buat Ebook", type="primary"):
        if not api_keys:
            st.error("Mohon masukkan Gemini API Key di sidebar.")
        elif not topic:
            st.error("Mohon masukkan topik.")
        else:
            # Generate Outline First
            with st.spinner("Merancang struktur ebook..."):
                # Pass all params to generate_outline
                outline = generate_outline(topic, st.session_state.form_data["num_chapters"])
                if outline:
                    st.session_state.outline = outline
                    
                    # Generate Preface
                    status_text = st.empty()
                    status_text.text("Menulis Kata Pengantar...")
                    from generator import generate_preface, generate_conclusion
                    preface = generate_preface(topic, st.session_state.form_data)
                    
                    # Generate Content
                    chapters_content = []
                    full_outline_str = "\n".join([f"{i+1}. {title}" for i, title in enumerate(outline)])

                    for i, chapter_title in enumerate(outline):
                        with st.status(f"✍️ Menulis Bab {i+1}: {chapter_title}...", expanded=True) as status:
                            # Pass chapter_num (i+1) and full outline to generator
                            content = generate_chapter(topic, chapter_title, st.session_state.form_data, i+1, full_outline_str)
                            
                            if content:
                                chapters_content.append((chapter_title, content))
                                status.update(label=f"✅ Bab {i+1} Selesai!", state="complete", expanded=False)
                            else:
                                status.update(label=f"❌ Gagal menulis Bab {i+1}", state="error")
                                st.error("Gagal menghasilkan konten bab. Coba lagi.")
                                st.stop()
                    
                    status_text.text("Menulis Penutup...")
                    conclusion = generate_conclusion(topic, st.session_state.form_data)
                    
                    status_text.text("Menyusun Ebook...")
                    doc = create_ebook(topic, preface, chapters_content, conclusion)
                    
                    # Save to buffer
                    buffer = BytesIO()
                    doc.save(buffer)
                    buffer.seek(0)
                    st.session_state.ebook_buffer = buffer
                    st.success("Ebook Berhasil Dibuat!")
                    st.rerun()
                else:
                    st.error("Gagal membuat outline.")

with b2:
    if st.button("🔄 Reset"):
        st.session_state.form_data = {
            "topic": "",
            "target_audience": "",
            "num_chapters": 6,
            "word_count": 1000,
            "tone": "Lucu, Santai, dan Mengena",
            "perspective": "Otomatis (disarankan)",
            "core_problem": "",
            "core_message": "",
            "case_study_type": "Kantoran umum (HR, atasan, tim)",
            "emotional_tone": "Satir tajam (menyindir realitas)"
        }
        st.session_state.outline = []
        st.session_state.ebook_buffer = None
        st.rerun()

# Download Button - Only show if ebook has been generated
if st.session_state.ebook_buffer is not None:
    st.markdown("---")
    st.success("✅ Ebook Anda siap diunduh!")
    st.download_button(
        label="📥 Unduh Ebook (.docx)",
        data=st.session_state.ebook_buffer,
        file_name=f"{topic.replace(' ', '_')}.docx" if topic else "ebook.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
