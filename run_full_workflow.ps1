# Full workflow script - waits for data fetch, then runs report, ChatGPT validation, and position suggestions
# IMPORTANT: Start 01_fetch_stock_data.py first (or use run_full_pipeline.ps1 to run 01 then 02/03/05 in one go)
# This script monitors fetch completion, then runs: 02 -> 03 -> 05

Write-Host "=" * 80
Write-Host "FULL WORKFLOW MONITOR (02 -> 03 -> 05 after fetch)"
Write-Host "=" * 80

$fetchLog = "fetch_log.txt"
$maxWaitMinutes = 180  # Wait up to 3 hours for fetch to complete

Write-Host "`n[1/4] Waiting for data fetch to complete..."
Write-Host "   Monitoring: $fetchLog"
Write-Host "   Max wait time: $maxWaitMinutes minutes"

$startTime = Get-Date
$fetchComplete = $false

while (-not $fetchComplete) {
    $elapsed = (Get-Date) - $startTime
    
    if ($elapsed.TotalMinutes -gt $maxWaitMinutes) {
        Write-Host "`n[WARNING] Max wait time exceeded. Proceeding anyway..."
        break
    }
    
    # Check if fetch process is still running
    $fetchProcess = Get-Process python -ErrorAction SilentlyContinue | 
        Where-Object { $_.MainWindowTitle -like "*fetch*" -or (Get-Content $fetchLog -Tail 5 -ErrorAction SilentlyContinue | Select-String "Fetching data") }
    
    if (-not $fetchProcess) {
        # Check log for completion message
        $logContent = Get-Content $fetchLog -Tail 10 -ErrorAction SilentlyContinue
        if ($logContent -match "completed|finished|saved|Total.*tickers") {
            Write-Host "`n[OK] Data fetch appears to be complete!"
            $fetchComplete = $true
            break
        }
    }
    
    # Show progress
    $lastLine = Get-Content $fetchLog -Tail 1 -ErrorAction SilentlyContinue
    if ($lastLine -match '\[(\d+)/(\d+)\]') {
        $current = [int]$matches[1]
        $total = [int]$matches[2]
        $percent = [math]::Round(($current / $total) * 100, 1)
        Write-Host "   Progress: $current/$total ($percent%) - Elapsed: $([math]::Round($elapsed.TotalMinutes, 1)) minutes" -NoNewline
        Write-Host "`r" -NoNewline
    }
    
    Start-Sleep -Seconds 10
}

Write-Host "`n`n[2/4] Generating full report..."
python 02_generate_full_report.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Report generation failed!"
    exit 1
}

Write-Host "`n[3/4] Running ChatGPT validation..."
python 03_chatgpt_validation.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] ChatGPT validation failed!"
    exit 1
}

Write-Host "`n[4/4] Running position suggestions..."
python 05_position_suggestions.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Position suggestions failed!"
    exit 1
}

Write-Host "`n" + ("=" * 80)
Write-Host "[SUCCESS] Full workflow completed!"
Write-Host "=" * 80
Write-Host "`nCheck the reports/ directory for:"
Write-Host "  - summary_report_*.txt"
Write-Host "  - detailed_report_*.txt"
Write-Host "  - summary_Chat_GPT.txt"
Write-Host "  - position_suggestions_*.txt"