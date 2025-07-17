<#
.SYNOPSIS
    DDEX XML驗證器 PowerShell CLI工具

.DESCRIPTION
    用於驗證DDEX XML檔案的PowerShell命令列工具，支援單檔驗證、批次驗證等功能

.PARAMETER Action
    執行的動作：validate, batch, info

.PARAMETER XmlFile
    要驗證的XML檔案路徑

.PARAMETER Directory
    批次驗證的目錄路徑

.PARAMETER Schema
    XSD檔案路徑

.PARAMETER SchemaDir
    XSD檔案目錄

.PARAMETER OutputFormat
    輸出格式：text, json, xml, csv

.PARAMETER OutputFile
    輸出檔案路徑

.PARAMETER NoBusinessRules
    停用業務規則驗證

.PARAMETER Recursive
    遞迴搜尋子目錄

.PARAMETER Pattern
    檔案搜尋模式

.PARAMETER Verbose
    詳細輸出

.PARAMETER ContinueOnError
    遇到錯誤時繼續處理

.EXAMPLE
    .\validate.ps1 -Action validate -XmlFile "C:\path\to\file.xml"

.EXAMPLE
    .\validate.ps1 -Action batch -Directory "C:\path\to\xml\files" -OutputFormat json -OutputFile "results.json"

.EXAMPLE
    .\validate.ps1 -Action info -XmlFile "C:\path\to\file.xml"
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory=$true, Position=0)]
    [ValidateSet("validate", "batch", "info", "help")]
    [string]$Action,
    
    [Parameter(Position=1)]
    [string]$XmlFile,
    
    [string]$Directory,
    [string]$Schema,
    [string]$SchemaDir,
    
    [ValidateSet("text", "json", "xml", "csv")]
    [string]$OutputFormat = "text",
    
    [string]$OutputFile,
    [switch]$NoBusinessRules,
    [switch]$Recursive,
    [string]$Pattern = "*.xml",
    [switch]$VerboseOutput,
    [switch]$ContinueOnError
)

# 設定錯誤處理
$ErrorActionPreference = "Stop"

# 取得腳本目錄
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir
$PythonCLI = Join-Path $ProjectDir "examples\cli_validator.py"

# 顏色輸出函數 - 修正版本
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    
    # 確保顏色值有效
    $validColors = @("Black", "DarkBlue", "DarkGreen", "DarkCyan", "DarkRed", "DarkMagenta", "DarkYellow", "Gray", "DarkGray", "Blue", "Green", "Cyan", "Red", "Magenta", "Yellow", "White")
    
    if ($Color -notin $validColors) {
        $Color = "White"
    }
    
    try {
        Write-Host $Message -ForegroundColor $Color
    }
    catch {
        # 如果顏色輸出失敗，使用普通輸出
        Write-Host $Message
    }
}

# 檢查Python環境
function Test-PythonEnvironment {
    try {
        # 檢查python命令
        $pythonCmd = Get-Command python -ErrorAction SilentlyContinue
        if (-not $pythonCmd) {
            # 嘗試python3
            $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
            if (-not $pythonCmd) {
                throw "Python not found"
            }
            $script:PythonExecutable = "python3"
        } else {
            $script:PythonExecutable = "python"
        }
        
        $pythonVersion = & $script:PythonExecutable --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "Python execution failed"
        }
        
        Write-ColorOutput "✓ Python環境檢查通過: $pythonVersion" "Green"
        return $true
    }
    catch {
        Write-ColorOutput "✗ 錯誤: 需要安裝Python 3.7或更高版本" "Red"
        Write-ColorOutput "請從 https://www.python.org/downloads/ 下載並安裝Python" "Yellow"
        return $false
    }
}

# 檢查依賴套件
function Test-PythonDependencies {
    $requiredPackages = @("lxml", "xmlschema", "click", "colorama")
    $missingPackages = @()
    
    foreach ($package in $requiredPackages) {
        try {
            $result = & $script:PythonExecutable -c "import $package" 2>&1
            if ($LASTEXITCODE -ne 0) {
                $missingPackages += $package
            }
        }
        catch {
            $missingPackages += $package
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-ColorOutput "✗ 缺少必要的Python套件: $($missingPackages -join ', ')" "Red"
        Write-ColorOutput "請執行以下命令安裝:" "Yellow"
        Write-ColorOutput "pip install $($missingPackages -join ' ')" "Cyan"
        return $false
    }
    
    Write-ColorOutput "✓ Python依賴套件檢查通過" "Green"
    return $true
}

# 驗證單個檔案
function Invoke-ValidateFile {
    param(
        [string]$FilePath,
        [hashtable]$Options
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-ColorOutput "✗ 錯誤: 檔案不存在 - $FilePath" "Red"
        return $false
    }
    
    Write-ColorOutput "正在驗證檔案: $FilePath" "Blue"
    
    # 建構Python命令
    $pythonArgs = @("validate", "`"$FilePath`"")
    
    if ($Options.Schema) {
        $pythonArgs += "--schema", "`"$($Options.Schema)`""
    }
    
    if ($Options.SchemaDir) {
        $pythonArgs += "--schema-dir", "`"$($Options.SchemaDir)`""
    }
    
    if ($Options.NoBusinessRules) {
        $pythonArgs += "--no-business-rules"
    }
    
    if ($Options.OutputFormat) {
        $pythonArgs += "--output", $Options.OutputFormat
    }
    
    if ($Options.OutputFile) {
        $pythonArgs += "--output-file", "`"$($Options.OutputFile)`""
    }
    
    if ($Options.VerboseOutput) {
        $pythonArgs += "--verbose"
    }
    
    # 執行Python CLI
    try {
        Write-ColorOutput "執行命令: $script:PythonExecutable $PythonCLI $($pythonArgs -join ' ')" "Gray"
        
        # 捕獲標準輸出和錯誤輸出
        $output = & $script:PythonExecutable $PythonCLI $pythonArgs 2>&1
        $exitCode = $LASTEXITCODE
        
        # 顯示輸出
        if ($output) {
            Write-ColorOutput "輸出:" "Gray"
            $output | ForEach-Object { Write-Host "  $_" }
        }
        
        if ($exitCode -eq 0) {
            Write-ColorOutput "✓ 驗證通過" "Green"
        } else {
            Write-ColorOutput "✗ 驗證失敗 (退出代碼: $exitCode)" "Red"
        }
        
        return $exitCode -eq 0
    }
    catch {
        Write-ColorOutput "✗ 執行驗證時發生錯誤: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 批次驗證
function Invoke-BatchValidate {
    param(
        [string]$DirectoryPath,
        [hashtable]$Options
    )
    
    if (-not (Test-Path $DirectoryPath -PathType Container)) {
        Write-ColorOutput "✗ 錯誤: 目錄不存在 - $DirectoryPath" "Red"
        return $false
    }
    
    Write-ColorOutput "正在批次驗證目錄: $DirectoryPath" "Blue"
    
    # 建構Python命令
    $pythonArgs = @("batch", "`"$DirectoryPath`"")
    
    if ($Options.Schema) {
        $pythonArgs += "--schema", "`"$($Options.Schema)`""
    }
    
    if ($Options.SchemaDir) {
        $pythonArgs += "--schema-dir", "`"$($Options.SchemaDir)`""
    }
    
    if ($Options.Pattern) {
        $pythonArgs += "--pattern", $Options.Pattern
    }
    
    if ($Options.Recursive) {
        $pythonArgs += "--recursive"
    }
    
    if ($Options.NoBusinessRules) {
        $pythonArgs += "--no-business-rules"
    }
    
    if ($Options.OutputFormat) {
        $pythonArgs += "--output", $Options.OutputFormat
    }
    
    if ($Options.OutputFile) {
        $pythonArgs += "--output-file", "`"$($Options.OutputFile)`""
    }
    
    if ($Options.ContinueOnError) {
        $pythonArgs += "--continue-on-error"
    }
    
    # 執行Python CLI
    try {
        Write-ColorOutput "執行命令: $script:PythonExecutable $PythonCLI $($pythonArgs -join ' ')" "Gray"
        
        $result = & $script:PythonExecutable $PythonCLI $pythonArgs
        $exitCode = $LASTEXITCODE
        
        if ($exitCode -eq 0) {
            Write-ColorOutput "✓ 批次驗證完成" "Green"
        } else {
            Write-ColorOutput "✗ 批次驗證發現問題" "Yellow"
        }
        
        return $exitCode -eq 0
    }
    catch {
        Write-ColorOutput "✗ 執行批次驗證時發生錯誤: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 顯示檔案資訊
function Show-FileInfo {
    param(
        [string]$FilePath
    )
    
    if (-not (Test-Path $FilePath)) {
        Write-ColorOutput "✗ 錯誤: 檔案不存在 - $FilePath" "Red"
        return $false
    }
    
    Write-ColorOutput "正在分析檔案: $FilePath" "Blue"
    
    # 執行Python CLI
    try {
        Write-ColorOutput "執行命令: $script:PythonExecutable $PythonCLI info `"$FilePath`"" "Gray"
        
        $result = & $script:PythonExecutable $PythonCLI "info" "`"$FilePath`""
        return $LASTEXITCODE -eq 0
    }
    catch {
        Write-ColorOutput "✗ 分析檔案時發生錯誤: $($_.Exception.Message)" "Red"
        return $false
    }
}

# 顯示幫助資訊
function Show-Help {
    Write-ColorOutput "DDEX XML驗證器 PowerShell CLI工具" "Cyan"
    Write-ColorOutput ("=" * 50) "Cyan"
    Write-ColorOutput ""
    Write-ColorOutput "用法:" "Yellow"
    Write-ColorOutput "  .\validate.ps1 -Action <action> [參數...]" "White"
    Write-ColorOutput ""
    Write-ColorOutput "動作:" "Yellow"
    Write-ColorOutput "  validate    驗證單個XML檔案" "White"
    Write-ColorOutput "  batch       批次驗證目錄中的XML檔案" "White"
    Write-ColorOutput "  info        顯示XML檔案資訊" "White"
    Write-ColorOutput "  help        顯示此幫助資訊" "White"
    Write-ColorOutput ""
    Write-ColorOutput "範例:" "Yellow"
    Write-ColorOutput "  # 驗證單個檔案" "Green"
    Write-ColorOutput "  .\validate.ps1 -Action validate -XmlFile 'C:\path\to\file.xml'" "White"
    Write-ColorOutput ""
    Write-ColorOutput "  # 批次驗證並輸出JSON結果" "Green"
    Write-ColorOutput "  .\validate.ps1 -Action batch -Directory 'C:\xml\files' -OutputFormat json -OutputFile 'results.json'" "White"
    Write-ColorOutput ""
    Write-ColorOutput "  # 遞迴批次驗證" "Green"
    Write-ColorOutput "  .\validate.ps1 -Action batch -Directory 'C:\xml\files' -Recursive -Pattern '*.xml'" "White"
    Write-ColorOutput ""
    Write-ColorOutput "  # 顯示檔案資訊" "Green"
    Write-ColorOutput "  .\validate.ps1 -Action info -XmlFile 'C:\path\to\file.xml'" "White"
    Write-ColorOutput ""
    Write-ColorOutput "參數說明:" "Yellow"
    Write-ColorOutput "  -XmlFile           XML檔案路徑" "White"
    Write-ColorOutput "  -Directory         批次驗證的目錄路徑" "White"
    Write-ColorOutput "  -Schema            XSD檔案路徑" "White"
    Write-ColorOutput "  -SchemaDir         XSD檔案目錄" "White"
    Write-ColorOutput "  -OutputFormat      輸出格式 (text, json, xml, csv)" "White"
    Write-ColorOutput "  -OutputFile        輸出檔案路徑" "White"
    Write-ColorOutput "  -NoBusinessRules   停用業務規則驗證" "White"
    Write-ColorOutput "  -Recursive         遞迴搜尋子目錄" "White"
    Write-ColorOutput "  -Pattern           檔案搜尋模式 (預設: *.xml)" "White"
    Write-ColorOutput "  -VerboseOutput     詳細輸出" "White"
    Write-ColorOutput "  -ContinueOnError   遇到錯誤時繼續處理" "White"
}

# 初始化全域變數
$script:PythonExecutable = "python"

# 主要執行邏輯
function Main {
    Write-ColorOutput "DDEX XML驗證器 v1.0.0" "Cyan"
    Write-ColorOutput ("=" * 30) "Cyan"
    
    # 檢查幫助
    if ($Action -eq "help") {
        Show-Help
        return
    }
    
    # 檢查Python環境
    if (-not (Test-PythonEnvironment)) {
        exit 1
    }
    
    # 檢查Python CLI工具
    if (-not (Test-Path $PythonCLI)) {
        Write-ColorOutput "✗ 錯誤: 找不到Python CLI工具 - $PythonCLI" "Red"
        Write-ColorOutput "請確認專案結構完整" "Yellow"
        exit 1
    }
    
    # 檢查依賴套件
    if (-not (Test-PythonDependencies)) {
        Write-ColorOutput "提示: 執行 .\scripts\install-dependencies.ps1 來安裝依賴套件" "Yellow"
        exit 1
    }
    
    # 準備選項
    $options = @{
        Schema = $Schema
        SchemaDir = $SchemaDir
        OutputFormat = $OutputFormat
        OutputFile = $OutputFile
        NoBusinessRules = $NoBusinessRules.IsPresent
        Recursive = $Recursive.IsPresent
        Pattern = $Pattern
        VerboseOutput = $VerboseOutput.IsPresent
        ContinueOnError = $ContinueOnError.IsPresent
    }
    
    # 執行對應動作
    $success = $false
    
    switch ($Action) {
        "validate" {
            if (-not $XmlFile) {
                Write-ColorOutput "✗ 錯誤: 請指定要驗證的XML檔案" "Red"
                Write-ColorOutput "用法: .\validate.ps1 -Action validate -XmlFile 'path\to\file.xml'" "Yellow"
                exit 1
            }
            $success = Invoke-ValidateFile -FilePath $XmlFile -Options $options
        }
        
        "batch" {
            if (-not $Directory) {
                Write-ColorOutput "✗ 錯誤: 請指定要批次驗證的目錄" "Red"
                Write-ColorOutput "用法: .\validate.ps1 -Action batch -Directory 'path\to\directory'" "Yellow"
                exit 1
            }
            $success = Invoke-BatchValidate -DirectoryPath $Directory -Options $options
        }
        
        "info" {
            if (-not $XmlFile) {
                Write-ColorOutput "✗ 錯誤: 請指定要分析的XML檔案" "Red"
                Write-ColorOutput "用法: .\validate.ps1 -Action info -XmlFile 'path\to\file.xml'" "Yellow"
                exit 1
            }
            $success = Show-FileInfo -FilePath $XmlFile
        }
        
        default {
            Write-ColorOutput "✗ 錯誤: 未知的動作 - $Action" "Red"
            Show-Help
            exit 1
        }
    }
    
    if (-not $success) {
        exit 1
    }
}

# 執行主函數
try {
    Main
}
catch {
    Write-ColorOutput "✗ 發生未預期的錯誤: $($_.Exception.Message)" "Red"
    if ($VerboseOutput) {
        Write-ColorOutput "堆疊追蹤:" "Yellow"
        Write-ColorOutput $_.ScriptStackTrace "Gray"
    }
    exit 1
}

