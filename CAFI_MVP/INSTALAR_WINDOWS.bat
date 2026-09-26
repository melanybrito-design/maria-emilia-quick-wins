@echo off
setlocal
cd /d "%~dp0"
echo CAFI incluye Python y sus bibliotecas. No requiere instalacion con pip.
echo Comprobando los componentes locales...
call DIAGNOSTICO_WINDOWS.bat
exit /b %ERRORLEVEL%
