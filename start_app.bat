@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
rem Release launcher updated 2026-08-03: prefer the current packaged build.
set "PACKAGED_ENTRY=%~dp0发布版本\单文件版\联锁对抗BP助手_v0.5.1.exe"
set "SOURCE_ENTRY=%~dp0launcher.pyw"

if exist "%PACKAGED_ENTRY%" (
    start "" /D "%~dp0发布版本\单文件版" "%PACKAGED_ENTRY%"
    exit /b 0
)

set "PYTHONW_PATH="
for %%P in (pythonw.exe) do set "PYTHONW_PATH=%%~$PATH:P"

if defined PYTHONW_PATH if exist "%SOURCE_ENTRY%" (
    start "" /D "%~dp0" "%PYTHONW_PATH%" "%SOURCE_ENTRY%"
    exit /b 0
)

set "PYTHON_PATH="
for %%P in (python.exe) do set "PYTHON_PATH=%%~$PATH:P"

if defined PYTHON_PATH if exist "%SOURCE_ENTRY%" (
    start "" /D "%~dp0" "%PYTHON_PATH%" "%SOURCE_ENTRY%"
    exit /b 0
)

echo The v0.5.1 packaged build was not found and Python 3 is unavailable.
echo Copy the release package here or install Python 3 with "Add Python to PATH".
pause
exit /b 1
