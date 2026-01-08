@echo off
setlocal
set ROOT=C:\Users\wduser01\Desktop\tiktokdatebase
set EXE=%ROOT%\tiktok.exe
set LOG=%ROOT%\logs
if not exist "%LOG%" mkdir "%LOG%"

rem ---- Part1 (0-14) ----
"%EXE%" run --settings "%ROOT%\initial_settings.xlsx" --offset 0 --limit 15 --per-song-timeout 300 --skip-on-timeout ^
  > "%LOG%\detail_part1.log" 2>&1

rem ---- Part2 (15-29) ----
"%EXE%" run --settings "%ROOT%\initial_settings.xlsx" --offset 15 --limit 15 --per-song-timeout 300 --skip-on-timeout ^
  > "%LOG%\detail_part2.log" 2>&1

endlocal
