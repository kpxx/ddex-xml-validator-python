# 基本安裝腳本 - 完全避免PowerShell語法問題
Write-Host "DDEX XML驗證器 - 基本安裝程式"
Write-Host "================================"

# 檢查Python
Write-Host "檢查Python..." -ForegroundColor Blue
$python = "python"
try {
    $version = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $python = "python3"
        $version = python3 --version 2>&1
    }
    Write-Host "找到: $version" -ForegroundColor Green
} catch {
    Write-Host "錯誤: 需要安裝Python" -ForegroundColor Red
    exit 1
}

# 安裝套件
$packages = @("lxml", "xmlschema", "click", "colorama", "pydantic", "python-dateutil", "tabulate")

Write-Host "安裝依賴套件..." -ForegroundColor Blue
foreach ($pkg in $packages) {
    Write-Host "安裝 $pkg..." -ForegroundColor Yellow
    & $python -m pip install $pkg
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  成功" -ForegroundColor Green
    } else {
        Write-Host "  失敗" -ForegroundColor Red
    }
}

# 驗證 - 完全避免冒號問題
Write-Host "驗證安裝..." -ForegroundColor Blue
foreach ($pkg in @("lxml", "xmlschema", "click")) {
    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    
    # 使用字符串拼接避免冒號問題
    $okMessage = $pkg + " verification OK"
    $pythonCode = "import $pkg`nprint('$okMessage')"
    
    $pythonCode | Out-File -FilePath $tempFile -Encoding UTF8
    
    $result = & $python $tempFile 2>&1
    Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    
    if ($result -like "*verification OK*") {
        Write-Host ($pkg + " - OK") -ForegroundColor Green
    } else {
        Write-Host ($pkg + " - FAIL") -ForegroundColor Red
    }
}

Write-Host "安裝完成！" -ForegroundColor Green

