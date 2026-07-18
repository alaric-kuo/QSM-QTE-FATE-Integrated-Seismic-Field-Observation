param(
    [Parameter(Mandatory = $true)]
    [string]$DataRoot,

    [string]$Conda = "D:\Application\miniconda3\Scripts\conda.exe",
    [string]$EnvironmentName = "ifcman",

    [int]$Workers = 8,
    [int]$PrepareWorkers = 2,
    [int]$ChunkRows = 200000,
    [int]$Stride = 5,

    [switch]$KeepOutput
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDirectory
$PythonScript = Join-Path $RepoRoot "code\qsm_qte_fate_nees_multicase_release_v11.py"
$OutputRoot = Join-Path $RepoRoot "outputs_qsm_qte_fate_nees_2011_1076_v11"

if (-not (Test-Path $DataRoot)) {
    throw "Data directory not found: $DataRoot"
}
if (-not (Test-Path $PythonScript)) {
    throw "V11 Python script not found: $PythonScript"
}
if (-not (Test-Path $Conda)) {
    throw "Conda executable not found: $Conda"
}

$RepoDrive = "R:"
$DataDrive = "S:"

cmd /c "subst $RepoDrive /d" 2>$null | Out-Null
cmd /c "subst $DataDrive /d" 2>$null | Out-Null

try {
    cmd /c "subst $RepoDrive `"$RepoRoot`""
    cmd /c "subst $DataDrive `"$DataRoot`""

    $Arguments = @(
        "run", "-n", $EnvironmentName,
        "python",
        "$RepoDrive\code\qsm_qte_fate_nees_multicase_release_v11.py",
        "--root", "$DataDrive\",
        "--out", "$RepoDrive\outputs_qsm_qte_fate_nees_2011_1076_v11",
        "--stride", "$Stride",
        "--workers", "$Workers",
        "--prepare-workers", "$PrepareWorkers",
        "--chunk-rows", "$ChunkRows"
    )

    if ($KeepOutput) {
        $Arguments += "--keep-output"
    }

    Write-Host ""
    Write-Host "=== QSM-QTE-FATE V11 repository run ==="
    Write-Host "Repository: $RepoRoot"
    Write-Host "Data:       $DataRoot"
    Write-Host "Output:     $OutputRoot"
    Write-Host ""

    & $Conda @Arguments

    if ($LASTEXITCODE -ne 0) {
        throw "V11 failed with exit code $LASTEXITCODE"
    }

    Write-Host ""
    Write-Host "Completed:"
    Write-Host $OutputRoot
}
finally {
    cmd /c "subst $RepoDrive /d" 2>$null | Out-Null
    cmd /c "subst $DataDrive /d" 2>$null | Out-Null
}
