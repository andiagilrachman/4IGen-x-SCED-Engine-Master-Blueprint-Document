# 📌 PROGRESS.md — Catatan Progres Proyek 4IGen x SCED Engine

> File ini adalah sumber kebenaran progres proyek. Baca file ini di awal
> setiap sesi kerja baru untuk tahu di mana pekerjaan terakhir berhenti.

---

## ✅ SELESAI

### 1. Audit lengkap struktur repo (2026-08-23)
- Review menyeluruh: `BLUEPRINT.md`, `teacher_master_prompt.md`, dataset sintetis
  5 aset pilot, `sced_pilot_train.jsonl`, `icbp_test_schema.json`, notebook training.
- Temuan: kerangka legal (GREEN/YELLOW/RED, Zero-Narrative Scraping) solid,
  format data → training konsisten.

### 2. Fix bug Sel 9 notebook — struktur input eval vs training (2026-08-23)
- **Masalah:** Sel 9 (ujian ICBP) mengirim seluruh `icbp_test_schema.json`
  termasuk `metadata`, padahal data training di `sced_pilot_train.jsonl`
  hanya menyertakan `financial_metrics` + `macro_context`. Struktur input
  yang beda antara training dan eval membuat hasil ujian tidak representatif.
- **Fix:** Sel 9 sekarang membuang `metadata` dari `icbp_data_full` sebelum
  dikirim ke prompt, menyamakan struktur dengan format training.
- **Status:** Sudah live di `main` (commit `9c29404`).

### 3. Cek token length dataset pilot (2026-08-23)
- 20 sampel di `sced_pilot_train.jsonl` dicek: rata-rata ~620 token,
  maksimum ~731 token (estimasi char/3.5, bukan tokenizer asli Qwen).
- `max_seq_length=2048` di notebook **aman**, ada margin besar — tidak ada
  risiko truncation untuk dataset saat ini.
- **Belum diverifikasi dengan tokenizer asli** — perlu jalankan
  `len(tokenizer.encode(text))` langsung di Colab sebelum training penuh
  untuk kepastian, terutama setelah data discaling (CoT bisa lebih panjang).

### 4. Susun anchor makro historis riil — `data/macro_anchors.json` (2026-08-23)
- **Keputusan pendekatan:** kombinasi anchor historis riil + skenario sintetis
  di atasnya (bukan cuma satu atau yang lain).
- Riset & susun 3 periode makro riil Indonesia sebagai anchor:
  - **Maret 2023** — BI Rate 5.75%, Inflasi YoY 4.97% (sumber: BI, BPS)
  - **Desember 2023** — BI Rate 6.00%, Inflasi YoY 2.61% (sumber: BI, BPS)
  - **Q3 2024** — BI Rate 6.00%, Inflasi YoY 2.12% (periode yang sudah
    dipakai di dataset pilot sebelumnya, dipertahankan sebagai anchor ke-3)
- File tersimpan di `data/macro_anchors.json`, lengkap dengan sumber dan
  catatan penggunaan (kapan pakai anchor riil vs skenario sintetis turunan).
- **Belum diverifikasi lebih presisi:** `usd_idr_exchange_rate_approx` dan
  `economic_growth_gdp_percent` di 2 anchor baru (Maret & Desember 2023)
  masih estimasi mendekati, bukan angka resmi per-kuartal — perlu
  diverifikasi lagi sebelum dipakai untuk scaling besar (500-10.000 data).

---

## 🔜 BELUM DIKERJAKAN (urutan prioritas)

### 5. ✅ Klarifikasi Model Guru (Teacher Model) API — RISIKO DITURUNKAN (2026-08-23)
- **Model Guru yang dipakai:** Gemini (Google).
- **Teks resmi ToS diverifikasi langsung** (Gemini API Additional Terms of
  Service, efektif 23 Maret 2026, dari `ai.google.dev/gemini-api/terms`,
  disediakan lengkap oleh user).
- **Klausul kunci:** "You may not use the Services to develop models that
  compete with the Services (e.g., Gemini API or Google AI Studio). You also
  may not attempt to reverse engineer, extract or replicate any component of
  the Services, including the underlying data or models (e.g., parameter
  weights)."
- **Analisis:** larangan ini merujuk pada membangun *layanan/API LLM tujuan
  umum yang bersaing langsung dengan Gemini API/Google AI Studio* — bukan
  larangan umum "model apa pun yang dilatih dengan bantuan Gemini." SCED
  Engine adalah model kecil (7B) fine-tuned sempit untuk satu domain
  (finansial IHSG), terintegrasi ke satu produk (4IGen.com), tidak
  diposisikan sebagai API LLM umum yang bersaing dengan Gemini/AI Studio —
  karakternya beda dari yang dilarang klausul ini.
- **Nuansa yang tetap perlu hati-hati:** frasa "tidak boleh reverse
  engineer/extract/replicate underlying model" — proses generate data
  sintetis sebaiknya tetap mengikuti aturan ketat "Strict Fact Adherence"
  yang sudah ada di `teacher_master_prompt.md` (bukan sekadar re-package
  mentah), yang memang sudah jadi praktik proyek ini.
- **Kesimpulan (bukan nasihat hukum resmi):** risiko jauh lebih rendah dari
  dugaan awal, cukup aman untuk lanjut skala saat ini. Rekomendasi: konsultasi
  singkat ke pengacara IP/teknologi sebelum scaling penuh ke 10.000 data dan
  sebelum proyek menghasilkan revenue signifikan, sebagai langkah kehati-hatian
  standar untuk komersialisasi jangka panjang — bukan karena ada red flag
  spesifik yang ditemukan.

### 6. ✅ Sumber data fundamental terstruktur ditemukan — `financial_rows` & `indicator_snapshot_fundamental` (2026-08-23)
- User mengirim export tabel dari 2 database proyek lain miliknya:
  - **`4igen` → `financial_rows`**: data laporan keuangan mentah (Neraca/BS,
    Laba-Rugi/IS, Arus Kas/CF, KeyStat), long-format per baris akun per
    kuartal, untuk **101 saham**. Row name lengkap dalam Bahasa Indonesia
    (contoh: "Jumlah aset", "Jumlah ekuitas", "Jumlah laba (rugi)",
    "Pendapatan bunga") — persis field yang dibutuhkan skema SCED
    (total_assets, net_income, revenue). Cakupan periode: Q1 2023 - Q2 2026.
  - **`aigen_db` → `indicator_snapshot_fundamental`**: rasio siap pakai
    (ROE, ROA, DER, PER, PBV, EPS, Altman Z-Score, Piotroski F-Score,
    Graham Number, fundamental_score) untuk **1.203 saham** (hampir seluruh
    IDX), snapshot 2026-08-21. Beberapa field tambahan (dividend_yield,
    revenue_growth_yoy, net_profit_margin, current_ratio) ADA di skema
    tabel tapi NULL di data sample yang dicek — perlu dicek lagi apakah
    terisi untuk saham lain.
  - File SQL disimpan lokal di sesi kerja (belum di-commit ke repo — file
    besar berisi data vendor komersial, TIDAK untuk taruh di GitHub, lihat
    poin 6b).
- **Ini menggantikan pendekatan riset manual web search satu-per-satu**
  (yang terbukti tidak scalable di percobaan sebelumnya) — jauh lebih
  efisien dan konsisten karena satu sumber terstruktur untuk ratusan saham.

### 6b. ⚠️ Klarifikasi ToS DataSectors & Invezgo — RISIKO CAMPURAN, PERLU AKSI (2026-08-23)
- **ToS DataSectors** (`datasectors.com/terms`, dibaca lengkap): generik —
  soal rate limit, pembayaran, disclaimer akurasi, batas tanggung jawab.
  TIDAK ADA klausul eksplisit larangan reuse data untuk training model atau
  produk turunan. **Risiko rendah** — wajar dibaca sebagai data API boleh
  dipakai membangun produk sendiri termasuk fine-tuning model internal.
- **ToS Invezgo** (`invezgo.com/id/terms`, dibaca lengkap): ADA klausul
  ketat — "Everything on Invezgo.com... belongs to Invezgo or its
  partners... You can print or save it for **personal, non-commercial use
  only**. You may not copy, share, or sell any content without
  permission..." Klausul ini kemungkinan besar juga mencakup "Invezgo
  Data" (didefinisikan di bagian lain ToS sebagai akses data finansial
  eksklusif untuk subscriber), bukan cuma artikel/konten editorial.
  **Risiko lebih tinggi** — "personal, non-commercial use" jelas
  bertentangan dengan tujuan SCED Engine yang komersial.
- **Catatan penting:** ToS yang dibaca ini kemungkinan ToS umum
  website/konten Invezgo — ada kemungkinan ToS API/SDK Invezgo yang
  terpisah (produk developer mereka disebut di halaman lain: API, SDK,
  MCP) punya ketentuan berbeda. BELUM diverifikasi.
- **Data yang sudah dicek eksplisit bersumber Invezgo:** kolom
  `source='invezgo'` di `shareholder_composition`, dan `vendor_insight_score`
  di `indicator_snapshot_fundamental` menyebut "skor bawaan DataSectors
  insights untuk pembanding" (mengindikasikan `indicator_snapshot_fundamental`
  kemungkinan data campuran dari 2 vendor, perlu dicek lebih lanjut field
  mana dari vendor mana).
- **REKOMENDASI/KEPUTUSAN SEMENTARA:**
  1. Prioritaskan generate dataset training dari field yang jelas
     bersumber DataSectors dulu (lebih aman dipastikan).
  2. Field yang jelas dari Invezgo — TAHAN dulu sampai user cek apakah ada
     ToS API-spesifik Invezgo yang berbeda dari yang dibaca ini, atau
     tanya langsung ke support Invezgo soal izin pakai data untuk training
     model AI komersial.
  3. `financial_rows` (dari database `4igen`) perlu dicek lagi asalnya
     dari vendor mana — belum eksplisit ada kolom `source` di skema
     tabelnya (beda dari `aigen_db` yang beberapa tabelnya eksplisit
     mencatat source).
- **STATUS: belum sepenuhnya selesai** — aman lanjut untuk data
  DataSectors, tapi perlu keputusan/klarifikasi user untuk data Invezgo
  sebelum dipakai skala besar.

### 6c. ✅ Batch 2 dataset sintetis dibangun dari data database (2026-08-23)
- Tambah **anchor makro ke-4** di `data/macro_anchors.json`
  (`periode_agustus_2026_terkini`: BI Rate 4.75%, inflasi 4.76%,
  USD/IDR ~16.985, GDP 5.12%) — dibutuhkan karena snapshot
  `indicator_snapshot_fundamental` bertanggal 2026-08-21 (terkini),
  tidak konsisten kalau dipasangkan anchor 2023/2024.
- Dibangun 2 script reusable di `scripts/`:
  - `extract_fundamental_data.py` — parse `Database_Stock_1.sql` (mapping
    stock_id->symbol) + `aigen_db.sql` (indicator_snapshot_fundamental) jadi
    `fundamental_snapshot_all.json` (1.203 saham, HANYA field aman: ROE,
    ROA, DER, PER, PBV, EPS, BVPS, dividend_yield, growth rates, margins,
    current/quick ratio, Altman Z, Piotroski F, Graham Number,
    fundamental_score — `vendor_insight_score` proprietary SENGAJA di-skip).
  - `generate_batch2.py` — generate Q&A lensa "Value & Risk Margin" dari
    hasil ekstraksi ke format schema SCED.
- **Hasil:** `data/synthetic_dataset/batch2_fundamental_db_value_risk.json`
  — 4 entri baru (BMRI, UNVR, ANTM, ASII), semua dari data real database,
  BUKAN riset manual. ICBP sengaja dilewati (tetap reserved sebagai unseen
  eval data di `eval/icbp_test_schema.json`).
- Proof-of-concept manual (`bmri_synthetic_qa_PROOF_OF_CONCEPT.json`) DIHAPUS
  karena sudah tergantikan data yang lebih akurat dari database.
- **File SQL sumber (`Database_Stock_1.sql`, `aigen_db.sql`, dll) TIDAK
  di-commit ke GitHub** — cuma dipakai lokal di sesi kerja untuk ekstraksi,
  karena berisi data vendor mentah skala besar (bukan untuk didistribusi
  ulang, beda dengan hasil olahan/faktanya sendiri).

### 6d. Langkah selanjutnya untuk scaling lebih lanjut
- Perluas `generate_batch2.py` ke 3 lensa lain (Growth, Macro Sensitivity,
  Risk/Red Flags) untuk 4 saham yang sudah ada datanya.
- Perluas ke lebih banyak saham dari 1.203 yang tersedia di
  `fundamental_snapshot_all.json` (saat ini baru dipakai 4 dari 1.203).
- Manfaatkan juga `financial_rows` (data neraca/laba-rugi mentah historis
  101 saham, Q1 2023 - Q2 2026) untuk pasangan data historis + 3 anchor
  makro 2023/2024 yang sudah ada — ini akan memberi variasi periode yang
  lebih kaya dibanding cuma snapshot terkini.
- Tetap tunda pemakaian data eksplisit Invezgo (shareholder_composition,
  dll) sampai ToS API-spesifik dikonfirmasi (lihat poin 6b).
- Sebelum training final: audit manual sampel tiap batch baru, verifikasi
  `sector` field yang sengaja dikosongkan di batch2 (perlu join ke tabel
  `sectors`/`sector_id` agar lengkap).

### 7. Smoke test training run v0.1 di Colab
- Jalankan notebook end-to-end (10 sel) sebagai uji pipeline teknis, BUKAN
  uji kualitas model (dataset masih 20 baris, rawan overfit 3 epoch).
- Cek juga apakah `SFTTrainer`/versi library `trl` terbaru masih kompatibel
  dengan syntax di Sel 7 (API `trl` sering berubah antar versi).

### 8. Rencana deployment lokal (Ollama/LM Studio)
- Bahas cara gabungkan adapter LoRA hasil Colab + base model Qwen 2.5 7B
  untuk inferensi 100% offline di PC rumah user (i5, RAM 16GB, GPU AMD
  R7 4GB — tidak dipakai untuk training/inferensi berat).

---

## 🗒️ Catatan Workflow

- Setiap sesi kerja baru dimulai, baca file ini dulu untuk konteks.
- Setiap satu unit kerja selesai, update bagian ✅ SELESAI dan pindahkan
  item terkait dari 🔜 BELUM DIKERJAKAN.
- Commit ke GitHub butuh Personal Access Token baru tiap sesi (bukan token
  yang sama dipakai berulang) — demi keamanan.
