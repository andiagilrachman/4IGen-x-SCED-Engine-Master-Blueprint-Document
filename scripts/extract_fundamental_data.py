#!/usr/bin/env python3
"""
Ekstraksi data fundamental saham dari SQL dump aigen_db untuk SCED Engine.
VERSI PORTABLE — pakai path relatif, bisa dijalankan di komputer manapun
(termasuk lewat run_scaling.bat di Windows).

CARA PAKAI:
1. Export tabel `stocks`+`sectors` (dari database aigen_db) dan tabel
   `indicator_snapshot_fundamental` (juga dari aigen_db) lewat phpMyAdmin.
2. Taruh file .sql hasil export di folder scripts/sql_dumps/ dengan nama:
   - scripts/sql_dumps/stocks_sectors.sql  (berisi tabel stocks + sectors)
   - scripts/sql_dumps/indicator_snapshot_fundamental.sql
3. Jalankan: python scripts/extract_fundamental_data.py
   (atau lewat run_scaling.bat)

PRINSIP KEAMANAN DATA (lihat PROGRESS.md poin 6b):
- HANYA pakai rasio standar terhitung (ROE/ROA/DER/PER/PBV/EPS/Altman Z/
  Piotroski F/Graham Number) -> rumus standar dari fakta publik.
- TIDAK PAKAI vendor_insight_score (eksplisit proprietary vendor).
"""
import re
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SQL_DUMPS_DIR = os.path.join(SCRIPT_DIR, "sql_dumps")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "_working")

STOCKS_SQL = os.path.join(SQL_DUMPS_DIR, "stocks_sectors.sql")
SNAPSHOT_SQL = os.path.join(SQL_DUMPS_DIR, "indicator_snapshot_fundamental.sql")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "fundamental_snapshot_all.json")


def parse_stocks_map(path):
    """Baca SEMUA blok INSERT INTO `stocks` (dump SQL sering dipecah jadi
    banyak statement INSERT terpisah, bukan 1 blok besar)."""
    stock_map = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    for m in re.finditer(r"INSERT INTO `stocks`.*?VALUES\s*(.*?);", content, re.S):
        body = m.group(1)
        for row_match in re.finditer(r"\((\d+),\s*'([^']*)',\s*'([^']*)'", body):
            sid, symbol, name = row_match.groups()
            stock_map[int(sid)] = {"symbol": symbol, "company_name": name}
    return stock_map


def parse_sector_ids_map(path):
    """Ambil sector_id per stock_id dari SEMUA blok INSERT INTO stocks."""
    sector_id_map = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    for m in re.finditer(r"INSERT INTO `stocks`.*?VALUES\s*(.*?);", content, re.S):
        body = m.group(1)
        for row in re.finditer(r"\((\d+),\s*'[^']*',\s*'[^']*',\s*NULL,\s*(\d+|NULL)", body):
            sid, sector_id = row.groups()
            if sector_id != "NULL":
                sector_id_map[int(sid)] = int(sector_id)
    return sector_id_map


def parse_sectors_map(path):
    sector_map = {}
    with open(path, encoding="utf-8", errors="ignore") as f:
        content = f.read()
    m = re.search(r"INSERT INTO `sectors`.*?VALUES\s*(.*?);", content, re.S)
    if not m:
        return sector_map
    body = m.group(1)
    for row_match in re.finditer(r"\((\d+),\s*'([^']*)'", body):
        sid, name = row_match.groups()
        sector_map[int(sid)] = name
    return sector_map


def parse_indicator_snapshot(path, stock_map, sector_id_map, sectors_map):
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

            sector_id = sector_id_map.get(sid)
            sector_name = sectors_map.get(sector_id, "Tidak diketahui")

            results[stock_map[sid]["symbol"]] = {
                "company_name": stock_map[sid]["company_name"],
                "sector": sector_name,
                "snapshot_date": snap_date,
                "roe_percent": num(roe), "roa_percent": num(roa), "der_x": num(der),
                "per_x": num(per), "pbv_x": num(pbv), "eps": num(eps), "bvps": num(bvps),
                "dividend_yield_percent": num(div_yield),
                "revenue_growth_yoy_percent": num(rev_growth),
                "net_income_growth_yoy_percent": num(ni_growth),
                "net_profit_margin_percent": num(npm), "gross_profit_margin_percent": num(gpm),
                "current_ratio": num(curr_ratio), "quick_ratio": num(quick_ratio),
                "altman_z_score": num(altman_z), "piotroski_f_score": num(piotroski_f),
                "graham_number": num(graham), "fundamental_score": num(fscore),
                # vendor_insight_score SENGAJA TIDAK DIAMBIL (proprietary vendor)
            }
    return results


if __name__ == "__main__":
    if not os.path.exists(STOCKS_SQL):
        print(f"ERROR: File tidak ditemukan: {STOCKS_SQL}")
        print("Taruh file export SQL tabel stocks+sectors di sana dulu.")
        raise SystemExit(1)
    if not os.path.exists(SNAPSHOT_SQL):
        print(f"ERROR: File tidak ditemukan: {SNAPSHOT_SQL}")
        print("Taruh file export SQL tabel indicator_snapshot_fundamental di sana dulu.")
        raise SystemExit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    stock_map = parse_stocks_map(STOCKS_SQL)
    sector_id_map = parse_sector_ids_map(STOCKS_SQL)
    sectors_map = parse_sectors_map(STOCKS_SQL)
    print(f"Jumlah saham di stock_map: {len(stock_map)}")

    snapshot = parse_indicator_snapshot(SNAPSHOT_SQL, stock_map, sector_id_map, sectors_map)
    print(f"Jumlah saham dengan snapshot fundamental: {len(snapshot)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2, ensure_ascii=False)
    print(f"Tersimpan: {OUTPUT_PATH} ({len(snapshot)} saham)")
