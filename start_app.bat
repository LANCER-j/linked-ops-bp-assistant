@echo off
setlocal
cd /d "%~dp0"

if exist "%~dp0联锁对抗BP助手.exe" (
    start "" /D "%~dp0" "%~dp0联锁对抗BP助手.exe"
    exit /b 0
)

if exist "%~dp0发布版本\单文件版\联锁对抗BP助手.exe" (
    start "" /D "%~dp0发布版本\单文件版" "%~dp0发布版本\单文件版\联锁对抗BP助手.exe"
    exit /b 0
)

set "PYTHONW_PATH="
for %%P in (pythonw.exe) do set "PYTHONW_PATH=%%~$PATH:P"

if defined PYTHONW_PATH (
    start "" /D "%~dp0" "%PYTHONW_PATH%" "%~dp0launcher.pyw"
    exit /b 0
)

set "PYTHON_PATH="
for %%P in (python.exe) do set "PYTHON_PATH=%%~$PATH:P"

if defined PYTHON_PATH (
    start "" /D "%~dp0" "%PYTHON_PATH%" "%~dp0launcher.pyw"
    exit /b 0
)

echo The standalone EXE was not found, and Python 3 is not installed.
echo Please use the release version or install Python 3 with "Add Python to PATH".
pause
exit /b 1
