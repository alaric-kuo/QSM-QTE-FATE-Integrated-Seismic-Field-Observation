param(
    [string]$DataRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) "Data Source"),
    [string]$OutputRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) "outputs_qsm_qte_fate_nees_2011_1076_v12_2"),
    [string]$Conda = "D:\Application\miniconda3\Scripts\conda.exe",
    [string]$Environment = "ifcman",
    [int]$Workers = 8,
    [int]$PrepareWorkers = 2,
    [int]$ChunkRows = 200000,
    [int]$Stride = 5
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ProjectRoot = $PSScriptRoot
$ScriptPath = Join-Path $ProjectRoot "code\qsm_qte_fate_nees_multicase_release_v12_2.py"

if (-not (Test-Path $Conda)) { throw "Conda executable not found: $Conda" }
if (-not (Test-Path $DataRoot)) { throw "Data Source folder not found: $DataRoot" }
if (-not (Test-Path $ScriptPath)) { throw "V12.2 script not found: $ScriptPath" }

Write-Host ""
Write-Host "========================================================"
Write-Host " QSM-QTE-FATE Integrated Seismic Field Observation V12.2"
Write-Host "========================================================"
Write-Host "Method order : QSM -> QTE -> FATE"
Write-Host "Program      : $ScriptPath"
Write-Host "Data         : $DataRoot"
Write-Host "Output       : $OutputRoot"
Write-Host ""

& $Conda run -n $Environment python $ScriptPath `
    --root $DataRoot `
    --out $OutputRoot `
    --stride $Stride `
    --workers $Workers `
    --prepare-workers $PrepareWorkers `
    --chunk-rows $ChunkRows

if ($LASTEXITCODE -ne 0) {
    throw "V12.2 execution failed with exit code $LASTEXITCODE"
}

Write-Host ""
Write-Host "Completed: $OutputRoot"
Invoke-Item $OutputRoot
