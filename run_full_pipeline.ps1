# Full pipeline: fetch data, then report, ChatGPT validation, and position suggestions
# Runs: 01_fetch_stock_data.py -> 02_generate_full_report.py -> 03_chatgpt_validation.py -> 05_position_suggestions.py

$ErrorActionPreference = "Stop"

Write-Host ("=" * 80)
Write-Host "FULL PIPELINE (Fetch + Report + ChatGPT + Position Suggestions)"
Write-Host ("=" * 80)

Write-Host "`n[1/4] Fetching stock data (force refresh)..."
python 01_fetch_stock_data.py --refresh
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Data fetch failed!"
    exit 1
}

Write-Host "`n[2/4] Generating full report..."
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
Write-Host "[SUCCESS] Full pipeline completed!"
Write-Host ("=" * 80)
Write-Host "`nCheck the reports/ directory for:"
Write-Host "  - summary_report_*.txt"
Write-Host "  - detailed_report_*.txt"
Write-Host "  - summary_Chat_GPT.txt"
Write-Host "  - position_suggestions_*.txt"
