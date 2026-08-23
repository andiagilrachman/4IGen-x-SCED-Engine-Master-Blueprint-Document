#!/usr/bin/env python3
"""
Generate lensa Risk & Red Flags Detector dan Macro & Interest Rate Sensitivity
untuk 19 institusi keuangan yang punya data 2 tahun (FY2023 & FY2024) di
financial_rows -- memanfaatkan pertumbuhan YoY RIIL dari fakta neraca,
bukan snapshot 1 titik waktu.
"""
import json

FIN_DATA_PATH = "/home/claude/financial_rows_2year_complete.json"
NAMES_PATH = "/home/claude/company_names_batch2.json"  # 15 nama baru
OUTPUT_PATH = "data/synthetic_dataset/batch7_19finance_risk_macro.json"

# nama 4 institusi dari batch4 yang belum ada di company_names_batch2.json
EXTRA_NAMES = {
    "BBCA": "Bank Central Asia",
    "BBNI": "Bank Negara Indonesia (Persero)",
    "BDMN": "Bank Danamon Indonesia",
    "BNGA": "Bank CIMB Niaga",
}

# Anchor makro FY2024 (Q3 2024) dipakai sebagai konteks utama karena analisis
# berfokus pada kondisi TERKINI (FY2024) dengan FY2023 sebagai pembanding historis
MACRO_FY2024 = {
    "bi_rate_percent": 6.00, "inflation_yoy_percent": 2.12,
    "usd_idr_exchange_rate": 15800, "economic_growth_gdp_percent": 4.95,
    "sector_trend": "BI Rate bertahan di 6.00%, inflasi tetap rendah dan stabil di 2.12%"
}


def fmt_rp(v):
    return f"Rp{v/1e12:.2f} Triliun"


def fmt_pct(v):
    return f"{v:+.2f}%"


def pct_change(new, old):
    if old == 0:
        return None
    return ((new - old) / abs(old)) * 100


def build_risk_entry(code, name, p23, p24):
    assets23, assets24 = p23["Jumlah aset"], p24["Jumlah aset"]
    equity23, equity24 = p23["Jumlah ekuitas"], p24["Jumlah ekuitas"]
    ni23, ni24 = p23["Jumlah laba (rugi)"], p24["Jumlah laba (rugi)"]

    asset_growth = pct_change(assets24, assets23)
    equity_growth = pct_change(equity24, equity23)
    ni_growth = pct_change(ni24, ni23)

    roe23 = (ni23 / equity23) * 100
    roe24 = (ni24 / equity24) * 100

    is_declining = ni_growth is not None and ni_growth < 0
    closing = (
        f"Penurunan laba bersih YoY sebesar {fmt_pct(ni_growth)} adalah sinyal yang perlu "
        f"diinvestigasi lebih lanjut — apakah disebabkan faktor musiman, peningkatan "
        f"pencadangan/provisi, atau tekanan struktural pada bisnis inti."
    ) if is_declining else (
        f"Pertumbuhan laba bersih YoY yang positif ({fmt_pct(ni_growth)}) merupakan sinyal "
        f"sehat, namun tetap perlu dibandingkan dengan pertumbuhan aset dan ekuitas untuk "
        f"memastikan kualitas pertumbuhan (bukan sekadar ekspansi neraca tanpa efisiensi)."
    )

    return {
        "asset_code": code,
        "lens": "Risk & Red Flags Detector",
        "instruction": f"Tren apa yang teridentifikasi dari perbandingan kinerja {code} ({name}) antara FY2023 dan FY2024, dan apakah ada sinyal risiko dari perubahan tersebut?",
        "input_data": {
            "metadata": {"asset_code": code, "asset_name": name, "sector": "Financial Services",
                         "period": "FY2023 vs FY2024 (YoY)", "currency": "IDR", "scale": "Absolut (IDR) & Persen"},
            "financial_metrics": {
                "total_assets_fy2023_idr": assets23, "total_assets_fy2024_idr": assets24,
                "total_equity_fy2023_idr": equity23, "total_equity_fy2024_idr": equity24,
                "net_income_fy2023_idr": ni23, "net_income_fy2024_idr": ni24,
                "asset_growth_yoy_percent": round(asset_growth, 2) if asset_growth is not None else None,
                "equity_growth_yoy_percent": round(equity_growth, 2) if equity_growth is not None else None,
                "net_income_growth_yoy_percent": round(ni_growth, 2) if ni_growth is not None else None,
                "roe_fy2023_percent": round(roe23, 2),
                "roe_fy2024_percent": round(roe24, 2),
            },
            "macro_context": MACRO_FY2024
        },
        "chain_of_thought": {
            "step_1_identification": f"Perbandingan FY2023->FY2024: Total Aset {fmt_rp(assets23)} -> {fmt_rp(assets24)} ({fmt_pct(asset_growth)}), Ekuitas {fmt_rp(equity23)} -> {fmt_rp(equity24)} ({fmt_pct(equity_growth)}), Laba Bersih {fmt_rp(ni23)} -> {fmt_rp(ni24)} ({fmt_pct(ni_growth)}).",
            "step_2_correlation": f"ROE bergerak dari {roe23:.2f}% (FY2023) menjadi {roe24:.2f}% (FY2024). Pertumbuhan laba bersih ({fmt_pct(ni_growth)}) dibandingkan pertumbuhan ekuitas ({fmt_pct(equity_growth)}) menunjukkan apakah profitabilitas tumbuh lebih cepat atau lebih lambat dari basis modal.",
            "step_3_macro_contextualization": f"Kedua periode berada dalam rezim BI Rate 6.00% yang relatif stabil, sehingga perubahan kinerja lebih mencerminkan faktor internal/operasional {code} dibanding perubahan kebijakan moneter drastis.",
            "step_4_synthesis": closing
        },
        "_source_note": f"Data neraca/laba-rugi murni FY2023 & FY2024 dari financial_rows (database 4igen user). Semua rasio pertumbuhan dan ROE DIHITUNG LANGSUNG dari fakta (bukan diambil dari sumber lain)."
    }


def build_macro_entry(code, name, p23, p24):
    assets24, equity24 = p24["Jumlah aset"], p24["Jumlah ekuitas"]
    leverage_ratio = assets24 / equity24  # aset/ekuitas, proksi leverage untuk institusi finansial

    return {
        "asset_code": code,
        "lens": "Macro & Interest Rate Sensitivity",
        "instruction": f"Bagaimana tingkat leverage {code} ({name}) pada FY2024 memengaruhi sensitivitasnya terhadap perubahan suku bunga BI Rate?",
        "input_data": {
            "metadata": {"asset_code": code, "asset_name": name, "sector": "Financial Services",
                         "period": "FY2024", "currency": "IDR", "scale": "Absolut (IDR) & Rasio"},
            "financial_metrics": {
                "total_assets_idr": assets24,
                "total_equity_idr": equity24,
                "asset_to_equity_ratio": round(leverage_ratio, 2),
            },
            "macro_context": MACRO_FY2024
        },
        "chain_of_thought": {
            "step_1_identification": f"Total Aset {code} FY2024 sebesar {fmt_rp(assets24)} dengan Total Ekuitas {fmt_rp(equity24)}, menghasilkan rasio Aset/Ekuitas (proksi leverage) sebesar {leverage_ratio:.2f}x.",
            "step_2_correlation": f"Rasio Aset/Ekuitas {leverage_ratio:.2f}x menunjukkan seberapa besar operasi {code} dibiayai oleh sumber dana selain ekuitas (utang/simpanan nasabah untuk institusi perbankan) — semakin tinggi rasio ini, semakin besar eksposur terhadap perubahan biaya dana.",
            "step_3_macro_contextualization": f"Dalam kondisi BI Rate {MACRO_FY2024['bi_rate_percent']}% dan inflasi {MACRO_FY2024['inflation_yoy_percent']}%, institusi dengan leverage tinggi seperti rasio {leverage_ratio:.2f}x lebih sensitif terhadap perubahan biaya dana dibanding institusi dengan basis ekuitas yang lebih tebal.",
            "step_4_synthesis": f"Rasio Aset/Ekuitas {leverage_ratio:.2f}x memberi gambaran skala leverage {code}, namun data ini tidak merinci komposisi sumber dana (giro/tabungan murah vs deposito mahal untuk bank), sehingga kesimpulan sensitivitas suku bunga bersifat indikatif berdasarkan leverage agregat saja."
        },
        "_source_note": f"Data neraca murni FY2024 dari financial_rows (database 4igen user). Rasio Aset/Ekuitas dihitung langsung dari fakta."
    }


if __name__ == "__main__":
    with open(FIN_DATA_PATH) as f:
        fin_data = json.load(f)
    with open(NAMES_PATH) as f:
        names = json.load(f)
    names.update(EXTRA_NAMES)

    results = []
    for code, periods in fin_data.items():
        name = names.get(code, code)
        p23, p24 = periods["FY2023"], periods["FY2024"]
        results.append(build_risk_entry(code, name, p23, p24))
        results.append(build_macro_entry(code, name, p23, p24))

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Berhasil generate {len(results)} entri -> {OUTPUT_PATH}")
