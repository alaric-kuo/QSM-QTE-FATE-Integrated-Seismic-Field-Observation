$ErrorActionPreference = "Stop"

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"

$ProjectRoot = $PSScriptRoot
$Conda = "D:\Application\miniconda3\Scripts\conda.exe"
$Drive = "Q:"
$ScriptName = "qsm_qte_fate_nees_multicase_release_v11.py"

cmd /c "subst $Drive /d" 2>$null | Out-Null

try {
    cmd /c "subst $Drive `"$ProjectRoot`""

    & $Conda run -n ifcman python "$Drive\$ScriptName" `
        --root "$Drive\" `
        --out "$Drive\outputs_qsm_qte_fate_v11_smoke_test" `
        --cases morgan_hill_100_passive_off `
        --stride 20 `
        --workers 5 `
        --prepare-workers 1 `
        --chunk-rows 100000 `
        --allow-missing

    if ($LASTEXITCODE -ne 0) {
        throw "V11 smoke test failed with exit code $LASTEXITCODE"
    }
}
finally {
    cmd /c "subst $Drive /d" 2>$null | Out-Null
}
