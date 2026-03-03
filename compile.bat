@echo off
echo ============================================
echo  Pacer Prank - EXE Compiler
echo ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python first.
    pause
    exit /b 1
)

:: Find the mp3 file in the same folder as this script
set MP3_FILE=
for %%f in ("%~dp0*.mp3") do (
    set MP3_FILE=%%f
    goto :found_mp3
)

:found_mp3
if "%MP3_FILE%"=="" (
    echo [ERROR] No .mp3 file found in this folder.
    echo         Put your pacer .mp3 here next to compile.bat and try again.
    pause
    exit /b 1
)

echo [OK] Found MP3: %MP3_FILE%
echo.

:: Install dependencies
echo [1/3] Installing dependencies...
pip install pyinstaller pygame pyautogui psutil --quiet
if errorlevel 1 (
    echo [ERROR] pip install failed.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.
echo.

:: Compile - bundle the mp3 with --add-data
echo [2/3] Compiling pacer_prank.py with bundled MP3...
echo.

pyinstaller ^
    --onefile ^
    --noconsole ^
    --name "pacer_prank" ^
    --add-data "%MP3_FILE%;." ^
    --hidden-import pygame ^
    --hidden-import pyautogui ^
    --hidden-import psutil ^
    --hidden-import ctypes ^
    --hidden-import tkinter ^
    --hidden-import glob ^
    --collect-all pygame ^
    "%~dp0pacer_prank.py"

if errorlevel 1 (
    echo.
    echo [ERROR] Compilation failed. See errors above.
    pause
    exit /b 1
)

echo.
echo [3/3] Done!
echo.
echo ============================================
echo  Output: dist\pacer_prank.exe
echo  MP3 bundled: %MP3_FILE%
echo.
echo  The exe is fully self-contained.
echo  No mp3 or Python needed on the target PC.
echo ============================================
echo.
pause
