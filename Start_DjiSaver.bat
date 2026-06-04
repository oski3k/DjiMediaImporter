@echo off
cd /d "%~dp0"
py main.py
if %errorlevel% neq 0 (
    python main.py
)
if %errorlevel% neq 0 (
    echo.
    echo Blad: Nie udalo sie uruchomic Pythona. Upewnij sie, ze Python jest zainstalowany.
    pause
)
