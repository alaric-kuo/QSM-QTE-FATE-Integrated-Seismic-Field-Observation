param(
    [string]$DataRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) "Data Source"),
    [string]$OutputRoot = (Join-Path (Split-Path $PSScriptRoot -Parent) "outputs_qsm_qte_fate_v12_2_smoke_test"),
    [string]$Conda = "D:\Application\miniconda3\Scripts\conda.exe",
    [string]$Environment = "ifcman"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ScriptPath = Join-Path $PSScriptRoot "code\qsm_qte_fate_nees_multicase_release_v12_2.py"
if (-not (Test-Path $Conda)) { throw "Conda executable not found: $Conda" }
if (-not (Test-Path $DataRoot)) { throw "Data Source folder not found: $DataRoot" }
if (-not (Test-Path $ScriptPath)) { throw "V12.2 script not found: $ScriptPath" }

& $Conda run -n $Environment python $ScriptPath `
    --root $DataRoot `
    --out $OutputRoot `
    --cases morgan_hill_100_passive_off `
    --stride 20 `
    --workers 3 `
    --prepare-workers 1 `
    --chunk-rows 100000

if ($LASTEXITCODE -ne 0) {
    throw "V12.2 smoke test failed with exit code $LASTEXITCODE"
}

Write-Host "Completed: $OutputRoot"
