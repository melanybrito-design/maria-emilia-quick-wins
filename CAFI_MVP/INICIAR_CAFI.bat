@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\pythonw.exe" goto missing
if not exist "CAFI.pyw" goto missing
start "" "%~dp0runtime\pythonw.exe" "%~dp0CAFI.pyw"
exit /b 0
:missing
echo Extrae TODO el ZIP antes de abrir el asistente CAFI.
echo Conserva runtime, assets y CAFI.pyw junto a este archivo.
pause
exit /b 1
