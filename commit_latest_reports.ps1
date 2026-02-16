# Run this AFTER the full pipeline has finished to commit and push the latest reports.
# Commits: summary_report_*.txt, summary_Chat_GPT_*.txt, position_suggestions_*.txt, position_suggestions_Chat_GPT_*.txt
# (detailed_report_*.txt are gitignored - too large)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

git add reports/
git status --short reports/

git commit -m "Latest reports" -- reports/
if ($LASTEXITCODE -ne 0) {
    Write-Host "Nothing to commit or commit failed."
    exit 1
}

git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed."
    exit 1
}

Write-Host "`nDone. Latest reports pushed to repo."
