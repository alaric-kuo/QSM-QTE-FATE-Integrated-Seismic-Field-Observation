$ErrorActionPreference = "Stop"

$ScriptDirectory = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDirectory
Set-Location $RepoRoot

$TrackedFiles = git ls-files |
    Where-Object {
        $_ -ne "SHA256SUMS.txt" -and
        -not $_.StartsWith(".git/")
    } |
    Sort-Object

$Lines = foreach ($RelativePath in $TrackedFiles) {
    $FullPath = Join-Path $RepoRoot $RelativePath

    if (Test-Path $FullPath -PathType Leaf) {
        $Hash = (Get-FileHash -Algorithm SHA256 -Path $FullPath).Hash.ToLowerInvariant()
        "$Hash  $($RelativePath.Replace('\', '/'))"
    }
}

$OutputPath = Join-Path $RepoRoot "SHA256SUMS.txt"
[System.IO.File]::WriteAllLines(
    $OutputPath,
    $Lines,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "Updated checksums:"
Write-Host $OutputPath
Write-Host "Files hashed: $($Lines.Count)"
