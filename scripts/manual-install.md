# 手動安裝指南

如果PowerShell腳本有問題，可以手動安裝依賴套件：

## 1. 檢查Python

```cmd
python --version
# 或
python3 --version
```

## 2. 安裝依賴套件

```cmd
pip install lxml xmlschema click colorama pydantic python-dateutil tabulate
# 或
python -m pip install lxml xmlschema click colorama pydantic python-dateutil tabulate

```

## 3. 驗證安裝

```cmd
python -c "import lxml; print('lxml: OK')"
python -c "import xmlschema; print('xmlschema: OK')"
python -c "import click; print('click: OK')"
python -c "import colorama; print('colorama: OK')"
```

## 4. 測試驗證器

```cmd
python examples/basic_usage.py
```


## 現在測試安裝

```powershell
# 使用修正後的安裝腳本
.\scripts\install-dependencies.ps1

# 或者使用基本版本
.\scripts\install-basic.ps1

# 或者手動安裝
pip install lxml xmlschema click colorama pydantic python-dateutil tabulate

# 安裝完成後測試
.\scripts\validate.ps1 -Action help

