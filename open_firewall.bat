@echo off
echo ==========================================
echo   ZEA Firewall Setup - Membuka Port 5000
echo ==========================================
echo.
echo Script ini perlu dijalankan sebagai Administrator.
echo Klik kanan file ini lalu pilih "Run as administrator".
echo.

netsh advfirewall firewall add rule name="ZEA Flask Server (TCP 5000)" dir=in action=allow protocol=TCP localport=5000

if %errorlevel%==0 (
    echo.
    echo [SUKSES] Port 5000 berhasil dibuka!
    echo HP Anda sekarang bisa mengakses ZEA via WiFi.
) else (
    echo.
    echo [GAGAL] Pastikan Anda menjalankan file ini sebagai Administrator.
)

echo.
pause
