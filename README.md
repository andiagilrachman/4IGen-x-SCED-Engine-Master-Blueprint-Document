# 📘 BLUEPRINT.md
## 4IGen x SCED Engine — Master Blueprint Document
**Versi:** 1.0  
**Status:** Foundational Design  
**Domain Utama:** 4IGen.com  
**Nama Engine:** SCED (System Core Data Engine)

---

## 1. 🎯 VISI & MISI PROYEK

### 1.1 Visi
Membangun **Engine Penalaran Ekonomi & Finansial (Financial Reasoning Engine)** berbasis LLM lokal skala rumahan, yang mampu memberikan analisis multi-lensa (Saham, Forex, Makroekonomi) dengan integritas data 100% legal dan bebas hak cipta pihak ketiga.

### 1.2 Misi
1. Menyediakan analisis finansial objektif yang dapat menyesuaikan dengan **gaya berpikir pengguna** (bukan gaya pengembang).
2. Menjaga **legalitas dan keamanan hukum** untuk komersialisasi jangka panjang.
3. Beroperasi secara efisien di **hardware standar (PC rumahan)**, bukan di data center mahal.
4. Menghilangkan halusinasi angka dengan pendekatan **Fact-Based Synthetic Reasoning**.

---

## 2. 🏷️ IDENTITAS BRAND

| Elemen | Detail |
| :--- | :--- |
| **Platform Frontend** | 4IGen.com |
| **AI Engine** | SCED (System Core Data Engine) |
| **Tagline Konseptual** | *"Powered by SCED System Core Data Engine — Next-Gen Economic & Financial Reasoning."* |

### 2.1 Empat Pilar Identitas (4 Pillars of "I")
1. **INTEGRITY** — Data murni, legal, bebas sengketa hak cipta.
2. **INSIGHT** — Wawasan penalaran multi-lensa yang dalam.
3. **IMPARTIAL** — Netral, objektif, tidak memaksakan gaya investasi tertentu.
4. **INTELLIGENCE** — Kecerdasan penalaran sintetis tingkat tinggi (Chain-of-Thought).

---

## 3. ⚖️ PRINSIP LEGAL & ATURAN EMAS

### 3.1 Tiga Aturan Emas Sumber Data
1. **Zero-Narrative Scraping** — Sistem hanya mengambil fakta angka/tabel, tidak pernah menyimpan teks narasi berita, opini blog, atau riset sekuritas pihak lain.
2. **100% Owned Intellectual Property** — Seluruh dataset sintetis hasil generate adalah IP milik 4IGen sepenuhnya.
3. **Universal Data Standard** — Semua data (Saham IHSG, Forex, Komoditas) mengikuti satu standar format internal (JSON/Tabel).

### 3.2 Sistem Kategorisasi Legalitas Data (3 Label)
| Label | Deskripsi | Penggunaan |
| :--- | :--- | :--- |
| 🟢 **GREEN** | Fakta dari regulator, laporan emiten, dataset MIT/Apache 2.0, data sintetis milik sendiri. | Bebas untuk RAG, Fine-Tuning, & Redistribusi. |
| 🟡 **YELLOW** | Data fakta publik tanpa narasi hak cipta. | Boleh untuk RAG internal, tidak dijual mentah. |
| 🔴 **RED** | Artikel berita utuh, riset proprietary, data lisensi non-komersial. | Blokir otomatis dari pipeline. |

---

## 4. 🗂️ SUMBER DATA MURNI (WHITELIST)

### 4.1 Regulator & Pemerintah (Public Domain)
- Bank Indonesia (Suku Bunga, Kebijakan Moneter, LSSK)
- Otoritas Jasa Keuangan (OJK)
- Badan Pusat Statistik (BPS) — Inflasi, PDB, Ekspor-Impor
- FRED (Federal Reserve Economic Data) untuk konteks global
- SEC EDGAR untuk emiten Wall Street

### 4.2 Dokumen Publik Emiten
- Laporan Keuangan Kuartalan & Tahunan (angka murni)
- Prospektus IPO
- Materi Paparan Publik & Transkrip RUPS

### 4.3 Data Sintetis Buatan Sendiri
- Dataset Q&A ber-penalaran (Chain-of-Thought) hasil generate Model Guru dari fakta murni.

---

## 5. 🧬 ARSITEKTUR SISTEM SCED

### 5.1 Data Pipeline Flow
[ SUMBER DATA MURNI ]
│
▼
[ METRIC & FACT EXTRACTOR ] ── (Buang teks naratif)
│
▼
[ DATA SCHEMA UNIVERSAL (JSON/Tabel) ]
│
▼
[ MULTI-LENS SYNTHETIC GENERATOR ] ── (Model Guru via API)
├── Lensa A: Value & Risk
├── Lensa B: Growth & Expansion
├── Lensa C: Macro & Sektoral
└── Lensa D: Trader/Technical Structure
│
▼
[ DATASET EMAS (PROPRIETARY 10.000 CoT Q&A) ]
│
▼
[ FINE-TUNING MODEL LOKAL (LoRA/QLoRA) ]
│
▼
[ SCED ENGINE v1.0 ]
│
▼
[ 4IGEN.COM (Frontend User Interface) ]

text


### 5.2 Spesifikasi Model
- **Base Model:** Open-Weight 7B–8B parameter (kandidat: Llama-3 8B, Qwen 2.5 7B, Mistral 7B).
- **Metode Training:** Supervised Fine-Tuning (SFT) dengan teknik LoRA/QLoRA.
- **Target Hardware:** PC rumahan standar (RAM 16–32GB, GPU konsumen menengah opsional).
- **Kuantisasi:** Model dioptimasi ke format ringan agar bisa inferensi cepat di CPU/GPU biasa.

---

## 6. 📋 FORMAT DATA INPUT (DATA SCHEMA)

Setiap aset yang masuk ke SCED wajib mengikuti 3 Blok Data Standar:

### Blok 1 — Identitas & Kontekstual (Metadata)
- Kode Aset (contoh: `BBRI`, `USD/IDR`, `GOLD`)
- Pasar/Sektor
- Periode Data (Q3-2024 / Harian)
- Satuan Angka (IDR / % / Absolut)

### Blok 2 — Fundamental & Angka Kunci (Financial Metrics)
- Neraca: Aset, Utang, Ekuitas
- Laba/Rugi: Pendapatan, Laba Bersih, Operating Profit
- Rasio Kunci: ROE, PER, PBV, DER, NIM, NPL, Dividend Yield
- Pertumbuhan: YoY & QoQ (%)

### Blok 3 — Ekonomi Makro & Lingkungan Pasar
- Suku Bunga Regulator (BI Rate / Fed Rate)
- Inflasi Lokal & Global
- Nilai Tukar Utama (USD/IDR, EUR/USD)
- Harga Komoditas Relevan (CPO, Batu Bara, Emas, Minyak)

---

## 7. 🧪 ATURAN PEMBUATAN DATA SINTETIS (RULES OF GENERATION)

Instruksi wajib untuk Model Guru (Teacher Model):

### Aturan 1 — Strict Fact Adherence
Dilarang mengubah, membulatkan, atau mengarang angka di luar Data Schema Input.

### Aturan 2 — Mandatory Chain-of-Thought (4 Langkah)
1. **Identifikasi** — Sebutkan angka kunci.
2. **Korelasikan** — Hubungkan antar rasio.
3. **Kontekstualisasi Makro** — Kaitkan dengan kondisi ekonomi.
4. **Sintesis Risk/Reward** — Kesimpulan objektif & berimbang.

### Aturan 3 — Multi-Lens Mandate
Dari 1 Data Schema, buat variasi Q&A sesuai Lensa: Value, Growth, Macro, Risk, Technical.

### Aturan 4 — Clean Legal Output
Narasi bersifat akademis/analitis, bebas dari kutipan atau gaya bahasa media/sekuritas pihak lain.

---

## 8. 💡 MATRIKS KOMPOSISI DATASET (10.000 DATA)

| Modul Kemampuan | Porsi | Jumlah Data |
| :--- | :--- | :--- |
| Penalaran Laporan Keuangan (Fundamental) | 35% | ~3.500 |
| Ekonomi Makro & Kebijakan Moneter | 25% | ~2.500 |
| Aksi Korporasi & Struktur Pasar | 20% | ~2.000 |
| Integrasi Lintas Sektor (Intermarket) | 10% | ~1.000 |
| Metodologi Analisis Sesuai Permintaan | 10% | ~1.000 |

---

## 9. 🖥️ INTERAKSI PENGGUNA DI 4IGEN.COM

### 9.1 Alur "2-Step Selection System"
Langkah 1: PILIH ASET
└── User memasukkan kode saham/forex (contoh: "BBCA", "USD/IDR")

Langkah 2: PILIH LENSA ANALISIS (PRESET)
├── 🔘 Value & Margin of Safety
├── 🔘 Growth & Business Expansion
├── 🔘 Macro & Interest Rate Sensitivity
├── 🔘 Risk & Red Flags Detector
└── 🔘 Custom Prompt (untuk user advanced)

Langkah 3: OUTPUT SCED ENGINE
└── Laporan analisis multi-langkah dalam hitungan detik.

text


### 9.2 Format Standar Output
Setiap output SCED wajib mengandung:
1. Header: `[4IGen - SCED Engine Analysis]`
2. Temuan Kunci (Angka Fakta)
3. Penalaran Chain-of-Thought
4. Kesimpulan Impartial (Risk & Reward berimbang)
5. Disclaimer: *"Analisis ini bukan nasihat keuangan. Keputusan investasi ada di tangan pengguna."*

---

## 10. 🚀 ROADMAP PELATIHAN AWAL (5 FASE)

### FASE 1 — Pemilihan Base Model
- Uji kandidat model 7B–8B open-weight.
- Pilih yang paling kuat dalam penalaran numerik & bahasa Indonesia.

### FASE 2 — Pembuatan Dataset Pilot (100–500 Q&A)
- Kumpulkan fakta dari 5 aset pilot.
- Generate melalui Model Guru dengan aturan Chain-of-Thought.
- Audit manual kualitas hasil.

### FASE 3 — Training Efisien (LoRA/QLoRA)
- Freeze parameter utama, latih hanya adaptor kecil.
- Estimasi waktu: 1–3 jam di PC standar.

### FASE 4 — Evaluasi Kelulusan
- Uji halusinasi angka.
- Uji konsistensi fleksibilitas lensa.
- Uji gaya bahasa profesional & objektif.

### FASE 5 — Scaling Massal (10.000 Data)
- Perluas ke 100–200 emiten + data makro 5 tahun.
- Training final untuk menghasilkan **SCED Engine v1.0 Proprietary**.

---

## 11. 🧩 ASET PILOT AWAL

| Aset | Kategori | Fungsi Uji |
| :--- | :--- | :--- |
| BBRI / BBCA | Saham Perbankan | Penalaran kredit & suku bunga |
| ADRO / PGAS | Saham Energi/Komoditas | Korelasi komoditas global |
| TLKM / ICBP | Saham Consumer/Telko | Pertumbuhan & daya beli |
| USD/IDR | Forex | Penalaran makro & nilai tukar |
| GOLD | Komoditas | Penalaran risk-on/risk-off |

---

## 12. 📊 KRITERIA SUKSES PROYEK

Sebuah versi SCED Engine dianggap "Lulus" jika memenuhi kriteria berikut:
1. ✅ Akurasi angka 100% (tanpa halusinasi numerik).
2. ✅ Fleksibel mengubah lensa analisis sesuai preset user.
3. ✅ Gaya bahasa profesional, objektif, tidak menggurui.
4. ✅ Waktu inferensi wajar (< 30 detik untuk analisis lengkap di PC standar).
5. ✅ Semua data & output 100% legal untuk komersialisasi.

---

## 13. ⚠️ BATASAN & DISCLAIMER PROYEK

1. SCED Engine **bukan** bot pemberi sinyal beli/jual otomatis.
2. SCED Engine **tidak** memberikan price target absolut.
3. SCED Engine adalah **asisten analis**, bukan pengganti keputusan manusia.
4. Setiap output wajib menyertakan disclaimer bahwa ini **bukan nasihat keuangan resmi**.

---

## 14. 📅 STATUS DOKUMEN

| Tanggal | Versi | Status |
| :--- | :--- | :--- |
| 2025-08-23 | 1.0 | Foundational Design — Disetujui bersama |

---

**Dokumen ini adalah acuan utama proyek. Setiap perubahan konsep wajib melalui revisi resmi BLUEPRINT.md sebelum diimplementasikan.**
