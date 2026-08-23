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

### 6d. ✅ Perluasan dataset: 3 lensa + 33 saham baru + data historis (2026-08-23)
Total dataset sekarang **77 entri** (naik dari 20 di awal sesi). Rincian
kerja tambahan:

- **3 lensa tambahan untuk 4 saham existing** (`scripts/generate_batch2_3lenses.py`
  → `batch2_fundamental_db_3lenses.json`, 12 entri): Growth & Business
  Expansion, Macro & Interest Rate Sensitivity, Risk & Red Flags Detector
  untuk BMRI/UNVR/ANTM/ASII. **Catatan penting:** field growth
  rate/margin/current-quick ratio/dividend_yield/bvps NULL untuk 4 saham
  ini di sumber data — lensa Growth/Macro/Risk disesuaikan memakai HANYA
  field yang benar-benar terisi (ROE/ROA/DER/PER/PBV/EPS/Altman
  Z/Piotroski F/Graham Number), bukan dipaksakan sesuai template asli
  `teacher_master_prompt.md` yang minta NIM/growth YoY (Strict Fact
  Adherence tetap dijaga, bukan dilanggar demi ikut template).
- **33 saham baru dari 11 sektor** (`batch3_expanded_33stocks_value_risk.json`,
  33 entri, lensa Value & Risk Margin) — dipilih dari `fundamental_snapshot_all.json`
  (1.203 saham) dengan kriteria: top 3 `fundamental_score` per sektor
  (proksi kelengkapan/kualitas data), skip warrant/right (`-W`/`-R`), skip
  saham yang sudah dipakai sebelumnya. Sektor: Energi, Barang Konsumen
  Primer/Non-Primer, Keuangan, Infrastruktur, Properti, Barang Baku,
  Transportasi, Perindustrian, Teknologi, Kesehatan.
- **Data historis dari `financial_rows`** (`batch4_historical_financial_rows.json`,
  8 entri) — BBCA/BBNI/BDMN/BNGA, FY2023 & FY2024, lensa Growth & Business
  Expansion. Ditemukan: data BS/IS di `financial_rows` formatnya **Tahunan
  (FY)**, bukan kuartalan seperti dugaan awal. FY2023 dipasangkan anchor
  makro Desember 2023, FY2024 dipasangkan anchor Q3 2024 (pendekatan
  wajar karena rezim BI Rate 6.00% sama sepanjang kedua periode).
  **Penting:** `financial_rows` HANYA mencakup 101 saham sektor Keuangan
  (semua kategori IDXFINANCE) — tidak bisa dipakai untuk sektor lain.
  ROE di batch ini dihitung langsung dari fakta (Net Income/Equity),
  bukan diambil dari sumber lain.
- Semua script disimpan di `scripts/` (reusable untuk scaling lanjutan):
  `extract_fundamental_data.py`, `generate_batch2.py`,
  `generate_batch2_3lenses.py`.

### 6f. ✅ Audit kualitas + 33 saham dilengkapi ke 4 lensa penuh (2026-08-23)
Total dataset sekarang **176 entri** (naik dari 77 di akhir sesi
sebelumnya).

- **Audit otomatis kualitas dataset** (5 sampel acak + cek semua 77 entri
  yang ada saat itu): script cek apakah semua angka di narasi CoT bisa
  dilacak balik ke `input_data` (deteksi kemungkinan karangan angka).
  Hasil: awalnya 102 "potensi tidak match" ternyata SEMUA false-positive
  dari bug regex audit sendiri (tidak menangkap tanda minus pada angka
  negatif) — setelah dicek manual, tidak ada fabrikasi data. Angka di CoT
  konsisten dengan `input_data`.
- **Temuan kualitas nyata (bukan fabrikasi, tapi soal nada narasi):** 2
  dari 33 saham (ACST, PGJO) punya rasio ekstrem negatif (PER/PBV negatif,
  Altman Z sangat negatif, Piotroski F terendah — indikasi kemungkinan
  ekuitas negatif/kondisi keuangan sangat bermasalah), tapi generator versi
  lama tetap pakai nada penutup CoT yang generik/netral sama seperti saham
  sehat. **Diperbaiki**: `generate_batch5_33stocks_3lenses.py` sekarang
  punya fungsi `severity_note()` yang mendeteksi kondisi ekstrem dan
  menyesuaikan nada step_4 (Growth) dan opening_tone step_4 (Risk) supaya
  lebih tegas memperingatkan, bukan generik.
- **33 saham dilengkapi ke 4 lensa penuh** (`batch5_33stocks_3lenses.json`,
  99 entri: 3 lensa baru × 33 saham) — Growth & Business Expansion, Macro &
  Interest Rate Sensitivity, Risk & Red Flags Detector. Digabung dengan
  `batch3_expanded_33stocks_value_risk.json` (lensa Value & Risk Margin
  yang sudah ada), sekarang 33 saham ini punya cakupan 4 lensa lengkap.
- Script tersimpan di `scripts/generate_batch5_33stocks_3lenses.py`
  (reusable, butuh `fundamental_snapshot_all.json` &
  `selected_stocks_batch3.json` sebagai input — file kerja lokal, tidak
  di-commit).

### 6h. ✅ Fix bug narasi + audit manual + 15 institusi keuangan baru (2026-08-23)
Total dataset sekarang **206 entri** (naik dari 176 di akhir sesi
sebelumnya).

- **Cek kondisi ekstrem 4 saham batch2** (BMRI/UNVR/ANTM/ASII): semua
  normal (tidak ada PER/PBV/Altman Z negatif) — tidak perlu perbaikan,
  narasi generik yang sudah ada sudah sesuai.
- **Bug ditemukan & diperbaiki** di `generate_batch5_33stocks_3lenses.py`:
  kalimat step_2 lensa Risk selalu bilang "PBV yang negatif (jika ada)
  umumnya mengindikasikan ekuitas negatif" TANPA CEK apakah PBV memang
  negatif — untuk saham normal (PBV positif) kalimat ini jadi tidak
  relevan/membingungkan. Diperbaiki jadi kondisional: kalau PBV negatif ->
  jelaskan implikasinya; kalau PBV positif -> jelaskan itu wajar, bukan
  masalah. Script sudah dijalankan ulang, `batch5_33stocks_3lenses.json`
  ter-update dengan perbaikan ini (masih 99 entri, isi diperbaiki).
- **Audit manual** (baca langsung 5 sampel dari berbagai batch, bukan cuma
  cek angka otomatis): semua bersih — angka konsisten, narasi masuk akal,
  tidak ada frasa aneh lain ditemukan setelah fix bug PBV di atas.
- **15 institusi keuangan baru dari `financial_rows`**
  (`batch6_15finance_historical.json`, 30 entri: 15 institusi x FY2023 &
  FY2024) — ADMF, ASDM, BBTN, BFIN, BJBR, BNLI, BRIS, BTPS, LPGI, MEGA,
  NISP, PANS, PNBN, SRTG, TUGU. Cakupan beragam: bank umum, bank syariah
  (BRIS/BTPS), multifinance (ADMF/BFIN), asuransi (ASDM/LPGI/TUGU),
  sekuritas (PANS), holding investasi (SRTG). Beberapa entri (sekuritas/
  asuransi) tidak selalu punya field "Pendapatan bunga" — script
  `generate_batch6_15finance.py` menangani ini secara kondisional (field
  di-skip kalau tidak ada, bukan diisi 0/dikarang).
  **Total bank/institusi keuangan dari financial_rows sekarang: 19 dari
  101 yang tersedia** (4 dari batch4 + 15 dari batch6).

### 6j. ✅ Lensa Risk & Macro untuk 19 institusi keuangan pakai YoY riil (2026-08-23)
Total dataset sekarang **244 entri** (naik dari 206).

- Manfaatkan data 2 tahun (FY2023 & FY2024) yang sudah tersedia untuk 19
  institusi keuangan (4 dari batch4 + 15 dari batch6) untuk hitung
  **pertumbuhan YoY sungguhan** dari fakta neraca — bukan snapshot 1 titik
  waktu seperti kebanyakan data lain di dataset ini.
- `batch7_19finance_risk_macro.json` (38 entri: 19 institusi x 2 lensa):
  - **Risk & Red Flags Detector**: bandingkan Total Aset/Ekuitas/Laba
    Bersih FY2023 vs FY2024, hitung growth % riil + ROE tiap tahun. Narasi
    kondisional: kalau laba bersih turun YoY -> nada waspada + saran
    investigasi lanjutan (bukan asal klaim penyebab); kalau naik -> nada
    positif tapi tetap ingatkan cek kualitas pertumbuhan.
  - **Macro & Interest Rate Sensitivity**: rasio Aset/Ekuitas (proksi
    leverage) FY2024 dikaitkan dengan sensitivitas suku bunga.
  - **Temuan menarik**: 10 dari 19 institusi mengalami penurunan laba
    bersih YoY riil (contoh: ADMF -27.64%), padahal aset/ekuitas tetap
    tumbuh — insight yang tidak mungkin didapat dari data snapshot 1
    waktu saja.
  - Semua rasio growth/ROE DIHITUNG LANGSUNG dari fakta (Net Income/
    Equity, YoY %), bukan diambil dari sumber lain manapun.

### 6l. ✅ KRUSIAL: Konsolidasi 244 entri ke format JSONL training (2026-08-23)
**Temuan penting sebelum tugas ini:** 224 entri hasil scaling (batch2 s/d
batch7) TERNYATA belum pernah dikonversi ke format `messages` (system/
user/assistant) yang benar-benar dipakai notebook training — yang
terpakai training selama ini masih file pilot lama 20 baris saja
(`sced_pilot_train.jsonl`). Semua kerja scaling sebelumnya tersimpan rapi
di `data/synthetic_dataset/` tapi belum "tersambung" ke pipeline training.
Ini sudah diperbaiki:

- **`scripts/build_training_jsonl.py`**: baca SEMUA file di
  `data/synthetic_dataset/*.json`, konversi tiap entri ke format
  `messages` (system prompt tetap sama seperti pilot asli, user content =
  `[LENSA]/[ASET]/[INSTRUCTION]/[INPUT DATA]` dengan `metadata` di-strip
  dari input_data biar konsisten dengan format pilot, assistant content =
  4 section CoT + disclaimer baku).
- **Output: `data/training_jsonl/sced_scaled_train_v1.jsonl`** — 244 baris,
  semua tervalidasi strukturnya benar. `sced_pilot_train.jsonl` (20 baris)
  TIDAK dihapus/ditimpa, tetap ada sebagai referensi historis v0.1.
- **Notebook `SCED_Engine_v0_1_Training.ipynb` Sel 6 di-update**:
  `DATASET_PATH` sekarang menunjuk ke `sced_scaled_train_v1.jsonl`, bukan
  file pilot lama.
- **Verifikasi token length**: maksimum ~779 token estimasi (dari 244
  sampel), masih aman jauh di bawah `max_seq_length=2048` — tidak perlu
  ubah konfigurasi training.
- **Status sekarang: pipeline training benar-benar siap dipakai dengan
  244 entri**, bukan cuma 20 seperti sebelumnya.

### 6n. ✅ 50 saham baru 4 lensa penuh + fix bug PBV=0 + rebuild JSONL (2026-08-23)
Total dataset sekarang **444 entri** (naik dari 244, lebih dari 22x lipat
dari pilot awal 20 entri).

- **50 saham baru dari 10 sektor** (`batch8_50stocks_4lenses.json`, 200
  entri: 50 saham x 4 lensa langsung sekaligus) — dipilih rank ke-4 s/d
  ke-8 `fundamental_score` per sektor (skip 3 teratas yang sudah dipakai
  di batch3/5), dari `fundamental_snapshot_all.json` (1.203 saham
  tersedia). Cakupan saham sekarang: 87 saham unik (37 dari batch3/5 +
  50 baru) + 19 institusi keuangan dari `financial_rows`.
- **Bug baru ditemukan & diperbaiki**: kondisi `pbv < 0` di lensa Risk
  tidak menangkap kasus **PBV = 0 persis** (2 saham: BATA, HEXA) — nilai
  0 salah diklaim "wajar (positif)" padahal PBV 0.0000x lebih mungkin
  anomali data / nilai buku mendekati nol yang perlu diverifikasi, bukan
  otomatis dianggap sehat. Diperbaiki di `generate_batch8_50stocks_4lenses.py`
  DAN `generate_batch5_33stocks_3lenses.py` (jaga-jaga run ulang di masa
  depan, meski batch5 kebetulan tidak ada kasus ini saat ini) — sekarang
  3 cabang kondisi: negatif / nol / positif wajar.
- **6 dari 50 saham baru kondisi ekstrem** (INPS, BATA, ABBA, SAFE, CMPP,
  ENVY) — otomatis tertangani nada narasinya lewat `severity_note()` yang
  sudah ada.
- **JSONL training di-rebuild**: `sced_scaled_train_v1.jsonl` sekarang 444
  baris (dari `scripts/build_training_jsonl.py`, dijalankan ulang setelah
  ada data baru — SELALU JALANKAN INI TIAP ADA BATCH DATA BARU).
  Token length masih aman (maksimum ~779 token estimasi, jauh di bawah
  `max_seq_length=2048`).

### 6o. Langkah selanjutnya
- **Dataset sudah 444 entri — SANGAT layak untuk smoke test training di
  Colab sekarang.** Ini rekomendasi utama untuk sesi berikutnya: jalankan
  `notebooks/SCED_Engine_v0_1_Training.ipynb` (10 sel) di Google Colab,
  laporkan hasilnya (berhasil/error, kualitas output model).
- Kalau mau scaling lebih lanjut dulu sebelum training: masih ada ~1.116
  saham belum dipakai dari `fundamental_snapshot_all.json`, dan 82
  institusi keuangan belum dipakai dari `financial_rows`.
- Tetap tunda data eksplisit Invezgo sampai ToS dikonfirmasi (poin 6b).
- **Pengingat penting**: `scripts/build_training_jsonl.py` HARUS
  dijalankan ulang setiap kali ada file baru di `data/synthetic_dataset/`
  — proses ini TIDAK otomatis.

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
- **Folder lokal user:** `C:\4IGen-x-SCED-Engine` (Windows) — sudah
  di-clone dari repo ini (2026-08-23). Sinkronisasi rutin pakai
  `git pull origin main` di folder itu, BUKAN clone ulang.
