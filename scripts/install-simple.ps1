# 簡化版依賴安裝腳本 - 避免顏色問題
param(
    [switch]$Force,
    [switch]$Upgrade
)

Write-Host "DDEX XML驗證器 - 依賴套件安裝程式"
Write-Host "=" * 50

# 檢查Python
Write-Host "檢查Python環境..."
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $pythonVersion = python3 --version 2>&1
        $pythonCmd = "python3"
    } else {
        $pythonCmd = "python"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "找到Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "錯誤: 需要安裝Python 3.7或更高版本" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "錯誤: Python未安裝" -ForegroundColor Red
    exit 1
}

# 檢查pip
Write-Host "檢查pip..."
try {
    $pipVersion = pip --version 2>&1
    $pipCmd = "pip"
    if ($LASTEXITCODE -ne 0) {
        $pipVersion = & $pythonCmd -m pip --version 2>&1
        $pipCmd = "$pythonCmd -m pip"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "找到pip: $pipVersion" -ForegroundColor Green
    } else {
        Write-Host "錯誤: pip未安裝" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "錯誤: pip無法執行" -ForegroundColor Red
    exit 1
}

# 安裝套件
$packages = @("lxml", "xmlschema", "python-dateutil", "pydantic", "click", "colorama", "tabulate")

Write-Host "正在安裝依賴套件..."
foreach ($package in $packages) {
    Write-Host "安裝 $package..." -ForegroundColor Yellow
    
    $installArgs = @("install", $package)
    if ($Force) { $installArgs += "--force-reinstall" }
    if ($Upgrade) { $installArgs += "--upgrade" }
    
    if ($pipCmd -eq "pip") {
        $result = pip @installArgs 2>&1
    } else {
        $result = & $pythonCmd -m pip @installArgs 2>&1
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  成功安裝 $package" -ForegroundColor Green
    } else {
        Write-Host "  安裝 $package 失敗" -ForegroundColor Red
    }
}

Write-Host "安裝完成！" -ForegroundColor Green
Write-Host "現在可以使用驗證器了" -ForegroundColor Cyan

