@echo off
:: Check for admin rights and run server
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
    python server.py
) else (
    echo Requesting administrator privileges...
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
)
pause