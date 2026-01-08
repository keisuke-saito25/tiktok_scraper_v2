@echo off
setlocal
set ROOT=C:\Users\wduser01\Desktop\tiktokdatebase
set TARGET=%ROOT%\UGCdate\TikTok_UGC.xlsx
set PATTERN=%ROOT%\runs\w*\ugc_%DATE:~0,4%%DATE:~5,2%%DATE:~8,2%.csv

rem ---- tiktok_cli.exe（collect）が残っていたら待つ ----
:wait_collect
tasklist /FI "IMAGENAME eq tiktok_cli.exe" | find /I "tiktok_cli.exe" >nul
if %ERRORLEVEL%==0 (
  echo [INFO] collectors still running... wait 30s
  timeout /t 30 /nobreak >nul
  goto wait_collect
)

echo [INFO] ===== Apply start =====
echo [INFO] target  = "%TARGET%"
echo [INFO] pattern = "%PATTERN%"

"%ROOT%\tiktok_cli.exe" apply --target "%TARGET%" --in "%PATTERN%"

endlocal
