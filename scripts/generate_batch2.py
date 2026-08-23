#!/usr/bin/env python3
"""
Generate dataset sintetis SCED Engine dari data fundamental yang sudah diekstrak
(fundamental_snapshot_all.json) + anchor makro Agustus 2026 (data terkini).

Mengikuti aturan teacher_master_prompt.md:
- Strict Fact Adherence (hanya angka dari data)
- Chain-of-Thought 4 langkah
- Lensa: Value & Risk Margin (mulai dari 1 lensa dulu untuk batch ini)
"""
import json

with open("/home/claude/fundamental_snapshot_all.json") as f:
    snapshot = json.load(f)

MACRO_ANCHOR = {
    "bi_rate_percent": 4.75,
    "inflation_yoy_percent": 4.76,
    "usd_idr_exchange_rate": 16985,
    "economic_growth_gdp_percent": 5.12,
    "sector_trend": "BI Rate turun kumulatif 150 bps sejak September 2024 ke level terendah sejak Oktober 2022, tapi inflasi kembali naik mendekati batas atas target BI"
}
PERIOD_LABEL = "Agustus 2026 (snapshot terkini)"

TARGET_CODES = ["BMRI", "UNVR", "ANTM", "ASII"]  # ICBP sengaja dilewati (reserved unseen eval data)

def build_value_risk_entry(code, data):
    d = data
    def fmt(v, suffix=""):
        return f"{v:.4f}{suffix}" if v is not None else "tidak tersedia"

    input_data = {
        "metadata": {
            "asset_code": code,
            "asset_name": d["company_name"],
            "sector": "Lihat data 4igen (tidak disertakan di sample ini)",
            "period": PERIOD_LABEL,
            "currency": "IDR",
            "scale": "Rasio & per-lembar saham"
        },
        "financial_metrics": {k: v for k, v in {
            "roe_percent": d["roe_percent"],
            "roa_percent": d["roa_percent"],
            "der_x": d["der_x"],
            "per_x": d["per_x"],
            "pbv_x": d["pbv_x"],
            "eps": d["eps"],
            "altman_z_score": d["altman_z_score"],
            "piotroski_f_score": d["piotroski_f_score"],
            "graham_number": d["graham_number"],
        }.items() if v is not None},
        "macro_context": MACRO_ANCHOR
    }

    entry = {
        "asset_code": code,
        "lens": "Value & Risk Margin",
        "instruction": f"Sebagai investor yang mengutamakan proteksi modal dan margin keselamatan (margin of safety), bagaimana Anda menilai profil valuasi dan risiko {code} berdasarkan data rasio terkini?",
        "input_data": input_data,
        "chain_of_thought": {
            "step_1_identification": f"Indikator kunci {code} mencakup PER sebesar {fmt(d['per_x'], 'x')}, PBV sebesar {fmt(d['pbv_x'], 'x')}, dan EPS sebesar {fmt(d['eps'])}. ROE tercatat {fmt(d['roe_percent'], '%')} dan ROA {fmt(d['roa_percent'], '%')}.",
            "step_2_correlation": f"Rasio DER sebesar {fmt(d['der_x'], 'x')} menunjukkan struktur permodalan perusahaan terhadap ekuitas. Altman Z-Score sebesar {fmt(d['altman_z_score'])} memberi indikasi tingkat kesehatan keuangan (semakin tinggi umumnya semakin sehat), sementara Piotroski F-Score {fmt(d['piotroski_f_score'])} (skala 0-9) mengukur kekuatan fundamental berdasarkan 9 kriteria.",
            "step_3_macro_contextualization": f"Di tengah BI Rate {MACRO_ANCHOR['bi_rate_percent']}% dan inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% (periode {PERIOD_LABEL}), valuasi PER {fmt(d['per_x'], 'x')} perlu dibandingkan dengan biaya modal yang berlaku saat ini.",
            "step_4_synthesis": f"Graham Number (estimasi nilai wajar berbasis EPS & BVPS) tercatat {fmt(d['graham_number'])}, memberi salah satu acuan margin keselamatan bagi investor value. Kombinasi Altman Z-Score dan Piotroski F-Score membantu menilai risiko kebangkrutan dan kekuatan fundamental secara lebih menyeluruh sebelum mengambil keputusan."
        },
        "_source_note": f"Data rasio dari indicator_snapshot_fundamental (database aigen_db user, snapshot {d['snapshot_date']}), field vendor_insight_score SENGAJA TIDAK diikutkan (proprietary vendor). Field yang bernilai NULL di sumber data (bvps, dividend_yield, growth rates, margins, current/quick ratio) tidak disertakan di input_data."
    }
    return entry

results = []
for code in TARGET_CODES:
    if code in snapshot:
        results.append(build_value_risk_entry(code, snapshot[code]))
    else:
        print(f"SKIP {code}: tidak ditemukan di snapshot")

output_path = "/home/claude/repo/data/synthetic_dataset/batch2_fundamental_db_value_risk.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Berhasil generate {len(results)} entri -> {output_path}")
for r in results:
    print(f"  - {r['asset_code']}")
