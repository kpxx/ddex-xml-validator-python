@echo off
setlocal enabledelayedexpansion

REM DDEX XML驗證器 Windows批次檔

REM 取得腳本目錄
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."
set "POWERSHELL_SCRIPT=%SCRIPT_DIR%validate.ps1"

REM 檢查PowerShell腳本是否存在
if not exist "%POWERSHELL_SCRIPT%" (
    echo 錯誤: 找不到PowerShell腳本 %POWERSHELL_SCRIPT%
    exit /b 1
)

REM 檢查PowerShell是否可用
powershell -Command "Get-Host" >nul 2>&1
if errorlevel 1 (
    echo 錯誤: 需要PowerShell 5.0或更高版本
    echo 請更新Windows或安裝PowerShell Core
    exit /b 1
)

REM 執行PowerShell腳本
powershell -ExecutionPolicy Bypass -File "%POWERSHELL_SCRIPT%" %*

REM 傳遞退出代碼
exit /b %errorlevel%

