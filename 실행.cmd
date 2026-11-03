@echo off
chcp 65001 >nul
cd /d "%~dp0"
where py.exe >nul 2>nul
if %errorlevel% equ 0 (
    py -3 -X utf8 run_demo.py %*
) else (
    python -X utf8 run_demo.py %*
)
if errorlevel 1 pause
