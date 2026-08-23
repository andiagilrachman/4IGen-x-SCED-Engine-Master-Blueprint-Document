#!/usr/bin/env python3
"""
Generate 3 lensa tambahan (Growth, Macro & Interest Rate Sensitivity, Risk &
Red Flags Detector) untuk 4 saham (BMRI/UNVR/ANTM/ASII) yang lensa
"Value & Risk Margin"-nya sudah dibuat di batch2_fundamental_db_value_risk.json.

CATATAN PENTING: field revenue_growth_yoy, net_income_growth_yoy,
net_profit_margin, gross_profit_margin, current_ratio, quick_ratio,
dividend_yield, bvps SEMUA NULL untuk 4 saham ini di sumber data
(indicator_snapshot_fundamental). Sesuai Strict Fact Adherence, lensa
di bawah ini disesuaikan memakai HANYA field yang benar-benar terisi:
ROE, ROA, DER, PER, PBV, EPS, Altman Z-Score, Piotroski F-Score,
Graham Number, fundamental_score.
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
TARGET_CODES = ["BMRI", "UNVR", "ANTM", "ASII"]
SOURCE_NOTE = ("Data rasio dari indicator_snapshot_fundamental (database aigen_db user, "
               "snapshot {date}). vendor_insight_score proprietary SENGAJA TIDAK diikutkan. "
               "Field revenue_growth_yoy/net_income_growth_yoy/margin/current_ratio/quick_ratio/"
               "dividend_yield/bvps NULL di sumber data untuk saham ini sehingga TIDAK dipakai "
               "(Strict Fact Adherence) — lensa memakai field yang tersedia saja "
               "(ROE/ROA/DER/PER/PBV/EPS/Altman Z/Piotroski F/Graham Number/fundamental_score).")


def fmt(v, suffix=""):
    return f"{v:.4f}{suffix}" if v is not None else "tidak tersedia di data"


def base_input_data(code, d):
    return {
        "metadata": {
            "asset_code": code,
            "asset_name": d["company_name"],
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
            "fundamental_score": d["fundamental_score"],
        }.items() if v is not None},
        "macro_context": MACRO_ANCHOR
    }


def build_growth_entry(code, d):
    return {
        "asset_code": code,
        "lens": "Growth & Business Expansion",
        "instruction": f"Bagaimana efisiensi profitabilitas {code} jika ditinjau dari kemampuannya menghasilkan imbal balik atas ekuitas dan aset, mengingat data pertumbuhan pendapatan/laba periode ini tidak tersedia?",
        "input_data": base_input_data(code, d),
        "chain_of_thought": {
            "step_1_identification": f"Indikator efisiensi profitabilitas {code} yang tersedia mencakup ROE sebesar {fmt(d['roe_percent'], '%')} dan ROA sebesar {fmt(d['roa_percent'], '%')}, dengan EPS {fmt(d['eps'])} dan fundamental_score komposit {fmt(d['fundamental_score'])}.",
            "step_2_correlation": f"ROE {fmt(d['roe_percent'], '%')} dibandingkan ROA {fmt(d['roa_percent'], '%')} memberi gambaran seberapa besar leverage (utang) berkontribusi pada imbal hasil ekuitas — semakin lebar selisih keduanya (dengan DER {fmt(d['der_x'], 'x')}), semakin besar peran leverage dalam mendongkrak ROE dibanding murni efisiensi aset.",
            "step_3_macro_contextualization": f"Di tengah BI Rate {MACRO_ANCHOR['bi_rate_percent']}% dan inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% (periode {PERIOD_LABEL}), tingkat ROA {fmt(d['roa_percent'], '%')} perlu dibandingkan dengan biaya modal yang berlaku untuk menilai apakah profitabilitas aset masih mengungguli biaya dana.",
            "step_4_synthesis": f"Catatan penting: data pertumbuhan pendapatan/laba YoY tidak tersedia dalam Data Schema periode ini, sehingga analisis ini terbatas pada snapshot efisiensi (ROE {fmt(d['roe_percent'], '%')}, ROA {fmt(d['roa_percent'], '%')}) tanpa bisa menyimpulkan tren pertumbuhan bisnis secara historis."
        },
        "_source_note": SOURCE_NOTE.format(date=d["snapshot_date"])
    }


def build_macro_entry(code, d):
    return {
        "asset_code": code,
        "lens": "Macro & Interest Rate Sensitivity",
        "instruction": f"Sejauh mana struktur permodalan {code} membuatnya rentan atau tahan terhadap dinamika suku bunga BI Rate saat ini?",
        "input_data": base_input_data(code, d),
        "chain_of_thought": {
            "step_1_identification": f"Variabel makro periode ini: BI Rate {MACRO_ANCHOR['bi_rate_percent']}%, Inflasi YoY {MACRO_ANCHOR['inflation_yoy_percent']}%, GDP Growth {MACRO_ANCHOR['economic_growth_gdp_percent']}%. Dari sisi emiten, DER {code} tercatat {fmt(d['der_x'], 'x')} dengan ROA {fmt(d['roa_percent'], '%')}.",
            "step_2_correlation": f"DER {fmt(d['der_x'], 'x')} menunjukkan proporsi utang terhadap ekuitas — semakin tinggi rasio ini, semakin sensitif beban bunga perusahaan terhadap perubahan BI Rate. ROA {fmt(d['roa_percent'], '%')} mengindikasikan kemampuan aset menghasilkan laba yang bisa menutup beban bunga tersebut.",
            "step_3_macro_contextualization": f"BI Rate saat ini {MACRO_ANCHOR['bi_rate_percent']}% berada dalam tren penurunan kumulatif, namun inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% yang naik mendekati batas atas target bisa membatasi ruang pemangkasan suku bunga lebih lanjut oleh BI — situasi ini relevan bagi emiten dengan DER {fmt(d['der_x'], 'x')} karena memengaruhi proyeksi beban bunga ke depan.",
            "step_4_synthesis": f"Dengan DER {fmt(d['der_x'], 'x')} dan ROA {fmt(d['roa_percent'], '%')}, sensitivitas {code} terhadap perubahan suku bunga bergantung pada seberapa besar porsi utang berbunga mengambang dalam struktur modalnya — data ini tidak merinci komposisi tersebut, sehingga kesimpulan bersifat indikatif berdasarkan rasio agregat saja."
        },
        "_source_note": SOURCE_NOTE.format(date=d["snapshot_date"])
    }


def build_risk_entry(code, d):
    return {
        "asset_code": code,
        "lens": "Risk & Red Flags Detector",
        "instruction": f"Potensi risiko atau kerentanan apa yang dapat diidentifikasi dari profil kesehatan keuangan {code} berdasarkan skor-skor analitis yang tersedia?",
        "input_data": base_input_data(code, d),
        "chain_of_thought": {
            "step_1_identification": f"Titik perhatian risiko mencakup Altman Z-Score sebesar {fmt(d['altman_z_score'])}, Piotroski F-Score {fmt(d['piotroski_f_score'])} (skala 0-9), dan DER {fmt(d['der_x'], 'x')}.",
            "step_2_correlation": f"Altman Z-Score {fmt(d['altman_z_score'])} adalah indikator prediksi risiko kebangkrutan (umumnya makin rendah/negatif, makin berisiko, meski ambang batas berbeda antar sektor terutama untuk sektor keuangan). Piotroski F-Score {fmt(d['piotroski_f_score'])} merangkum 9 kriteria kesehatan fundamental — skor rendah (mendekati 0) mengindikasikan lebih banyak sinyal negatif dibanding skor tinggi (mendekati 9).",
            "step_3_macro_contextualization": f"Dalam kondisi inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% yang naik mendekati batas atas target BI, perusahaan dengan DER tinggi seperti {fmt(d['der_x'], 'x')} berpotensi menghadapi tekanan tambahan pada beban bunga jika BI menahan atau membalik arah kebijakan penurunan suku bunga.",
            "step_4_synthesis": f"Kombinasi Altman Z-Score {fmt(d['altman_z_score'])} dan Piotroski F-Score {fmt(d['piotroski_f_score'])} memberi dua sudut pandang berbeda (risiko kebangkrutan vs kekuatan fundamental) yang perlu dibaca bersama, bukan terpisah — perbedaan hasil antar kedua skor (jika ada) justru menandakan area yang perlu didalami lebih lanjut, bukan otomatis red flag."
        },
        "_source_note": SOURCE_NOTE.format(date=d["snapshot_date"])
    }


results = []
for code in TARGET_CODES:
    if code not in snapshot:
        print(f"SKIP {code}: tidak ditemukan")
        continue
    d = snapshot[code]
    results.append(build_growth_entry(code, d))
    results.append(build_macro_entry(code, d))
    results.append(build_risk_entry(code, d))

output_path = "/home/claude/repo/data/synthetic_dataset/batch2_fundamental_db_3lenses.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"Berhasil generate {len(results)} entri (3 lensa x {len(TARGET_CODES)} saham) -> {output_path}")
