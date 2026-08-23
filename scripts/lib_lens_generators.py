#!/usr/bin/env python3
"""
Modul generator reusable untuk 4 lensa analisis SCED Engine
(Value & Risk Margin, Growth, Macro & Interest Rate Sensitivity,
Risk & Red Flags Detector) dari data indicator_snapshot_fundamental.

Dipakai oleh scale_new_stocks.py. Konsolidasi dari pola yang sudah teruji
di batch3/batch5/batch8, termasuk semua perbaikan bug yang sudah ditemukan:
- Nada narasi menyesuaikan kondisi ekstrem (PER/PBV/Altman Z negatif)
- PBV=0 ditangani terpisah dari PBV negatif dan PBV positif wajar
  (bukan otomatis diklaim "wajar")
"""

MACRO_ANCHOR_TERKINI = {
    "bi_rate_percent": 4.75, "inflation_yoy_percent": 4.76,
    "usd_idr_exchange_rate": 16985, "economic_growth_gdp_percent": 5.12,
    "sector_trend": "BI Rate turun kumulatif 150 bps sejak September 2024 ke level terendah sejak Oktober 2022, tapi inflasi kembali naik mendekati batas atas target BI"
}
PERIOD_LABEL_TERKINI = "Agustus 2026 (snapshot terkini)"
SOURCE_NOTE_TMPL = ("Data rasio dari indicator_snapshot_fundamental (database aigen_db user, "
    "snapshot {date}), sektor dari tabel sectors/stocks. vendor_insight_score proprietary "
    "SENGAJA TIDAK diikutkan. Field NULL di sumber data tidak disertakan (Strict Fact Adherence).")


def fmt(v, suffix=""):
    return f"{v:.4f}{suffix}" if v is not None else "tidak tersedia di data"


def severity_note(d):
    """True kalau data menunjukkan kondisi ekstrem (kemungkinan ekuitas negatif dsb)."""
    per, pbv, az = d.get("per_x"), d.get("pbv_x"), d.get("altman_z_score")
    return (per is not None and per < 0) or (pbv is not None and pbv < 0) or (az is not None and az < 0)


def base_input_data(code, sector, d, macro=None, period_label=None):
    macro = macro or MACRO_ANCHOR_TERKINI
    period_label = period_label or PERIOD_LABEL_TERKINI
    return {
        "metadata": {"asset_code": code, "asset_name": d["company_name"], "sector": sector,
                     "period": period_label, "currency": "IDR", "scale": "Rasio & per-lembar saham"},
        "financial_metrics": {k: v for k, v in {
            "roe_percent": d["roe_percent"], "roa_percent": d["roa_percent"], "der_x": d["der_x"],
            "per_x": d["per_x"], "pbv_x": d["pbv_x"], "eps": d["eps"],
            "altman_z_score": d["altman_z_score"], "piotroski_f_score": d["piotroski_f_score"],
            "graham_number": d["graham_number"], "fundamental_score": d["fundamental_score"],
        }.items() if v is not None},
        "macro_context": macro
    }


def build_value_risk(code, sector, d, macro=None, period_label=None):
    macro = macro or MACRO_ANCHOR_TERKINI
    return {
        "asset_code": code, "lens": "Value & Risk Margin",
        "instruction": f"Sebagai investor yang mengutamakan proteksi modal dan margin keselamatan (margin of safety), bagaimana Anda menilai profil valuasi dan risiko {code} ({sector}) berdasarkan data rasio terkini?",
        "input_data": base_input_data(code, sector, d, macro, period_label),
        "chain_of_thought": {
            "step_1_identification": f"Indikator kunci {code} mencakup PER sebesar {fmt(d['per_x'], 'x')}, PBV sebesar {fmt(d['pbv_x'], 'x')}, dan EPS sebesar {fmt(d['eps'])}. ROE tercatat {fmt(d['roe_percent'], '%')} dan ROA {fmt(d['roa_percent'], '%')}.",
            "step_2_correlation": f"Rasio DER sebesar {fmt(d['der_x'], 'x')} menunjukkan struktur permodalan terhadap ekuitas. Altman Z-Score {fmt(d['altman_z_score'])} dan Piotroski F-Score {fmt(d['piotroski_f_score'])} (skala 0-9) memberi indikasi kesehatan keuangan dan kekuatan fundamental dari sudut pandang berbeda.",
            "step_3_macro_contextualization": f"Di tengah BI Rate {macro['bi_rate_percent']}% dan inflasi {macro['inflation_yoy_percent']}%, valuasi PER {fmt(d['per_x'], 'x')} perlu dibandingkan dengan biaya modal yang berlaku saat ini serta karakteristik sektor {sector}.",
            "step_4_synthesis": f"Graham Number (estimasi nilai wajar berbasis EPS & BVPS) tercatat {fmt(d['graham_number'])}, salah satu acuan margin keselamatan investor value. Fundamental score komposit {fmt(d['fundamental_score'])} merangkum banyak faktor sekaligus, namun tetap perlu dibaca bersama rasio individual di atas, bukan sebagai angka tunggal pengambil keputusan."
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


def build_growth(code, sector, d, macro=None, period_label=None):
    macro = macro or MACRO_ANCHOR_TERKINI
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
        "input_data": base_input_data(code, sector, d, macro, period_label),
        "chain_of_thought": {
            "step_1_identification": f"Indikator efisiensi {code} yang tersedia: ROE {fmt(d['roe_percent'], '%')}, ROA {fmt(d['roa_percent'], '%')}, EPS {fmt(d['eps'])}, fundamental_score {fmt(d['fundamental_score'])}.",
            "step_2_correlation": f"ROE {fmt(d['roe_percent'], '%')} dibanding ROA {fmt(d['roa_percent'], '%')} (dengan DER {fmt(d['der_x'], 'x')}) menggambarkan seberapa besar peran leverage dalam membentuk imbal hasil ekuitas.",
            "step_3_macro_contextualization": f"Di tengah BI Rate {macro['bi_rate_percent']}% dan inflasi {macro['inflation_yoy_percent']}%, ROA {fmt(d['roa_percent'], '%')} perlu dibandingkan dengan biaya modal berlaku serta karakteristik sektor {sector}.",
            "step_4_synthesis": closing
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


def build_macro(code, sector, d, macro=None, period_label=None):
    macro = macro or MACRO_ANCHOR_TERKINI
    return {
        "asset_code": code, "lens": "Macro & Interest Rate Sensitivity",
        "instruction": f"Sejauh mana struktur permodalan {code} ({sector}) membuatnya rentan atau tahan terhadap dinamika suku bunga BI Rate saat ini?",
        "input_data": base_input_data(code, sector, d, macro, period_label),
        "chain_of_thought": {
            "step_1_identification": f"Variabel makro: BI Rate {macro['bi_rate_percent']}%, Inflasi {macro['inflation_yoy_percent']}%, GDP {macro.get('economic_growth_gdp_percent', 'n/a')}%. DER {code}: {fmt(d['der_x'], 'x')}, ROA: {fmt(d['roa_percent'], '%')}.",
            "step_2_correlation": f"DER {fmt(d['der_x'], 'x')} menunjukkan proporsi utang terhadap ekuitas — makin tinggi, makin sensitif beban bunga terhadap perubahan BI Rate. ROA {fmt(d['roa_percent'], '%')} mengindikasikan kapasitas aset menutup beban bunga tsb.",
            "step_3_macro_contextualization": f"BI Rate {macro['bi_rate_percent']}% dengan inflasi {macro['inflation_yoy_percent']}% — relevan bagi emiten sektor {sector} dengan DER {fmt(d['der_x'], 'x')} dalam memproyeksikan beban bunga ke depan.",
            "step_4_synthesis": f"Sensitivitas {code} terhadap suku bunga bergantung pada komposisi utang berbunga mengambang yang tidak dirinci data ini — kesimpulan bersifat indikatif dari rasio agregat DER {fmt(d['der_x'], 'x')} dan ROA {fmt(d['roa_percent'], '%')} saja."
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


def build_risk(code, sector, d, macro=None, period_label=None):
    macro = macro or MACRO_ANCHOR_TERKINI
    extreme = severity_note(d)
    opening_tone = "signifikan dan memerlukan perhatian serius" if extreme else "yang perlu dipantau secara rutin"
    pbv = d.get("pbv_x")
    if pbv is not None and pbv < 0:
        pbv_sentence = f"PBV {fmt(pbv, 'x')} yang negatif mengindikasikan kemungkinan ekuitas negatif, sinyal risiko struktural yang serius."
    elif pbv == 0:
        pbv_sentence = "PBV tercatat 0.0000x, kemungkinan anomali data atau nilai buku mendekati nol — perlu verifikasi lebih lanjut sebelum ditafsirkan, bukan otomatis dianggap wajar."
    else:
        pbv_sentence = f"PBV {fmt(pbv, 'x')} berada dalam kisaran wajar (positif), tidak mengindikasikan masalah ekuitas negatif."
    return {
        "asset_code": code, "lens": "Risk & Red Flags Detector",
        "instruction": f"Potensi risiko atau kerentanan apa yang dapat diidentifikasi dari profil kesehatan keuangan {code} ({sector}) berdasarkan skor analitis yang tersedia?",
        "input_data": base_input_data(code, sector, d, macro, period_label),
        "chain_of_thought": {
            "step_1_identification": f"Titik risiko: Altman Z-Score {fmt(d['altman_z_score'])}, Piotroski F-Score {fmt(d['piotroski_f_score'])} (skala 0-9), DER {fmt(d['der_x'], 'x')}, PBV {fmt(d['pbv_x'], 'x')}.",
            "step_2_correlation": f"Altman Z-Score {fmt(d['altman_z_score'])} mengindikasikan risiko kebangkrutan (makin rendah/negatif makin berisiko). Piotroski F-Score {fmt(d['piotroski_f_score'])} merangkum 9 kriteria kesehatan fundamental. {pbv_sentence}",
            "step_3_macro_contextualization": f"Dalam inflasi {macro['inflation_yoy_percent']}% saat ini, perusahaan dengan DER {fmt(d['der_x'], 'x')} berpotensi hadapi tekanan tambahan bila BI menahan/membalik arah kebijakan suku bunga.",
            "step_4_synthesis": f"Kombinasi Altman Z-Score {fmt(d['altman_z_score'])} dan Piotroski F-Score {fmt(d['piotroski_f_score'])} menunjukkan tingkat risiko {opening_tone} — kedua skor sebaiknya dibaca bersama, bukan terpisah, sebelum kesimpulan investasi diambil."
        },
        "_source_note": SOURCE_NOTE_TMPL.format(date=d["snapshot_date"])
    }


ALL_LENS_BUILDERS = [build_value_risk, build_growth, build_macro, build_risk]
