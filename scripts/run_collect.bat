@echo off
setlocal

rem ===== 基本パス =====
set "ROOT=C:\Users\wduser01\Desktop\tiktokdatebase"
set "EXE=%ROOT%\tiktok_cli.exe"
set "LOG=%ROOT%\logs"
set "RUN1=%ROOT%\runs\w1"
set "RUN2=%ROOT%\runs\w2"
set "PROFILE1=%ROOT%\chrome_profile\worker_1"
set "PROFILE2=%ROOT%\chrome_profile\worker_2"
set "SETTINGS=%ROOT%\UGCdate\TikTok_UGC.xlsx"

rem ===== ロケール非依存の日付（yyyyMMdd） =====
for /f %%I in ('powershell -NoProfile -Command "(Get-Date).ToString(\"yyyyMMdd\")"') do set "YMD=%%I"

rem ===== 必要ディレクトリ作成 =====
if not exist "%LOG%"  mkdir "%LOG%"
if not exist "%RUN1%" mkdir "%RUN1%"
if not exist "%RUN2%" mkdir "%RUN2%"
if not exist "%PROFILE1%" mkdir "%PROFILE1%"
if not exist "%PROFILE2%" mkdir "%PROFILE2%"

set "LAUNCHLOG=%LOG%\collect_launcher_%YMD%.log"
echo [LAUNCH] %date% %time% starting...                                > "%LAUNCHLOG%"
echo   ROOT=%ROOT%                                                    >> "%LAUNCHLOG%"
echo   EXE =%EXE%                                                     >> "%LAUNCHLOG%"
echo   SETT=%SETTINGS% (SOURCE=UGCdate\TikTok_UGC.xlsx)               >> "%LAUNCHLOG%"

rem ===== 事前チェック =====
if not exist "%EXE%"       (echo [ERROR] not found exe: "%EXE%"       & echo [ERROR] not found exe: "%EXE%"       >> "%LAUNCHLOG%" & exit /b 3)
if not exist "%SETTINGS%"  (echo [ERROR] not found settings: "%SETTINGS%" & echo [ERROR] not found settings: "%SETTINGS%" >> "%LAUNCHLOG%" & exit /b 2)

rem ===== 残骸プロセス掃除（CSVロック対策） =====
taskkill /f /im tiktok_cli.exe /t >nul 2>nul

rem ===== 同名CSVを一旦削除（開きっぱなしだと消えない＝ロック検知） =====
del /f /q "%RUN1%\ugc_%YMD%.csv" >nul 2>nul
del /f /q "%RUN2%\ugc_%YMD%.csv" >nul 2>nul

echo [INFO] collect start  SHARDS=2  TIMEOUT=15  RETRIES=3
echo [INFO] launching workers...                                      >> "%LAUNCHLOG%"

rem === PowerShellで2ワーカーを並列起動→待機→退出コード集約（PS5.1対応版） ===
powershell -NoProfile -Command ^
  "$c1 = '""%EXE%"" collect --settings ""%SETTINGS%"" --shards 2 --shard-index 0 --out ""%RUN1%\ugc_%YMD%.csv"" --profile-dir ""%PROFILE1%"" --timeout 15 --retries 3';" ^
  "$c2 = '""%EXE%"" collect --settings ""%SETTINGS%"" --shards 2 --shard-index 1 --out ""%RUN2%\ugc_%YMD%.csv"" --profile-dir ""%PROFILE2%"" --timeout 15 --retries 3';" ^
  "$cmd1 = $c1 + ' 1>>""%LOG%\collect_w1.log"" 2>>&1';" ^
  "$cmd2 = $c2 + ' 1>>""%LOG%\collect_w2.log"" 2>>&1';" ^
  "$p1 = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $cmd1) -WindowStyle Minimized -PassThru;" ^
  "$p2 = Start-Process -FilePath 'cmd.exe' -ArgumentList @('/c', $cmd2) -WindowStyle Minimized -PassThru;" ^
  "$p1.WaitForExit(); $ec1=$p1.ExitCode; $p2.WaitForExit(); $ec2=$p2.ExitCode;" ^
  "Write-Host ('[EC] w1=' + $ec1 + ' w2=' + $ec2);" ^
  "if(($ec1 -eq 0) -and ($ec2 -eq 0)){ exit 0 } else { exit 1 }" ^
  >> "%LAUNCHLOG%" 2>>&1

if errorlevel 1 (
  echo [ERROR] one or more workers failed (see collect_w*.log) >> "%LAUNCHLOG%"
  endlocal & exit /b 1
) else (
  echo [INFO] workers finished OK. see %LOG%\collect_w*.log     >> "%LAUNCHLOG%"
  endlocal & exit /b 0
)
