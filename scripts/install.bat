@echo off
echo DDEX XML驗證器 - 依賴套件安裝
echo =============================

REM 檢查Python
echo 檢查Python環境...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    echo 找到Python命令: python
) else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
        echo 找到Python命令: python3
    ) else (
        echo 錯誤: 需要安裝Python 3.7或更高版本
        echo 請從 https://www.python.org/downloads/ 下載並安裝
        pause
        exit /b 1
    )
)

REM 顯示Python版本
%PYTHON_CMD% --version

REM 安裝依賴套件
echo.
echo 安裝依賴套件...
%PYTHON_CMD% -m pip install lxml xmlschema click colorama pydantic python-dateutil tabulate

if %errorlevel% equ 0 (
    echo.
    echo 安裝成功！
) else (
    echo.
    echo 安裝可能有問題，請檢查上面的輸出
)

REM 驗證安裝
echo.
echo 驗證安裝...
%PYTHON_CMD% -c "import lxml; print('lxml: OK')" 2>nul
%PYTHON_CMD% -c "import xmlschema; print('xmlschema: OK')" 2>nul
%PYTHON_CMD% -c "import click; print('click: OK')" 2>nul

echo.
echo 安裝完成！現在可以使用驗證器了
echo 使用方法: scripts\validate.bat -Action help
pause

