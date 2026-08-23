# 📘 README_training_guide.md
## SCED Engine v0.1 — Google Colab Training Guide
**Proyek:** 4IGen x SCED Engine  
**Metode:** Smart Hybrid (Train di Colab → Inferensi di PC Rumah)  
**Base Model:** Qwen 2.5 7B Instruct  
**Teknik:** QLoRA (4-bit) + Supervised Fine-Tuning (SFT)  
**Dataset Pilot:** `data/training_jsonl/sced_pilot_train.jsonl` (20 baris)  
**Soal Ujian:** `eval/icbp_test_schema.json`

---

## 1. Tujuan Dokumen Ini

Dokumen ini adalah panduan operasional untuk melatih **SCED Engine v0.1** tanpa membebani PC rumah.

### Prinsip Smart Hybrid
| Tahap | Di Mana | Hardware |
| :--- | :--- | :--- |
| Siapkan data & blueprint | PC Rumah + GitHub | Lokal |
| Fine-tuning model | Google Colab | GPU T4 16GB (gratis) |
| Simpan adapter hasil latih | GitHub / PC Rumah | File ~100–300 MB |
| Jalankan analisis harian | PC Rumah | CPU i5 + RAM 16GB |

> **Catatan hardware proyek ini:**  
> PC lokal memakai AMD Radeon R7 (VRAM 4GB) → **tidak dipakai untuk training**.  
> Training wajib di Colab (NVIDIA T4).  
> Inferensi harian tetap 100% lokal di PC rumah.

---

## 2. Prasyarat Sebelum Training

Pastikan semua ini sudah ada di repositori GitHub:

- [x] `BLUEPRINT.md`
- [x] `data/training_jsonl/sced_pilot_train.jsonl`
- [x] `data/synthetic_dataset/*.json` (arsip mentah, jangan dihapus)
- [x] `eval/icbp_test_schema.json`
- [x] `prompts/teacher_master_prompt.md`

### Akun yang Dibutuhkan
1. Akun Google (untuk Google Colab)
2. Akun Hugging Face (opsional, untuk unduh model lebih stabil)
3. Akses repositori GitHub proyek (private/public sesuai pengaturanmu)

---

## 3. Arsitektur Training v0.1

```text
[GitHub Repo]
   └── sced_pilot_train.jsonl
            │
            ▼
[Google Colab + GPU T4]
   1. Clone repo
   2. Load Qwen 2.5 7B Instruct (4-bit)
   3. Pasang LoRA Adapter
   4. SFT selama 3–4 epoch
   5. Uji dengan ICBP (unseen)
   6. Export adapter
            │
            ▼
[Output]
   models/sced_adapter_v0.1/
   ├── adapter_config.json
   ├── adapter_model.safetensors   (~100–300MB)
   └── README_adapter.md
            │
            ▼
[PC Rumah]
   Gabungkan adapter + base model
   untuk inferensi lokal (Ollama / LM Studio / llama.cpp)
