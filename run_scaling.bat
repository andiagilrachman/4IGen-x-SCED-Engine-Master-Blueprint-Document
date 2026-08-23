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

REM Pindah ke folder tempat file .bat ini berada (supaya selalu jalan dari
REM lokasi yang benar, apapun cara file ini dijalankan -- double-click,
REM shortcut, run as admin, dsb -- yang defaultnya bisa beda-beda folder kerja)
cd /d "%~dp0"

echo Folder kerja sekarang: %cd%
echo.

REM Cek kalau file SQL salah taruh (langsung di scripts\, bukan scripts\sql_dumps\)
REM Pakai wildcard (stocks_sectors*) supaya toleran kalau nama filenya sedikit
REM beda (misal ekstensi dobel karena Windows sembunyikan .sql -- lihat catatan
REM di extract_fundamental_data.py)
for %%f in (scripts\stocks_sectors*) do (
    if exist "%%f" (
        echo PERINGATAN: ditemukan %%f langsung di folder scripts\
        echo Seharusnya ada di scripts\sql_dumps\
        if not exist "scripts\sql_dumps" mkdir "scripts\sql_dumps"
        move "%%f" "scripts\sql_dumps\" >nul
        echo Dipindahkan ke scripts\sql_dumps\
        echo.
    )
)
for %%f in (scripts\indicator_snapshot_fundamental*) do (
    if exist "%%f" (
        echo PERINGATAN: ditemukan %%f langsung di folder scripts\
        echo Seharusnya ada di scripts\sql_dumps\
        if not exist "scripts\sql_dumps" mkdir "scripts\sql_dumps"
        move "%%f" "scripts\sql_dumps\" >nul
        echo Dipindahkan ke scripts\sql_dumps\
        echo.
    )
)
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
