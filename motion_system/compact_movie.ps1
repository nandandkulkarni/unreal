# Compact JSON Movie Files
# Usage: .\compact_movie.ps1 [filename]
# Example: .\compact_movie.ps1 tandem_run_square.json

param(
    [string]$FileName = "tandem_run_square.json"
)

# Ensure we're in the motion_system directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Add movies/ prefix if not already there
if ($FileName -notlike "movies/*") {
    $FileName = "movies/$FileName"
}

Write-Host "Compacting $FileName..." -ForegroundColor Cyan

# Run the Python script
python compact_json.py $FileName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! JSON file compacted." -ForegroundColor Green
    Write-Host ""
    Write-Host "Tip: To prevent auto-formatting in VS Code:" -ForegroundColor Yellow
    Write-Host "  1. Press Ctrl+Shift+P" -ForegroundColor Yellow
    Write-Host "  2. Type 'Preferences: Open Settings (JSON)'" -ForegroundColor Yellow
    Write-Host "  3. Add this to your settings:" -ForegroundColor Yellow
    Write-Host '     "[json]": { "editor.formatOnSave": false }' -ForegroundColor Yellow
} else {
    Write-Host "Error compacting file!" -ForegroundColor Red
}
