#!/usr/bin/env python3
"""
Ekstraksi data fundamental saham dari SQL dump aigen_db + 4igen untuk SCED Engine.

PRINSIP KEAMANAN DATA (lihat PROGRESS.md poin 6b):
- HANYA pakai fakta neraca/laba-rugi murni (financial_rows) -> disclosure wajib publik, GREEN
- HANYA pakai rasio standar terhitung (ROE/ROA/DER/PER/PBV/EPS/Altman Z/Piotroski F/Graham Number)
  -> rumus standar dari fakta publik, bukan opini/narasi proprietary vendor
- TIDAK PAKAI vendor_insight_score (eksplisit proprietary vendor)
- TIDAK PAKAI shareholder_composition (source='invezgo' eksplisit, ToS lebih ketat)
"""
import re
import json
import decimal

UPLOAD_DIR = "/mnt/user-data/uploads"

def parse_stocks_map(path):
    """Ambil mapping stock_id (int) -> {symbol, company_name, sector_id} dari tabel stocks aigen_db."""
    stock_map = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    # Ambil blok INSERT INTO `stocks`
    m = re.search(r"INSERT INTO `stocks`.*?VALUES\s*(.*?);\n\n", content, re.S)
    if not m:
        return stock_map
    body = m.group(1)
    # setiap baris data: (id, 'symbol', 'company_name', ...)
    for row_match in re.finditer(r"\((\d+),\s*'([^']*)',\s*'([^']*)'", body):
        sid, symbol, name = row_match.groups()
        stock_map[int(sid)] = {"symbol": symbol, "company_name": name}
    return stock_map

def parse_sectors_map(path):
    sector_map = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    m = re.search(r"INSERT INTO `sectors`.*?VALUES\s*(.*?);\n", content, re.S)
    if not m:
        return sector_map
    body = m.group(1)
    for row_match in re.finditer(r"\((\d+),\s*'([^']*)'", body):
        sid, name = row_match.groups()
        sector_map[int(sid)] = name
    return sector_map

def parse_indicator_snapshot(path, stock_map):
    """Ambil rasio fundamental standar per saham (exclude vendor_insight_score)."""
    results = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.match(
                r"\((\d+), (\d+), '([\d-]+)', "
                r"(NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), "
                r"(NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), "
                r"(NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), "
                r"(NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+), (NULL|[\d.-]+),",
                line,
            )
            if not m:
                continue
            (rid, stock_id, snap_date, roe, roa, der, per, pbv, eps, bvps, div_yield,
             rev_growth, ni_growth, npm, gpm, curr_ratio, quick_ratio,
             altman_z, beneish_m, piotroski_f, graham, fscore) = m.groups()
            sid = int(stock_id)
            if sid not in stock_map:
                continue

            def num(v):
                return None if v == "NULL" else float(v)

            results[stock_map[sid]["symbol"]] = {
                "company_name": stock_map[sid]["company_name"],
                "snapshot_date": snap_date,
                "roe_percent": num(roe),
                "roa_percent": num(roa),
                "der_x": num(der),
                "per_x": num(per),
                "pbv_x": num(pbv),
                "eps": num(eps),
                "bvps": num(bvps),
                "dividend_yield_percent": num(div_yield),
                "revenue_growth_yoy_percent": num(rev_growth),
                "net_income_growth_yoy_percent": num(ni_growth),
                "net_profit_margin_percent": num(npm),
                "gross_profit_margin_percent": num(gpm),
                "current_ratio": num(curr_ratio),
                "quick_ratio": num(quick_ratio),
                "altman_z_score": num(altman_z),
                "piotroski_f_score": num(piotroski_f),
                "graham_number": num(graham),
                "fundamental_score": num(fscore),
                # vendor_insight_score SENGAJA TIDAK DIAMBIL (proprietary vendor)
            }
    return results


def parse_financial_rows(path, target_codes, target_rows):
    """Ambil fakta neraca/laba-rugi murni untuk kode saham & row_name tertentu."""
    results = {}  # code -> {row_name: {fy_year, period: amount}}
    with open(path, encoding="utf-8", errors="ignore") as f:
        for line in f:
            m = re.search(
                r"\(\d+, '([A-Z0-9-]+)', '(BS|IS)', 'Q', '[^']*', '([^']+)', "
                r"NULL, NULL, NULL, '[^']*', (\d+), '([A-Z0-9]+)', ([\d.-]+)\)",
                line,
            )
            if not m:
                continue
            code, stmt, row_name, fy_year, period, amount = m.groups()
            if code not in target_codes or row_name not in target_rows:
                continue
            results.setdefault(code, {}).setdefault(row_name, {})[f"{period}{fy_year}"] = float(amount)
    return results


if __name__ == "__main__":
    stock_map = parse_stocks_map(f"{UPLOAD_DIR}/Database_Stock_1.sql")
    sector_map = parse_sectors_map(f"{UPLOAD_DIR}/Database_Stock_1.sql")
    print(f"Jumlah saham di stock_map: {len(stock_map)}")

    snapshot = parse_indicator_snapshot(f"{UPLOAD_DIR}/aigen_db.sql", stock_map)
    print(f"Jumlah saham dengan snapshot fundamental: {len(snapshot)}")

    # contoh cek 5 saham target scaling
    for code in ["BMRI", "UNVR", "ANTM", "ASII", "ICBP"]:
        if code in snapshot:
            print(f"\n=== {code} ===")
            print(json.dumps(snapshot[code], indent=2))
        else:
            print(f"\n{code}: TIDAK DITEMUKAN di snapshot")

    with open("/home/claude/fundamental_snapshot_all.json", "w") as f:
        json.dump(snapshot, f, indent=2)
    print(f"\nTersimpan: /home/claude/fundamental_snapshot_all.json ({len(snapshot)} saham)")
