@echo off
cd /d "%~dp0"
title IELTS FB Autoposter
python main.py
if %errorlevel% neq 0 (
    echo.
    echo [LOI] Ung dung bi dung voi ma loi %errorlevel%
    pause
)
