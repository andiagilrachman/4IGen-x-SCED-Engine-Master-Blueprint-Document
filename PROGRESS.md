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

### 6. ⚠️ Scaling dataset 20 → 500 Q&A — BOTTLENECK DITEMUKAN, BUTUH INPUT USER
- **Percobaan (2026-08-23):** mulai generate data baru untuk 3 emiten baru
  (BMRI, UNVR, ANTM) via web search manual satu-per-satu untuk data
  fundamental riil (sesuai aturan Strict Fact Adherence — dilarang karang
  angka).
- **Temuan masalah skalabilitas:** untuk 1 emiten (BMRI) saja butuh 3x
  pencarian web dan beberapa rasio (NIM, CAR, PER, PBV presisi) tetap tidak
  didapat dengan kepastian tinggi — sumber berbeda-beda saling tidak
  konsisten (contoh: PER BMRI ada sumber bilang 7.1x, ada yang 9.14x,
  tergantung periode/basis estimasi). **Pola ini tidak scalable untuk
  500-10.000 data** — googling manual satu-satu per emiten akan makan waktu
  sangat lama dan berisiko data tidak konsisten antar sumber.
- **Proof-of-concept dibuat:** 1 sampel BMRI (lensa Value & Risk Margin) di
  `data/synthetic_dataset/bmri_synthetic_qa_PROOF_OF_CONCEPT.json` — dibuat
  HANYA dari metrik yang benar-benar terverifikasi (total_assets, net_income,
  ROE, NPL Gross, dividend yield), metrik yang tidak pasti (NIM/CAR/PER/PBV)
  SENGAJA tidak disertakan, dengan `_source_note` transparan.
- **PERTANYAAN KRITIS UNTUK USER (belum terjawab):** apakah user sudah
  punya database/API data fundamental saham terstruktur dari proyek lain
  (kemungkinan `stockdataengine.com` atau `4igen.com` — proyek user yang
  lain, tercatat di memori terpisah)? Kalau ada, itu jauh lebih tepat
  dipakai sebagai sumber data terstruktur untuk generate dataset SCED
  daripada riset manual satu-satu via web search.
- **UNVR dan ANTM belum dikerjakan** — menunggu keputusan sumber data dulu
  sebelum lanjut, supaya tidak buang waktu riset manual kalau ternyata ada
  cara lebih efisien.

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
