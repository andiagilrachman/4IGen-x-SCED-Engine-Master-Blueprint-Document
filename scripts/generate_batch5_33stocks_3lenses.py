#!/usr/bin/env python3
"""
Generate 3 lensa tambahan (Growth, Macro & Interest Rate Sensitivity,
Risk & Red Flags Detector) untuk 33 saham yang lensa "Value & Risk Margin"-nya
sudah ada di batch3_expanded_33stocks_value_risk.json.

Perbaikan dari temuan audit (lihat PROGRESS.md poin 6f): nada narasi step_4
(sintesis) disesuaikan kalau data menunjukkan kondisi ekstrem (PER/PBV/
Altman Z negatif -> kemungkinan ekuitas negatif) -- tidak lagi generik sama
rata untuk semua saham.

Input yang dibutuhkan (file kerja lokal, hasil ekstraksi SQL dump vendor,
TIDAK di-commit ke repo karena besar):
- fundamental_snapshot_all.json (dari extract_fundamental_data.py)
- selected_stocks_batch3.json (daftar 33 saham terpilih + sektornya)
"""
import json

FUND_SNAPSHOT_PATH = "/home/claude/fundamental_snapshot_all.json"
SELECTED_STOCKS_PATH = "/home/claude/selected_stocks_batch3.json"
OUTPUT_PATH = "data/synthetic_dataset/batch5_33stocks_3lenses.json"

MACRO_ANCHOR = {
    "bi_rate_percent": 4.75, "inflation_yoy_percent": 4.76,
    "usd_idr_exchange_rate": 16985, "economic_growth_gdp_percent": 5.12,
    "sector_trend": "BI Rate turun kumulatif 150 bps sejak September 2024 ke level terendah sejak Oktober 2022, tapi inflasi kembali naik mendekati batas atas target BI"
}
PERIOD_LABEL = "Agustus 2026 (snapshot terkini)"
SOURCE_NOTE_TMPL = ("Data rasio dari indicator_snapshot_fundamental (database aigen_db user, "
    "snapshot {date}), sektor dari tabel sectors/stocks. vendor_insight_score proprietary "
    "SENGAJA TIDAK diikutkan. Field NULL di sumber data tidak disertakan (Strict Fact Adherence).")


def fmt(v, suffix=""):
    return f"{v:.4f}{suffix}" if v is not None else "tidak tersedia di data"


def severity_note(d):
    per, pbv, az = d.get("per_x"), d.get("pbv_x"), d.get("altman_z_score")
    return (per is not None and per < 0) or (pbv is not None and pbv < 0) or (az is not None and az < 0)


def base_input_data(code, sector, d):
    return {
        "metadata": {"asset_code": code, "asset_name": d["company_name"], "sector": sector,
                     "period": PERIOD_LABEL, "currency": "IDR", "scale": "Rasio & per-lembar saham"},
        "financial_metrics": {k: v for k, v in {
            "roe_percent": d["roe_percent"], "roa_percent": d["roa_percent"], "der_x": d["der_x"],
            "per_x": d["per_x"], "pbv_x": d["pbv_x"], "eps": d["eps"],
            "altman_z_score": d["altman_z_score"], "piotroski_f_score": d["piotroski_f_score"],
            "graham_number": d["graham_number"], "fundamental_score": d["fundamental_score"],
        }.items() if v is not None},
        "macro_context": MACRO_ANCHOR
    }


def build_growth(code, sector, d):
    extreme = severity_note(d)
    closing = (
        "Perlu dicatat: kombinasi rasio negatif pada data ini (PER/PBV negatif dan/atau Altman "
        "Z negatif) mengindikasikan kemungkinan ekuitas negatif atau kerugian signifikan — "
        "situasi yang memerlukan kehati-hatian ekstra, bukan sekadar variasi normal siklus bisnis."
    ) if extreme else (
        "Catatan: data pertumbuhan pendapatan/laba YoY tidak tersedia dalam Data Schema periode "
        "ini, sehingga analisis terbatas pada snapshot efisiensi tanpa bisa menyimpulkan tren historis."
    )
    return {
        "asset_code": code, "lens": "Growth & Business Expansion",
        "instruction": f"Bagaimana efisiensi profitabilitas {code} ({sector}) jika ditinjau dari kemampuannya menghasilkan imbal balik atas ekuitas dan aset?",
        "input_data": base_input_data(code, sector, d),
        "chain_of_thought": {
            "step_1_identification": f"Indikator efisiensi {code} yang tersedia: ROE {fmt(d['roe_percent'], '%')}, ROA {fmt(d['roa_percent'], '%')}, EPS {fmt(d['eps'])}, fundamental_score {fmt(d['fundamental_score'])}.",
            "step_2_correlation": f"ROE {fmt(d['roe_percent'], '%')} dibanding ROA {fmt(d['roa_percent'], '%')} (dengan DER {fmt(d['der_x'], 'x')}) menggambarkan seberapa besar peran leverage dalam membentuk imbal hasil ekuitas.",
            "step_3_macro_contextualization": f"Di tengah BI Rate {MACRO_ANCHOR['bi_rate_percent']}% dan inflasi {MACRO_ANCHOR['inflation_yoy_percent']}%, ROA {fmt(d['roa_percent'], '%')} perlu dibandingkan dengan biaya modal berlaku serta karakteristik sektor {sector}.",
            "step_4_synthesis": closing
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


def build_macro(code, sector, d):
    return {
        "asset_code": code, "lens": "Macro & Interest Rate Sensitivity",
        "instruction": f"Sejauh mana struktur permodalan {code} ({sector}) membuatnya rentan atau tahan terhadap dinamika suku bunga BI Rate saat ini?",
        "input_data": base_input_data(code, sector, d),
        "chain_of_thought": {
            "step_1_identification": f"Variabel makro: BI Rate {MACRO_ANCHOR['bi_rate_percent']}%, Inflasi {MACRO_ANCHOR['inflation_yoy_percent']}%, GDP {MACRO_ANCHOR['economic_growth_gdp_percent']}%. DER {code}: {fmt(d['der_x'], 'x')}, ROA: {fmt(d['roa_percent'], '%')}.",
            "step_2_correlation": f"DER {fmt(d['der_x'], 'x')} menunjukkan proporsi utang terhadap ekuitas — makin tinggi, makin sensitif beban bunga terhadap perubahan BI Rate. ROA {fmt(d['roa_percent'], '%')} mengindikasikan kapasitas aset menutup beban bunga tsb.",
            "step_3_macro_contextualization": f"BI Rate {MACRO_ANCHOR['bi_rate_percent']}% dalam tren turun, namun inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% mendekati batas atas target bisa membatasi ruang pemangkasan lebih lanjut — relevan bagi emiten sektor {sector} dengan DER {fmt(d['der_x'], 'x')}.",
            "step_4_synthesis": f"Sensitivitas {code} terhadap suku bunga bergantung pada komposisi utang berbunga mengambang yang tidak dirinci data ini — kesimpulan bersifat indikatif dari rasio agregat DER {fmt(d['der_x'], 'x')} dan ROA {fmt(d['roa_percent'], '%')} saja."
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


def build_risk(code, sector, d):
    extreme = severity_note(d)
    opening_tone = "signifikan dan memerlukan perhatian serius" if extreme else "yang perlu dipantau secara rutin"
    return {
        "asset_code": code, "lens": "Risk & Red Flags Detector",
        "instruction": f"Potensi risiko atau kerentanan apa yang dapat diidentifikasi dari profil kesehatan keuangan {code} ({sector}) berdasarkan skor analitis yang tersedia?",
        "input_data": base_input_data(code, sector, d),
        "chain_of_thought": {
            "step_1_identification": f"Titik risiko: Altman Z-Score {fmt(d['altman_z_score'])}, Piotroski F-Score {fmt(d['piotroski_f_score'])} (skala 0-9), DER {fmt(d['der_x'], 'x')}, PBV {fmt(d['pbv_x'], 'x')}.",
            "step_2_correlation": f"Altman Z-Score {fmt(d['altman_z_score'])} mengindikasikan risiko kebangkrutan (makin rendah/negatif makin berisiko). Piotroski F-Score {fmt(d['piotroski_f_score'])} merangkum 9 kriteria kesehatan fundamental. PBV {fmt(d['pbv_x'], 'x')} yang negatif (jika ada) umumnya mengindikasikan ekuitas negatif.",
            "step_3_macro_contextualization": f"Dalam inflasi {MACRO_ANCHOR['inflation_yoy_percent']}% yang naik mendekati batas atas target BI, perusahaan dengan DER {fmt(d['der_x'], 'x')} berpotensi hadapi tekanan tambahan bila BI menahan/membalik arah penurunan suku bunga.",
            "step_4_synthesis": f"Kombinasi Altman Z-Score {fmt(d['altman_z_score'])} dan Piotroski F-Score {fmt(d['piotroski_f_score'])} menunjukkan tingkat risiko {opening_tone} — kedua skor sebaiknya dibaca bersama, bukan terpisah, sebelum kesimpulan investasi diambil."
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


if __name__ == "__main__":
    with open(FUND_SNAPSHOT_PATH) as f:
        snapshot = json.load(f)
    with open(SELECTED_STOCKS_PATH) as f:
        selected = json.load(f)

    results = []
    for s in selected:
        code = s["symbol"]
        if code not in snapshot:
            continue
        d = snapshot[code]
        sector = s["sector"]
        results.append(build_growth(code, sector, d))
        results.append(build_macro(code, sector, d))
        results.append(build_risk(code, sector, d))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Berhasil generate {len(results)} entri -> {OUTPUT_PATH}")
