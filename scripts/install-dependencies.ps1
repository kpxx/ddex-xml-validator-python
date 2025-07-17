<#
.SYNOPSIS
    安裝DDEX XML驗證器的依賴套件

.DESCRIPTION
    自動安裝Python依賴套件和設定環境
#>

[CmdletBinding()]
param(
    [switch]$Force,
    [switch]$Upgrade
)

# 顏色輸出函數 - 修正版本
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    # 定義有效的顏色映射
    $validColors = @{
        "Red" = "Red"
        "Green" = "Green"
        "Yellow" = "Yellow"
        "Blue" = "Blue"
        "Cyan" = "Cyan"
        "Magenta" = "Magenta"
        "White" = "White"
        "Gray" = "Gray"
        "DarkGray" = "DarkGray"
    }
    
    # 確保顏色值有效
    if (-not $validColors.ContainsKey($Color)) {
        $Color = "White"
    }
    
    try {
        Write-Host $Message -ForegroundColor $validColors[$Color]
    }
    catch {
        # 如果顏色輸出失敗，使用普通輸出
        Write-Host $Message
    }
}

Write-ColorOutput "DDEX XML驗證器 - 依賴套件安裝程式" "Cyan"
Write-ColorOutput ("=" * 50) "Cyan"

# 檢查Python
try {
    # 嘗試不同的Python命令
    $pythonCmd = $null
    $pythonExecutable = $null
    
    # 檢查python命令
    try {
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if ($pythonCmd) {
            $pythonExecutable = "python"
        }
    } catch {}
    
    # 如果python不存在，嘗試python3
    if (-not $pythonCmd) {
        try {
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
            if ($pythonCmd) {
                $pythonExecutable = "python3"
            }
        } catch {}
    }
    
    if (-not $pythonExecutable) {
        throw "Python not found"
    }
    
    $pythonVersion = & $pythonExecutable --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python execution failed"
    }
    
    Write-ColorOutput "✓ 找到Python: $pythonVersion" "Green"
    Write-ColorOutput "  使用命令: $pythonExecutable" "Gray"
}
catch {
    Write-ColorOutput "✗ 錯誤: 需要安裝Python 3.7或更高版本" "Red"
    Write-ColorOutput "請從 https://www.python.org/downloads/ 下載並安裝" "Yellow"
    exit 1
}

# 檢查pip
try {
    # 嘗試不同的pip命令
    $pipExecutable = $null
    
    # 檢查pip命令
    try {
        $pipCmd = Get-Command pip -ErrorAction SilentlyContinue
        if ($pipCmd) {
            $pipExecutable = "pip"
        }
    } catch {}
    
    # 如果pip不存在，嘗試pip3
    if (-not $pipExecutable) {
        try {
            $pipCmd = Get-Command pip3 -ErrorAction SilentlyContinue
            if ($pipCmd) {
                $pipExecutable = "pip3"
            }
        } catch {}
    }
    
    # 如果還是沒有，嘗試python -m pip
    if (-not $pipExecutable) {
        try {
            $result = & $pythonExecutable -m pip --version 2>&1
            if ($LASTEXITCODE -eq 0) {
                $pipExecutable = "$pythonExecutable -m pip"
            }
        } catch {}
    }
    
    if (-not $pipExecutable) {
        throw "pip not found"
    }
    
    if ($pipExecutable -like "*-m pip") {
        $pipVersion = & $pythonExecutable -m pip --version 2>&1
    } else {
        $pipVersion = & $pipExecutable --version 2>&1
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "pip execution failed"
    }
    
    Write-ColorOutput "✓ 找到pip: $pipVersion" "Green"
    Write-ColorOutput "  使用命令: $pipExecutable" "Gray"
}
catch {
    Write-ColorOutput "✗ 錯誤: pip未安裝或無法執行" "Red"
    Write-ColorOutput "請確認Python安裝包含pip，或手動安裝pip" "Yellow"
    exit 1
}

# 安裝依賴套件
$packages = @(
    "lxml>=4.9.0",
    "xmlschema>=2.5.0", 
    "python-dateutil>=2.8.2",
    "pydantic>=2.0.0",
    "click>=8.1.0",
    "colorama>=0.4.6",
    "tabulate>=0.9.0"
)

Write-ColorOutput "正在安裝Python依賴套件..." "Blue"
Write-ColorOutput "總共需要安裝 $($packages.Count) 個套件" "Blue"

$successCount = 0
$failCount = 0

foreach ($package in $packages) {
    Write-ColorOutput "正在安裝 $package..." "Yellow"
    
    try {
        # 建構安裝命令
        if ($pipExecutable -like "*-m pip") {
            $installCmd = @($pythonExecutable, "-m", "pip", "install")
        } else {
            $installCmd = @($pipExecutable, "install")
        }
        
        if ($Force) { 
            $installCmd += "--force-reinstall" 
        }
        if ($Upgrade) { 
            $installCmd += "--upgrade" 
        }
        
        $installCmd += $package
        
        # 執行安裝命令
        Write-ColorOutput "  執行: $($installCmd -join ' ')" "Gray"
        
        $output = & $installCmd[0] $installCmd[1..($installCmd.Length-1)] 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "  ✓ $package 安裝成功" "Green"
            $successCount++
        } else {
            Write-ColorOutput "  ✗ $package 安裝失敗" "Red"
            Write-ColorOutput "  錯誤輸出: $output" "Red"
            $failCount++
        }
    }
    catch {
        Write-ColorOutput "  ✗ 安裝 $package 時發生例外: $($_.Exception.Message)" "Red"
        $failCount++
    }
    
    Write-ColorOutput "" # 空行分隔
}

# 顯示安裝結果
Write-ColorOutput ("=" * 50) "Cyan"
Write-ColorOutput "安裝結果摘要:" "Cyan"
Write-ColorOutput "成功安裝: $successCount 個套件" "Green"
Write-ColorOutput "安裝失敗: $failCount 個套件" "Red"

if ($failCount -eq 0) {
    Write-ColorOutput "✓ 所有依賴套件安裝完成！" "Green"
    Write-ColorOutput "現在可以使用 .\scripts\validate.ps1 來驗證DDEX XML檔案" "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "範例用法:" "Yellow"
    Write-ColorOutput "  .\scripts\validate.ps1 -Action help" "White"
    Write-ColorOutput "  .\scripts\validate.ps1 -Action validate -XmlFile 'path\to\file.xml'" "White"
} else {
    Write-ColorOutput "✗ 部分套件安裝失敗，請檢查錯誤訊息" "Red"
    Write-ColorOutput "您可以嘗試手動安裝失敗的套件:" "Yellow"
    Write-ColorOutput "  $pipExecutable install <package_name>" "White"
}

Write-ColorOutput ("=" * 50) "Cyan"

# 驗證安裝 - 使用Here-String避免解析問題
Write-ColorOutput "正在驗證安裝..." "Blue"

$verificationFailed = $false
$corePackages = @("lxml", "xmlschema", "click", "colorama")

foreach ($package in $corePackages) {
    try {
        # 使用Here-String避免PowerShell解析問題
        $pythonCode = @"
import $package
print("$package verification OK")
"@
        
        # 創建臨時檔案來執行Python代碼
        $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
        $pythonCode | Out-File -FilePath $tempFile -Encoding UTF8
        
        $result = & $pythonExecutable $tempFile 2>&1
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
        
        if ($LASTEXITCODE -eq 0 -and $result -like "*verification OK*") {
            Write-ColorOutput "  ✓ $package 驗證通過" "Green"
        } else {
            Write-ColorOutput "  ✗ $package 驗證失敗: $result" "Red"
            $verificationFailed = $true
        }
    }
    catch {
        Write-ColorOutput "  ✗ $package 驗證時發生錯誤: $($_.Exception.Message)" "Red"
        $verificationFailed = $true
    }
}

if (-not $verificationFailed) {
    Write-ColorOutput "✓ 所有核心套件驗證通過！" "Green"
    exit 0
} else {
    Write-ColorOutput "✗ 部分套件驗證失敗，請檢查安裝" "Red"
    exit 1
}

