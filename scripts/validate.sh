#!/bin/bash
# DDEX XML驗證腳本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
CLI_TOOL="$PROJECT_DIR/examples/cli_validator.py"

# 檢查Python是否安裝
if ! command -v python3 &> /dev/null; then
    echo "錯誤: 需要安裝Python 3"
    exit 1
fi

# 檢查CLI工具是否存在
if [ ! -f "$CLI_TOOL" ]; then
    echo "錯誤: 找不到CLI工具 $CLI_TOOL"
    exit 1
fi

# 執行CLI工具
python3 "$CLI_TOOL" "$@"

