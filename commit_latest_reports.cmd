@echo off
REM Run this AFTER the full pipeline has finished to commit and push the latest reports.
REM Commits: summary_report_*.txt, summary_Chat_GPT_*.txt, position_suggestions_*.txt
REM (detailed_report_*.txt are gitignored - too large)

cd /d "%~dp0"

git add reports/
git status --short reports/
if errorlevel 1 goto :eof

git commit -m "Latest reports" -- reports/
if errorlevel 1 (
    echo Nothing to commit or commit failed.
    exit /b 1
)

git push origin main
if errorlevel 1 (
    echo Push failed.
    exit /b 1
)

echo.
echo Done. Latest reports pushed to repo.
exit /b 0
