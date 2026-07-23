$ErrorActionPreference = "Stop"

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Output = Join-Path $RepoRoot "SHA256SUMS.txt"

$Files = @(
    git -C $RepoRoot ls-files
) | Where-Object {
    $_ -and $_ -ne "SHA256SUMS.txt" -and
    (Test-Path (Join-Path $RepoRoot $_) -PathType Leaf)
} | Sort-Object -Unique

$Lines = foreach ($RelativePath in $Files) {
    $FullPath = Join-Path $RepoRoot $RelativePath
    $Hash = (Get-FileHash -LiteralPath $FullPath -Algorithm SHA256).Hash.ToLowerInvariant()
    "$Hash  $($RelativePath -replace '\\','/')"
}

Set-Content -LiteralPath $Output -Value $Lines -Encoding UTF8
Write-Host "Updated: $Output"
Write-Host "Files hashed: $($Lines.Count)"
