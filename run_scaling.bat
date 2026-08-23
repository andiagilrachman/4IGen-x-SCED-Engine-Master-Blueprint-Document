@echo off
REM ==============================================================================
REM run_scaling.bat — Pipeline scaling data SCED Engine, jalan otomatis di Windows
REM ==============================================================================
REM CARA PAKAI:
REM   1. Pastikan Python sudah terinstall (cek: python --version di cmd)
REM   2. Taruh file SQL export terbaru di scripts\sql_dumps\:
REM        - stocks_sectors.sql (tabel stocks + sectors dari database aigen_db)
REM        - indicator_snapshot_fundamental.sql (tabel indicator_snapshot_fundamental)
REM   3. Double-click file ini, ATAU jalankan dari folder repo:
REM        run_scaling.bat
REM   4. Kalau file scripts\stocks_to_add.txt belum ada, script akan otomatis
REM      membuatkan daftar 30 kandidat saham -- review/edit file itu, lalu
REM      jalankan run_scaling.bat SEKALI LAGI untuk benar-benar generate datanya.
REM ==============================================================================

echo.
echo === LANGKAH 1: Ekstrak data fundamental dari SQL dump ===
python scripts\extract_fundamental_data.py
if errorlevel 1 (
    echo.
    echo GAGAL di Langkah 1. Cek pesan error di atas.
    pause
    exit /b 1
)

echo.
echo === LANGKAH 2: Generate data sintetis untuk saham baru ===
python scripts\scale_new_stocks.py
if errorlevel 1 (
    echo.
    echo GAGAL di Langkah 2. Cek pesan error di atas.
    pause
    exit /b 1
)

echo.
echo === LANGKAH 3: Rebuild file JSONL training ===
python scripts\build_training_jsonl.py
if errorlevel 1 (
    echo.
    echo GAGAL di Langkah 3. Cek pesan error di atas.
    pause
    exit /b 1
)

echo.
echo ==============================================================================
echo SELESAI. Jangan lupa commit ^& push ke GitHub:
echo   git add .
echo   git commit -m "scaling: tambah data saham baru"
echo   git push origin main
echo ==============================================================================
pause
