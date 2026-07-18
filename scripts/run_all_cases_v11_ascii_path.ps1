$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ProjectRoot = $PSScriptRoot
$Conda = "D:\Application\miniconda3\Scripts\conda.exe"
$Drive = "Q:"
$ScriptName = "qsm_qte_fate_nees_multicase_release_v11.py"

$Workers = 8
$PrepareWorkers = 2
$ChunkRows = 200000
$Stride = 5

if (-not (Test-Path $Conda)) {
    throw "Conda executable not found: $Conda"
}

$LocalScript = Join-Path $ProjectRoot $ScriptName
if (-not (Test-Path $LocalScript)) {
    throw "V11 Python script not found: $LocalScript"
}

cmd /c "subst $Drive /d" 2>$null | Out-Null

try {
    cmd /c "subst $Drive `"$ProjectRoot`""

    $MappedScript = "$Drive\$ScriptName"
    $MappedRoot = "$Drive\"
    $MappedOutput = "$Drive\outputs_qsm_qte_fate_nees_2011_1076_v11"

    Write-Host ""
    Write-Host "QSM-QTE-FATE Integrated Seismic Field Observation V11"
    Write-Host "Project mapped to: $Drive"
    Write-Host "Probe workers: $Workers"
    Write-Host "Preparation workers: $PrepareWorkers"
    Write-Host ""

    & $Conda run -n ifcman python $MappedScript `
        --root $MappedRoot `
        --out $MappedOutput `
        --stride $Stride `
        --workers $Workers `
        --prepare-workers $PrepareWorkers `
        --chunk-rows $ChunkRows

    if ($LASTEXITCODE -ne 0) {
        throw "QSM-QTE-FATE V11 failed with exit code $LASTEXITCODE"
    }

    Write-Host ""
    Write-Host "Completed."
    Write-Host "Output:"
    Write-Host (Join-Path $ProjectRoot "outputs_qsm_qte_fate_nees_2011_1076_v11")
}
finally {
    cmd /c "subst $Drive /d" 2>$null | Out-Null
}
