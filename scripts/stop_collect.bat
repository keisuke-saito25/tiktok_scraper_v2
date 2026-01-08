@echo off
echo [INFO] stopping collectors...
taskkill /IM tiktok_cli.exe /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq worker1" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq worker2" /T /F >nul 2>&1
taskkill /IM chromedriver.exe /F >nul 2>&1
echo [INFO] done.
