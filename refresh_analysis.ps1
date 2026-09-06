# Refresh all analysis outputs after updating data/customers.csv, data/products.csv, or data/orders.csv.
param(
    [string]$PythonExe = "python"
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $projectRoot
try {
    & $PythonExe "src/analyze.py"
    if ($LASTEXITCODE -ne 0) { throw "Analysis refresh failed." }
    Write-Host "Refresh complete. Open the outputs folder or refresh the Power BI report." -ForegroundColor Green
}
finally {
    Pop-Location
}
