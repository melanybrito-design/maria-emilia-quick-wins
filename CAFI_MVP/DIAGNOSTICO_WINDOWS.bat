@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\python.exe" goto missing
"runtime\python.exe" diagnostic.py
set "CAFI_RESULT=%ERRORLEVEL%"
pause
exit /b %CAFI_RESULT%
:missing
echo Extrae TODO el ZIP. Falta runtime\python.exe.
pause
exit /b 1
