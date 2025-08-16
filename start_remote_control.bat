@echo off
title PC Remote Control Server
echo.
echo ========================================
echo    PC REMOTE CONTROL - STARTING...
echo ========================================
echo.
echo Installing required packages...
py -m pip install pyautogui websockets aiohttp qrcode pillow --quiet
echo.
echo Starting server...
echo.
py remote_control_server.py
pause