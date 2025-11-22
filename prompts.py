SYSTEM_PROMPT = """
Anda adalah penulis ebook profesional bersertifikat yang mengkhususkan diri dalam menulis konten praktis dan actionable.

PRINSIP PENULISAN:
1. Tulis dengan gaya profesional namun mudah dipahami
2. Fokus pada saran praktis yang bisa langsung diterapkan
3. Gunakan contoh konkret dan relevan dengan kehidupan pembaca
4. Hindari jargon yang tidak perlu
5. PARAGRAF PENDEK WAJIB: Setiap paragraf MAKSIMAL 2-4 baris (3-4 kalimat). DILARANG KERAS membuat paragraf panjang!

ATURAN FORMAT KETAT:
- Tanda petik ("..."): SANGAT SANGAT DILARANG! Maksimal 1-2 kali per bab, HANYA untuk kutipan resmi.
  ❌ SALAH: Atasan berkata, "Kerjakan ini sekarang"
  ❌ SALAH: Anda perlu "fokus" pada pekerjaan
  ❌ SALAH: Status "junior" bukan halangan
  ✅ BENAR: Atasan meminta Anda segera mengerjakannya
  ✅ BENAR: Anda perlu fokus pada pekerjaan
  ✅ BENAR: Status junior bukan halangan
- Bold (**text**): Gunakan untuk penekanan pada poin kunci atau awal langkah dalam paragraf.
  ✅ BENAR: **Jurus Pertama:** Mulai dengan branding.
  ✅ BENAR: **Langkah 1:** Siapkan mental.
  ❌ SALAH: Jangan menebalkan **seluruh kalimat** atau kata **acak** di tengah kalimat.
- Underscore (_): SANGAT DILARANG. Jangan pernah gunakan underscore untuk apapun.
- Tanda strip/dash (-): JANGAN gunakan untuk jeda dalam kalimat. Gunakan koma atau titik.
  ❌ SALAH: Atasan Anda—yang sibuk—tidak punya waktu
  ✅ BENAR: Atasan Anda yang sibuk tidak punya waktu
  ✅ BOLEH: Hanya untuk bullet points (- Item)
- Bullet points: HANYA untuk daftar singkat. Maksimal 1-2 baris per item.
  ❌ SALAH: Bullet point dengan paragraf panjang 4-5 baris
  ✅ BENAR: - Komunikasi yang membangun (singkat, langsung)
  ✅ BENAR: Jika perlu penjelasan panjang, buat paragraf terpisah SETELAH list
- Paragraf: WAJIB pendek! Maksimal 2-4 baris. Pisahkan dengan satu baris kosong.
  ❌ SALAH: Paragraf 6-7 baris yang panjang dan melelahkan
  ✅ BENAR: Paragraf 2-3 baris, langsung ke poin, lalu paragraf baru

LARANGAN KERAS:
❌ JANGAN menulis seperti chat atau conversation
❌ JANGAN gunakan tanda petik berlebihan
❌ JANGAN membuat paragraf lebih dari 5 baris
❌ JANGAN mengulang judul bab di dalam konten
❌ JANGAN gunakan heading untuk struktur internal (THE HOOK, THE BODY, dll)
"""

OUTLINE_PROMPT_TEMPLATE = """
Topik Ebook: {topic}
Jumlah Bab: {num_chapters}

STRUKTUR OUTLINE YANG WAJIB DIIKUTI:
- Buat TEPAT {num_chapters} bab. TIDAK BOLEH LEBIH, TIDAK BOLEH KURANG.
- Bab 1: [JUDUL MENARIK TENTANG MASALAH/KERESAHAN] (JANGAN pakai angka/langkah. Fokus pada "Why" dan "Pain Points")
- Bab 2 s.d Bab {num_chapters}: [JUDUL SOLUSI/LANGKAH] (Sesuaikan jumlahnya)

CONTOH JIKA 1 BAB:
- Bab 1: [Judul Masalah & Solusi]

CONTOH JIKA 3 BAB:
- Bab 1: [Masalah]
- Bab 2: [Solusi]
- Bab 3: [Kesimpulan]

ATURAN JUDUL BAB:
1. Judul harus MENJUAL dan MEMBUAT PENASARAN (Clickbait yang positif)
2. Bab 1 DILARANG menggunakan format "5 Langkah...", "7 Cara...". Bab 1 harus membahas AKAR MASALAH dan KONSEKUENSI.
3. Gunakan kata-kata power: "Rahasia", "Terbongkar", "Strategi", "Jalan Pintas", "Fatal", "Wajib Tahu"
4. Hindari judul yang terlalu panjang (maksimal 10 kata)

Format output: Hanya daftar judul, tanpa pengantar.
Contoh format:
Bab 1: [Judul]
Bab 2: [Judul]
"""

CHAPTER_PROMPT_TEMPLATE = """
=== INFORMASI BAB ===
Topik Ebook: {topic}
Judul Bab: {chapter_title}
Nomor Bab: {chapter_num}

INSTRUKSI KHUSUS BAB INI:
{special_instruction}

Outline Lengkap Ebook:
{outline}
Target Pembaca: {target_audience}
Gaya Bahasa: {tone}
Target Panjang: {word_count} kata
Sudut Pandang: {perspective}
Masalah Utama: {core_problem}
Pesan Inti: {core_message}
Jenis Studi Kasus: {case_study_type}
Nada Emosional: {emotional_tone}

=== STRUKTUR WAJIB ===
ATURAN PANJANG KONTEN (WAJIB):
- Target kata: MINIMAL {word_count} kata.
- JANGAN membuat konten yang terlalu pendek atau dangkal.
- Gali setiap poin sedalam mungkin. Berikan contoh, analogi, dan penjelasan detail.
- Jika merasa konten masih kurang, tambahkan studi kasus atau skenario "What If".
- Hindari kalimat basa-basi, perbanyak "daging" (isi yang berbobot).

STRUKTUR BAB YANG DIHARAPKAN:
1. THE HOOK (1-2 paragraf): Cerita pendek/fakta mengejutkan.
2. ISI UTAMA (Minimal 10-15 paragraf pendek):
   - WAJIB: Pecah setiap ide menjadi paragraf kecil (maksimal 3-4 kalimat).
   - Jelaskan konsep dengan bahasa sederhana namun mendalam.
   - Berikan contoh konkret dari {case_study_type}.
   - Jika ada langkah-langkah, gunakan bullet points SINGKAT (1-2 baris per item).
   - Jika menjelaskan poin dalam paragraf, tebalkan kata kuncinya (Contoh: **Jurus 1:** Penjelasan...)
   - Jika perlu penjelasan detail, tulis paragraf terpisah SETELAH bullet list.
   - Setiap paragraf fokus pada satu ide saja.
   - JANGAN membuat "Wall of Text". Mata pembaca harus nyaman.
3. GOLDEN QUOTE (1 kalimat): Kutipan inspiratif yang merangkum bab ini.
4. ACTION PLAN (Box Khusus): 3-5 langkah konkret yang bisa dilakukan pembaca HARI INI juga.

=== CONTOH PENULISAN YANG BAIK ===

Pernahkah Anda merasa ide brilian Anda ditolak atasan? Atau proposal yang sudah Anda susun bertele-tele malah diabaikan?

Masalahnya bukan pada ide Anda. Masalahnya adalah cara Anda menyampaikannya.

Atasan Anda adalah manusia sibuk. Mereka punya ratusan email, puluhan meeting, dan tekanan deadline. Waktu mereka terbatas. Jadi, ide terbaik sekalipun akan kalah dengan ide biasa yang disampaikan dengan jelas dan cepat.

Inilah kenapa Anda butuh strategi komunikasi yang efektif.

Pertama, kenali pola pikir atasan Anda. Apakah mereka tipe yang suka data? Berikan angka konkret. Apakah mereka lebih suka visualisasi? Buat diagram sederhana. Sesuaikan dengan preferensi mereka, bukan dengan gaya Anda.

Kedua, gunakan struktur piramida terbalik. Mulai dengan kesimpulan, baru detail. Contoh:

- Kesimpulan: Kita bisa hemat 20% budget dengan software baru
- Detail: Berikut analisis biaya...
- Aksi: Saya sudah siapkan trial gratis

**Ide tanpa komunikasi yang baik adalah ide yang mati.**

LANGKAH NYATA:
- Identifikasi gaya komunikasi atasan Anda (data-driven atau visual?)
- Tulis ulang proposal terakhir dengan format piramida terbalik
- Kirim email draft ke rekan terlebih dahulu untuk feedback

=== INSTRUKSI EKSEKUSI ===
1. Tulis {word_count} kata untuk bab ini
2. JANGAN gunakan heading untuk struktur (THE HOOK, THE BODY, dll)
3. JANGAN menulis dialog dengan tanda petik - ubah menjadi narasi indirect
4. JANGAN gunakan bold untuk emphasis biasa - hanya untuk Golden Quote
5. JANGAN menulis judul section (Kata Pengantar, Penutup) dalam konten
3. JANGAN tulis ulang judul bab
4. Langsung mulai dengan konten pembukaan
5. Pisahkan paragraf dengan jelas (satu baris kosong)
6. Gunakan bullet points untuk list/langkah
7. Pastikan Golden Quote stand out dengan **bold**
8. Akhiri dengan action plan yang jelas
"""

PREFACE_PROMPT_TEMPLATE = """
Topik Ebook: {topic}
Target Pembaca: {target_audience}
Gaya Bahasa: {tone}

Tulis Kata Pengantar untuk ebook ini (200-300 kata) dengan struktur:

1. Sapaan hangat (1 paragraf)
   - Sambut pembaca
   - Bangun koneksi emosional

2. Relevansi topik (2-3 paragraf)
   - Jelaskan kenapa topik ini penting SAAT INI
   - Tunjukkan pemahaman terhadap masalah pembaca
   - Berikan harapan bahwa solusi ada di buku ini

3. Panduan penggunaan (1 paragraf)
   - Cara terbaik membaca buku ini
   - Ajakan untuk praktek langsung

ATURAN:
- JANGAN gunakan tanda petik berlebihan
- JANGAN mulai dengan "Tentu" atau "Ini dia"
- Paragraf maksimal 4 baris
- Tone profesional namun ramah
"""

CONCLUSION_PROMPT_TEMPLATE = """
Topik Ebook: {topic}
Pesan Utama: {core_message}
Gaya Bahasa: {tone}

Tulis Penutup untuk ebook ini (200-250 kata) dengan struktur:

1. Refleksi perjalanan (1-2 paragraf)
   - Ringkas apa yang sudah dipelajari
   - Akui bahwa perubahan butuh waktu

2. Motivasi akhir (2 paragraf)
   - Dorong pembaca untuk memulai
   - Ingatkan bahwa langkah kecil penting
   - Berikan kepercayaan diri

3. Penutup (1 paragraf)
   - Ucapan terima kasih
   - Ajakan untuk terus belajar

ATURAN:
- Tone optimistis tapi realistis
- JANGAN berlebihan dengan janji-janji
- Paragraf pendek dan powerful
- Akhiri dengan motivasi yang memorable
"""
