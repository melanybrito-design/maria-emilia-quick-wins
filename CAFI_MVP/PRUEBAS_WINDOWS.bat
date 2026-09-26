@echo off
setlocal
cd /d "%~dp0"
if not exist "runtime\python.exe" goto missing
"runtime\python.exe" -m pytest tests/test_real_workflow.py tests/test_windows_driver.py tests/test_session_controller.py -q
set "CAFI_RESULT=%ERRORLEVEL%"
echo Estas pruebas usan datos sinteticos y NO operan CAFI.
pause
exit /b %CAFI_RESULT%
:missing
echo Extrae TODO el ZIP. Falta runtime\python.exe.
pause
exit /b 1
