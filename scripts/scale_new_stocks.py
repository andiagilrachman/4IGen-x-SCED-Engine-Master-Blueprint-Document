#!/usr/bin/env python3
"""
Script scaling generic dan reusable — baca daftar kode saham dari
scripts/stocks_to_add.txt, otomatis SKIP kode yang sudah ada di dataset
(cek ke semua data/synthetic_dataset/*.json), generate 4 lensa penuh untuk
kode yang benar-benar baru.

CARA PAKAI:
1. Jalankan extract_fundamental_data.py dulu (butuh SQL dump terbaru di
   scripts/sql_dumps/).
2. Edit scripts/stocks_to_add.txt — satu kode saham per baris (atau baris
   kosong/komentar # diabaikan). Kalau file belum ada, script akan
   membuatkan otomatis 30 kandidat saham (yang punya fundamental_score
   tertinggi & belum pernah dipakai) untuk kamu review/edit dulu.
3. Jalankan: python scripts/scale_new_stocks.py
   (atau lewat run_scaling.bat)
4. Setelah ini, JALANKAN JUGA build_training_jsonl.py supaya JSONL
   training ikut ter-update (bisa manual, atau run_scaling.bat sudah
   include langkah ini otomatis).
"""
import json
import glob
import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
from lib_lens_generators import ALL_LENS_BUILDERS  # noqa: E402

SNAPSHOT_PATH = os.path.join(SCRIPT_DIR, "_working", "fundamental_snapshot_all.json")
STOCKS_LIST_PATH = os.path.join(SCRIPT_DIR, "stocks_to_add.txt")
REPO_ROOT = os.path.dirname(SCRIPT_DIR)
SYNTHETIC_DIR = os.path.join(REPO_ROOT, "data", "synthetic_dataset")


def get_already_used_codes():
    used = set()
    for path in glob.glob(os.path.join(SYNTHETIC_DIR, "*.json")):
        entries = json.load(open(path, encoding="utf-8"))
        for e in entries:
            used.add(e["asset_code"])
    return used


def suggest_candidates(snapshot, already_used, n=30):
    """Kalau stocks_to_add.txt belum ada, sarankan N saham fundamental_score
    tertinggi yang belum pernah dipakai, ditulis ke file untuk direview user."""
    candidates = []
    for code, d in snapshot.items():
        if code in already_used or "-W" in code or "-R" in code:
            continue
        fscore = d.get("fundamental_score")
        if fscore is None:
            continue
        candidates.append((fscore, code, d.get("sector", "?"), d.get("company_name", "?")))
    candidates.sort(reverse=True)
    top_n = candidates[:n]

    with open(STOCKS_LIST_PATH, "w", encoding="utf-8") as f:
        f.write("# Daftar kode saham untuk di-scale (satu kode per baris).\n")
        f.write("# Baris diawali # diabaikan. Hapus/tambah baris sesuai kebutuhan.\n")
        f.write(f"# {n} kandidat ini dipilih otomatis (fundamental_score tertinggi,\n")
        f.write("# belum pernah dipakai) -- REVIEW & edit sebelum run lagi kalau perlu.\n\n")
        for fscore, code, sector, name in top_n:
            f.write(f"{code}  # {sector} | score={fscore:.1f} | {name}\n")

    print(f"File {STOCKS_LIST_PATH} belum ada -- dibuatkan otomatis dengan {len(top_n)} kandidat.")
    print("Review/edit file itu dulu, lalu jalankan ulang script ini.")


def read_stock_list():
    codes = []
    with open(STOCKS_LIST_PATH, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                codes.append(line)
    return codes


if __name__ == "__main__":
    if not os.path.exists(SNAPSHOT_PATH):
        print(f"ERROR: {SNAPSHOT_PATH} tidak ditemukan.")
        print("Jalankan extract_fundamental_data.py dulu.")
        raise SystemExit(1)

    with open(SNAPSHOT_PATH, encoding="utf-8") as f:
        snapshot = json.load(f)

    already_used = get_already_used_codes()
    print(f"Kode saham yang sudah ada di dataset: {len(already_used)}")

    if not os.path.exists(STOCKS_LIST_PATH):
        suggest_candidates(snapshot, already_used)
        raise SystemExit(0)

    requested = read_stock_list()
    new_codes = [c for c in requested if c not in already_used]
    skipped_dup = [c for c in requested if c in already_used]
    not_found = [c for c in new_codes if c not in snapshot]
    new_codes = [c for c in new_codes if c in snapshot]

    print(f"Diminta: {len(requested)} | Baru & valid: {len(new_codes)} | "
          f"Sudah ada (skip): {len(skipped_dup)} | Tidak ditemukan di snapshot: {len(not_found)}")
    if not_found:
        print(f"  Tidak ditemukan: {not_found}")
    if not new_codes:
        print("Tidak ada saham baru untuk diproses. Selesai.")
        raise SystemExit(0)

    results = []
    for code in new_codes:
        d = snapshot[code]
        sector = d.get("sector", "Tidak diketahui")
        for builder in ALL_LENS_BUILDERS:
            results.append(builder(code, sector, d))

    # nama file output otomatis increment (batch9, batch10, dst) berdasar
    # file batchN yang sudah ada di folder
    existing_batches = glob.glob(os.path.join(SYNTHETIC_DIR, "batch*_*.json"))
    next_n = 1
    for path in existing_batches:
        base = os.path.basename(path)
        try:
            n = int(base.replace("batch", "").split("_")[0])
            next_n = max(next_n, n + 1)
        except ValueError:
            continue

    output_path = os.path.join(SYNTHETIC_DIR, f"batch{next_n}_scaled_{len(new_codes)}stocks.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nBerhasil generate {len(results)} entri ({len(new_codes)} saham x 4 lensa)")
    print(f"Tersimpan: {output_path}")
    print("\nJANGAN LUPA jalankan build_training_jsonl.py setelah ini!")
