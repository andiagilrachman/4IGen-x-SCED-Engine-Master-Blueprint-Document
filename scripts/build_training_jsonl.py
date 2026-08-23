#!/usr/bin/env python3
"""
Konsolidasi SEMUA data di data/synthetic_dataset/*.json ke format JSONL
(messages: system/user/assistant) yang dipakai notebook training
(SCED_Engine_v0_1_Training.ipynb, Sel 6-7).

Sebelum script ini ada, 224 entri hasil scaling (batch2-batch7) TIDAK bisa
dipakai training karena belum dikonversi ke format messages -- yang
terpakai training masih file pilot lama 20 baris saja
(sced_pilot_train.jsonl).

Output: data/training_jsonl/sced_scaled_train_v1.jsonl (244 baris = 20
pilot asli + 224 hasil scaling), sced_pilot_train.jsonl TIDAK diubah/
ditimpa (tetap sebagai referensi historis v0.1).
"""
import json
import glob

SYSTEM_PROMPT = (
    "Kamu adalah SCED Engine, AI Finansial & Ekonomi di 4IGen.com. Tugasmu "
    "adalah memberikan analisis berdasarkan Data Schema Murni yang diberikan "
    "dengan metode Chain-of-Thought (CoT) 4 langkah. Dilarang mengarang "
    "angka di luar data input."
)

DISCLAIMER = (
    "\n\n---\n*Disclaimer: Analisis ini disajikan secara otomatis oleh SCED "
    "Engine di 4IGen.com untuk tujuan edukasi dan analisa, bukan merupakan "
    "nasihat atau rekomendasi investasi resmi. Keputusan investasi "
    "sepenuhnya ada di tangan pengguna.*"
)


def build_user_content(entry):
    asset_code = entry["asset_code"]
    lens = entry["lens"]
    instruction = entry["instruction"]
    input_data = dict(entry["input_data"])
    input_data.pop("metadata", None)  # metadata (nama/sektor/periode) tidak
    # disertakan di [INPUT DATA] -- konsisten dengan format pilot asli yang
    # hanya kirim financial_metrics + macro_context (data numerik murni)

    input_json = json.dumps(input_data, ensure_ascii=False)
    return (
        f"[LENSA]: {lens}\n[ASET]: {asset_code}\n[INSTRUCTION]: {instruction}"
        f"\n\n[INPUT DATA]: {input_json}"
    )


def build_assistant_content(entry):
    cot = entry["chain_of_thought"]
    return (
        f"### 1. Identifikasi Angka Kunci\n{cot['step_1_identification']}\n\n"
        f"### 2. Korelasi Antar Rasio\n{cot['step_2_correlation']}\n\n"
        f"### 3. Kontekstualisasi Makro\n{cot['step_3_macro_contextualization']}\n\n"
        f"### 4. Sintesis Risk & Reward\n{cot['step_4_synthesis']}"
        f"{DISCLAIMER}"
    )


def convert_entry(entry):
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_content(entry)},
            {"role": "assistant", "content": build_assistant_content(entry)},
        ]
    }


if __name__ == "__main__":
    all_entries = []
    files_processed = []
    for path in sorted(glob.glob("data/synthetic_dataset/*.json")):
        entries = json.load(open(path, encoding="utf-8"))
        all_entries.extend(entries)
        files_processed.append((path, len(entries)))

    output_path = "data/training_jsonl/sced_scaled_train_v1.jsonl"
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in all_entries:
            converted = convert_entry(entry)
            f.write(json.dumps(converted, ensure_ascii=False) + "\n")

    print(f"Berhasil konversi {len(all_entries)} entri -> {output_path}\n")
    print("Rincian per file sumber:")
    for path, n in files_processed:
        print(f"  {path}: {n} entri")
