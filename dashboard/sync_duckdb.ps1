# Sync DuckDB database from warehouse to Evidence sources folder
# Usage: .\sync_duckdb.ps1

$ErrorActionPreference = "Stop"

$SourceDB = "..\warehouse\chessbi.duckdb"
$DestDir = ".\sources\chessbi"
$DestDB = "$DestDir\chessbi.duckdb"

Write-Host "[Evidence Sync] Syncing DuckDB database..." -ForegroundColor Cyan

# Check if source exists
if (-not (Test-Path $SourceDB)) {
    Write-Host "[Evidence Sync] ERROR: Source database not found: $SourceDB" -ForegroundColor Red
    Write-Host "Please ensure the database exists by running:" -ForegroundColor Yellow
    Write-Host "  python warehouse/load_duckdb.py --db warehouse/chessbi.duckdb --source sample" -ForegroundColor Yellow
    exit 1
}

# Create destination directory if it doesn't exist
if (-not (Test-Path $DestDir)) {
    Write-Host "[Evidence Sync] Creating directory: $DestDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DestDir -Force | Out-Null
}

# Copy database file
Write-Host "[Evidence Sync] Copying: $SourceDB -> $DestDB" -ForegroundColor Green
Copy-Item -Path $SourceDB -Destination $DestDB -Force

$successMsg = "[Evidence Sync] Database synced successfully!"
Write-Host $successMsg -ForegroundColor Green

# Process source data
Write-Host "[Evidence Sync] Processing source data with npm run sources..." -ForegroundColor Cyan
npm run sources

Write-Host "[Evidence Sync] Complete! Start Evidence with: npm run dev" -ForegroundColor GreenndColor Cyan
