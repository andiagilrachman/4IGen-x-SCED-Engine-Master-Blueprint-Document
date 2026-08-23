# Folder ini untuk file export SQL

Taruh 2 file hasil export dari phpMyAdmin di sini (database `aigen_db`):

1. **`stocks_sectors.sql`** — export tabel `stocks` + `sectors` bareng
   (centang keduanya di phpMyAdmin sebelum klik Ekspor)
2. **`indicator_snapshot_fundamental.sql`** — export tabel
   `indicator_snapshot_fundamental` saja

Setelah kedua file ada di sini, jalankan `run_scaling.bat` dari folder
utama repo (`C:\4IGen-x-SCED-Engine\run_scaling.bat`).

**Catatan:** file `.sql` di folder ini TIDAK ikut ter-commit ke Git
(sudah di-exclude lewat `.gitignore`) — karena berisi data vendor mentah
skala besar yang tidak untuk didistribusi ulang. Aman ditaruh di sini,
tidak akan ke-upload ke GitHub.
