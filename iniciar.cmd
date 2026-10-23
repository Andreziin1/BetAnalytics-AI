@echo off
cd /d "%~dp0"
py scripts\start_local.py
if errorlevel 1 pause
