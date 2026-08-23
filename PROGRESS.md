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

---

## 🔜 BELUM DIKERJAKAN (urutan prioritas)

### 4. Variasi data makro di dataset pilot
- **Masalah:** Semua 5 aset pilot (BBRI, ADRO, TLKM, GOLD, USD/IDR) pakai
  `bi_rate_percent: 6.00` dan `inflation_yoy_percent: 2.12` yang identik
  persis (semua per Q3-2024). Risiko: model "menghafal" angka makro sebagai
  konstanta, bukan belajar mengaitkan sensitivitas makro secara umum.
- **Perlu keputusan dari user:** apakah scaling data nanti akan
  mengambil periode historis berbeda (misal Q1-2023, Q2-2024, dst. dengan
  BI Rate/inflasi aktual periode itu), atau tetap 1 periode tapi variasi
  skenario makro dibuat sintetis (misal simulasi "seandainya BI Rate naik
  ke 7%")? Ini menentukan cara generate data selanjutnya.

### 5. Klarifikasi Model Guru (Teacher Model) API
- Belum diketahui: API/model apa yang dipakai user untuk generate dataset
  sintetis di `teacher_master_prompt.md` (GPT? Claude? Gemini? lokal?).
- Perlu dicek ToS provider tsb. soal penggunaan output untuk training model
  komersial pihak ketiga — beberapa provider melarang ini secara eksplisit.

### 6. Scaling dataset 20 → 500 Q&A
- Menambah 10–20 emiten IHSG baru + variasi periode/skenario makro (lihat
  poin 4) sebelum lanjut ke 500, lalu ke 10.000 sesuai roadmap Fase 5 di
  `BLUEPRINT.md`.
- Perlu jaga kualitas per-batch, bukan asal kuantitas — audit manual
  sampel tiap batch baru.

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
