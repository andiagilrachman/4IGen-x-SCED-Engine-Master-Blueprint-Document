#!/usr/bin/env python3
"""
Perluasan cakupan financial_rows: 15 institusi keuangan baru (bank umum,
bank syariah, multifinance, asuransi, sekuritas) selain 4 yang sudah dipakai
di batch4 (BBCA/BBNI/BDMN/BNGA).

Data historis FY2023 & FY2024, dipasangkan anchor makro Desember 2023 &
Q3 2024 (sama seperti batch4).
"""
import json

FIN_DATA_PATH = "/home/claude/financial_rows_batch2.json"
NAMES_PATH = "/home/claude/company_names_batch2.json"
OUTPUT_PATH = "data/synthetic_dataset/batch6_15finance_historical.json"

ANCHORS = {
    "FY2023": {
        "label": "FY2023 (data tahunan, dipasangkan konteks makro Desember 2023)",
        "bi_rate_percent": 6.00, "inflation_yoy_percent": 2.61,
        "usd_idr_exchange_rate": 15500,
        "sector_trend": "BI Rate naik ke 6.00% (tertinggi 4 tahun) untuk stabilkan Rupiah, inflasi domestik melandai ke 2.61%"
    },
    "FY2024": {
        "label": "FY2024 (data tahunan, dipasangkan konteks makro Q3 2024)",
        "bi_rate_percent": 6.00, "inflation_yoy_percent": 2.12,
        "usd_idr_exchange_rate": 15800, "economic_growth_gdp_percent": 4.95,
        "sector_trend": "BI Rate bertahan di 6.00%, inflasi tetap rendah dan stabil di 2.12%"
    }
}


def fmt_rp(v):
    return f"Rp{v/1e12:.2f} Triliun"


def fmt_pct(v):
    return f"{v:.2f}%"


if __name__ == "__main__":
    with open(FIN_DATA_PATH) as f:
        fin_data = json.load(f)
    with open(NAMES_PATH) as f:
        names = json.load(f)

    results = []
    skipped_incomplete = []
    for code, periods in fin_data.items():
        name = names.get(code, code)
        for fy, metrics in periods.items():
            assets = metrics.get("Jumlah aset")
            equity = metrics.get("Jumlah ekuitas")
            net_income = metrics.get("Jumlah laba (rugi)")
            interest_income = metrics.get("Pendapatan bunga")
            # beberapa institusi non-bank (sekuritas/asuransi) mungkin tidak
            # punya "Pendapatan bunga" -> skip kalau data inti tidak lengkap
            if not all([assets, equity, net_income]):
                skipped_incomplete.append(f"{code}-{fy}")
                continue

            roe_calc = (net_income / equity) * 100
            anchor = ANCHORS[fy]

            financial_metrics = {
                "total_assets_idr": assets,
                "total_equity_idr": equity,
                "net_income_idr": net_income,
                "roe_percent_calculated": round(roe_calc, 2)
            }
            if interest_income:
                financial_metrics["interest_income_idr"] = interest_income

            input_data = {
                "metadata": {
                    "asset_code": code, "asset_name": name,
                    "sector": "Financial Services", "period": anchor["label"],
                    "currency": "IDR", "scale": "Absolut (IDR) & Triliun"
                },
                "financial_metrics": financial_metrics,
                "macro_context": {k: v for k, v in anchor.items() if k != "label"}
            }

            interest_sentence = (
                f", Pendapatan Bunga {fmt_rp(interest_income)}" if interest_income else ""
            )

            entry = {
                "asset_code": code,
                "lens": "Growth & Business Expansion",
                "instruction": f"Bagaimana kinerja pertumbuhan aset dan profitabilitas {code} ({name}) pada {fy} berdasarkan data laporan keuangan tahunan?",
                "input_data": input_data,
                "chain_of_thought": {
                    "step_1_identification": f"Pada {fy}, {code} mencatat Total Aset sebesar {fmt_rp(assets)}, Total Ekuitas {fmt_rp(equity)}{interest_sentence}, dan Laba Bersih {fmt_rp(net_income)}.",
                    "step_2_correlation": f"ROE terhitung dari data (Laba Bersih / Ekuitas) sebesar {fmt_pct(roe_calc)}, menunjukkan efisiensi penggunaan modal pemegang saham untuk menghasilkan laba pada periode {fy}.",
                    "step_3_macro_contextualization": f"Periode {fy} berada dalam konteks BI Rate {anchor['bi_rate_percent']}% dan inflasi {anchor['inflation_yoy_percent']}% — {anchor['sector_trend']}",
                    "step_4_synthesis": f"Dengan Total Aset {fmt_rp(assets)} dan ROE {fmt_pct(roe_calc)} pada {fy}, {code} menunjukkan skala dan profitabilitas yang bisa dibandingkan dengan periode lain untuk menilai tren pertumbuhan dari waktu ke waktu."
                },
                "_source_note": f"Data neraca/laba-rugi murni dari financial_rows (database 4igen user, statement BS/IS periode FY {fy[2:]}). ROE dihitung langsung dari fakta (Net Income/Equity)."
            }
            results.append(entry)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Berhasil generate {len(results)} entri -> {OUTPUT_PATH}")
    if skipped_incomplete:
        print(f"Dilewati (data inti tidak lengkap): {skipped_incomplete}")
