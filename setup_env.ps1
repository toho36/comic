# Comic Slideshow Generator - Environment Setup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Comic Generator Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Add Poppler to PATH
$popplerBinPath = "C:\Users\duckt\poppler\poppler-23.01.0\Library\bin"
if (Test-Path $popplerBinPath) {
    $env:Path = "$popplerBinPath;$env:Path"
    Write-Host "Poppler added to PATH" -ForegroundColor Green
} else {
    Write-Host "Poppler not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Current PATH status:" -ForegroundColor Yellow
pdfinfo -v 2>&1 | Select-Object -First 1
Write-Host ""
Write-Host "Ready to process comics!" -ForegroundColor Green
