# DDEX XML 驗證器

一個全面的 DDEX XML 訊息驗證工具，支援多個 DDEX 版本和自定義業務規則驗證。

[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)](https://github.com/your-org/ddex-xml-validator-python)

## 功能特點

- ✅ **多版本支援**：支援 DDEX 3.8.2 和 4.1 版本
- ✅ **XSD 架構驗證**：完整的 XML Schema 驗證
- ✅ **業務規則驗證**：DDEX 特定的業務邏輯檢查
- ✅ **識別碼驗證**：GRid、ISRC、ISAN、ICPN 等格式驗證
- ✅ **詳細錯誤報告**：包含行號、錯誤代碼和修正建議
- ✅ **多種輸出格式**：支援文字、JSON、XML、CSV 格式
- ✅ **批次處理**：支援批次驗證多個檔案
- ✅ **跨平台**：支援 Windows、Linux、macOS
- ✅ **命令列工具**：提供 PowerShell 和 Bash 腳本

## 快速開始

### 安裝

#### 方法 1：使用安裝腳本

**Windows (PowerShell):**

```powershell
git clone https://github.com/kpxx/ddex-xml-validator-python.git
cd ddex-xml-validator-python
.\scripts\install-dependencies.ps1
```

**Linux/macOS (Bash):**

```bash
git clone https://github.com/kpxx/ddex-xml-validator-python.git
cd ddex-xml-validator-python
chmod +x scripts/validate.sh
./scripts/install-dependencies.sh
```

#### 方法 2：手動安裝

```bash
# 克隆專案
git clone https://github.com/kpxx/ddex-xml-validator-python.git
cd ddex-xml-validator-python

# 安裝 Python 依賴套件
pip install -r requirements.txt

# 或手動安裝
pip install lxml xmlschema click colorama pydantic python-dateutil tabulate
```

### 基本使用

#### 1. 驗證單個檔案

**使用 PowerShell 腳本 (Windows):**

```powershell
.\scripts\validate.ps1 -Action validate -XmlFile "path\to\your\ddex-message.xml"
```

**使用 Bash 腳本 (Linux/macOS):**

```bash
./scripts/validate.sh validate "path/to/your/ddex-message.xml"
```

**直接使用 Python:**

```bash
python examples/cli_validator.py validate "path/to/your/ddex-message.xml"
```

#### 2. 批次驗證

```powershell
# Windows
.\scripts\validate.ps1 -Action batch -Directory "C:\xml\files" -OutputFormat json -OutputFile "results.json"

# Linux/macOS
./scripts/validate.sh batch "/path/to/xml/files" --output json --output-file results.json
```

#### 3. 查看檔案資訊

```powershell
# Windows
.\scripts\validate.ps1 -Action info -XmlFile "path\to\file.xml"

# Linux/macOS
./scripts/validate.sh info "path/to/file.xml"
```

## 程式化使用

### Python API

```python
from ddex_validator.validator import DDEXXMLValidator

# 建立驗證器
validator = DDEXXMLValidator()

# 驗證檔案
result = validator.validate_file("path/to/ddex-message.xml")

# 檢查結果
if result.is_valid:
    print("✅ 驗證通過！")
else:
    print("❌ 驗證失敗")
    for error in result.errors:
        print(f"錯誤: {error}")

# 驗證字串
xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<NewReleaseMessage xmlns="http://ddex.net/xml/ern/382">
    <!-- XML 內容 -->
</NewReleaseMessage>"""

result = validator.validate_string(xml_content)
```

### 自定義驗證器

```python
from ddex_validator.validator import DDEXXMLValidator

# 使用自定義 XSD 檔案
validator = DDEXXMLValidator(
    schema_path="path/to/custom.xsd",
    enable_business_rules=True,
    strict_mode=False
)

# 批次驗證
file_paths = ["file1.xml", "file2.xml", "file3.xml"]
results = validator.validate_batch(file_paths)

for result in results:
    print(f"檔案: {result.file_path}")
    print(f"狀態: {'通過' if result.is_valid else '失敗'}")
```

## 命令列選項

### validate 命令

驗證單個 XML 檔案。

```bash
python examples/cli_validator.py validate [OPTIONS] XML_FILE
```

**選項:**

- `--schema, -s`: XSD 檔案路徑
- `--schema-dir, -d`: XSD 檔案目錄
- `--no-business-rules`: 停用業務規則驗證
- `--output, -o`: 輸出格式 (text, json, xml)
- `--output-file, -f`: 輸出檔案路徑
- `--verbose, -v`: 詳細輸出

**範例:**

```bash
# 基本驗證
python examples/cli_validator.py validate message.xml

# 使用自定義 XSD
python examples/cli_validator.py validate message.xml --schema custom.xsd

# JSON 輸出
python examples/cli_validator.py validate message.xml --output json --output-file result.json

# 停用業務規則
python examples/cli_validator.py validate message.xml --no-business-rules
```

### batch 命令

批次驗證目錄中的 XML 檔案。

```bash
python examples/cli_validator.py batch [OPTIONS] DIRECTORY
```

**選項:**

- `--pattern, -p`: 檔案模式 (預設: *.xml)
- `--recursive, -r`: 遞迴搜尋子目錄
- `--continue-on-error`: 遇到錯誤時繼續處理
- `--output, -o`: 輸出格式 (text, json, csv)
- `--output-file, -f`: 輸出檔案路徑

**範例:**

```bash
# 批次驗證目錄
python examples/cli_validator.py batch /path/to/xml/files

# 遞迴搜尋並輸出 CSV
python examples/cli_validator.py batch /path/to/xml/files --recursive --output csv --output-file report.csv

# 自定義檔案模式
python examples/cli_validator.py batch /path/to/files --pattern "*.ddex"
```

### info 命令

顯示 XML 檔案的基本資訊。

```bash
python examples/cli_validator.py info XML_FILE
```

**範例:**

```bash
python examples/cli_validator.py info message.xml
```

輸出範例:

```cmd
檔案: message.xml
DDEX版本: 3.8.2
訊息類型: NewReleaseMessage
檔案大小: 15,234 bytes
行數: 456
```

## 驗證規則

### XSD 架構驗證

- XML 語法正確性
- 元素結構符合 DDEX 規範
- 資料類型驗證
- 必要元素檢查

### 業務規則驗證

#### 識別碼驗證

- **GRid**: A1 + 16個字元格式
- **ISRC**: 國家代碼 + 註冊者代碼 + 年份 + 序號
- **ISAN**: 12個十六進制字符
- **V-ISAN**: 24個十六進制字符
- **ICPN**: 12或13位數字 (UPC/EAN)

#### 格式驗證

- **時間長度**: ISO 8601 格式 (PT3M45S)
- **日期**: YYYY-MM-DD 格式
- **地區代碼**: ISO 3166-1 Alpha-2
- **語言代碼**: ISO 639-1/639-2

#### 邏輯驗證

- 資源引用一致性
- 重複識別碼檢查
- Deal 完整性驗證
- 技術參數合理性

## 輸出格式

### 文字格式

```cmd
DDEX XML驗證結果
============================================================
狀態: ❌ 失敗
訊息類型: NewReleaseMessage
DDEX版本: 3.8.2
錯誤數量: 2
警告數量: 1
驗證時間: 0.123秒

🔴 錯誤詳情:
----------------------------------------

1. [ERROR:INVALID_ISRC] 元素: /NewReleaseMessage/ResourceList/SoundRecording/SoundRecordingId/ISRC: 無效的ISRC格式: INVALID_ISRC
    上下文: ISRC值: 'INVALID_ISRC'
    建議: ISRC格式應為: 2個國家代碼 + 3個註冊者代碼 + 7個數字 (例如: USRC17607839)

2. [ERROR:MISSING_DURATION] 元素: /NewReleaseMessage/ResourceList/SoundRecording: SoundRecording建議包含Duration
    建議: 為了更好的用戶體驗，建議為SoundRecording提供Duration
```

### JSON 格式

```json
{
  "summary": {
    "is_valid": false,
    "message_type": "NewReleaseMessage",
    "ddex_version": "3.8.2",
    "errors_count": 2,
    "warnings_count": 1,
    "validation_time": 0.123
  },
  "errors": [
    {
      "severity": "ERROR",
      "message": "無效的ISRC格式: INVALID_ISRC",
      "element_path": "/NewReleaseMessage/ResourceList/SoundRecording/SoundRecordingId/ISRC",
      "error_code": "INVALID_ISRC",
      "context": "ISRC值: 'INVALID_ISRC'",
      "suggestion": "ISRC格式應為: 2個國家代碼 + 3個註冊者代碼 + 7個數字"
    }
  ]
}
```

## 專案結構

```cmd
ddex-xml-validator-python/
├── README.md
├── requirements.txt
├── ddex_3-8-2.xsd                    # 預設 XSD 檔案
├── examples/
│   ├── basic_usage.py                # 基本使用範例
│   ├── advanced_usage.py             # 進階使用範例
│   └── cli_validator.py              # 命令列工具
├── scripts/
│   ├── validate.ps1                  # PowerShell 腳本
│   ├── validate.bat                  # Windows 批次檔
│   ├── validate.sh                   # Bash 腳本
│   ├── install-dependencies.ps1      # Windows 安裝腳本
│   └── install-dependencies.sh       # Linux/macOS 安裝腳本
├── src/
│   └── ddex_validator/
│       ├── __init__.py
│       ├── validator.py              # 主驗證器
│       ├── models.py                 # 資料模型
│       ├── rules.py                  # 業務規則
│       ├── utils.py                  # 工具函數
│       └── constants.py              # 常數定義
└── tests/
    ├── test_validator.py
    ├── test_rules.py
    └── test_data/
        ├── valid/
        └── invalid/
```

## 支援的 DDEX 版本

- **DDEX 3.8.2** (完整支援)
- **DDEX 4.1** (基本支援)

## 系統需求

- **Python**: 3.7 或更高版本
- **作業系統**: Windows 10+, Linux, macOS
- **記憶體**: 建議 512MB 以上
- **磁碟空間**: 100MB

## 依賴套件

```cmd
lxml>=4.9.0
xmlschema>=2.5.0
python-dateutil>=2.8.2
pydantic>=2.0.0
click>=8.1.0
colorama>=0.4.6
tabulate>=0.9.0
```

## 效能

- **小型檔案** (< 1MB): < 100ms
- **中型檔案** (1-10MB): < 1s
- **大型檔案** (> 10MB): < 5s
- **批次處理**: 支援數百個檔案

## 疑難排解

### 常見問題

#### 1. Python 找不到模組

```bash
# 確認 Python 路徑
python -c "import sys; print(sys.path)"

# 手動添加路徑
export PYTHONPATH="${PYTHONPATH}:/path/to/ddex-xml-validator-python/src"
```

#### 2. XSD 檔案找不到

```bash
# 檢查 XSD 檔案位置
ls -la ddex_3-8-2.xsd

# 使用絕對路徑
python examples/cli_validator.py validate message.xml --schema /full/path/to/ddex_3-8-2.xsd
```

#### 3. 編碼問題

```bash
# 檢查檔案編碼
file -i your-file.xml

# 轉換編碼
iconv -f ISO-8859-1 -t UTF-8 input.xml > output.xml
```

#### 4. 記憶體不足

```bash
# 對於大型檔案，增加 Python 記憶體限制
python -X dev examples/cli_validator.py validate large-file.xml
```

### 除錯模式

```bash
# 啟用詳細輸出
python examples/cli_validator.py validate message.xml --verbose

# 使用除錯腳本
python test_validator.py
```

## 貢獻

歡迎貢獻！請遵循以下步驟：

1. Fork 這個專案
2. 建立功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交變更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 開啟 Pull Request

### 開發環境設定

```bash
# 克隆專案
git clone https://github.com/kpxx/ddex-xml-validator-python.git
cd ddex-xml-validator-python

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安裝開發依賴
pip install -r requirements.txt
pip install pytest pytest-cov black flake8

# 執行測試
pytest tests/

# 程式碼格式化
black src/ examples/ tests/

# 程式碼檢查
flake8 src/ examples/ tests/
```

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案。

## 更新日誌

### v1.0.0 (2024-01-15)

- 初始版本發布
- 支援 DDEX 3.8.2 驗證
- 完整的業務規則驗證
- 命令列工具
- 跨平台支援

## 聯絡資訊

- **專案首頁**: <https://github.com/kpxx/ddex-xml-validator-python>
- **問題回報**: <https://github.com/kpxx/ddex-xml-validator-python/issues>

## 致謝

- [DDEX](https://ddex.net/) - 數位資料交換標準
- [lxml](https://lxml.de/) - XML 處理庫
- [xmlschema](https://github.com/sissaschool/xmlschema) - XML Schema 驗證
- [Click](https://click.palletsprojects.com/) - 命令列介面框架

---

**注意**: 本工具僅用於驗證 XML 格式和結構，不保證完全符合所有 DDEX 業務需求。請參考官方 DDEX 文檔進行最終確認。
