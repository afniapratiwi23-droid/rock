# Ebook Generator Antigravity

Aplikasi ini adalah generator ebook berbasis AI yang menggunakan Google Gemini untuk membuat ebook format .docx yang siap pakai.

## Prasyarat

- Python 3.8+
- Akun Google Cloud dengan API Key Gemini

## Cara Menjalankan (Akses)

Aplikasi ini menggunakan **Streamlit**. Berikut cara menjalankannya:

### 1. Aktifkan Virtual Environment
Jika Anda menggunakan Mac/Linux:
```bash
source .venv/bin/activate
```
Jika Anda menggunakan Windows:
```bash
.venv\Scripts\activate
```

### 2. Instal Dependensi (Jika belum)
```bash
pip install -r requirements.txt
```

### 3. Jalankan Aplikasi
```bash
streamlit run app.py
```

Aplikasi akan otomatis terbuka di browser Anda di alamat: `http://localhost:8501`

## Konfigurasi API Key

### Opsi 1: Input Manual di UI
Saat aplikasi terbuka, masukkan Google Gemini API Key Anda di sidebar sebelah kiri (satu key per baris).

### Opsi 2: Menggunakan Streamlit Secrets (Rekomendasi untuk Deployment)
Buat file `.streamlit/secrets.toml` dengan format:
```toml
[gemini]
api_keys = [
    "AIzaSyAbc123...",
    "AIzaSyDef456...",
    "AIzaSyGhi789..."
]
```

Atau jika di **Streamlit Cloud**, masukkan di **App Settings > Secrets** dengan format yang sama.

