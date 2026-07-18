param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"
Set-Location $RepoRoot

if (-not (Test-Path ".git")) {
    throw "Not a Git repository: $RepoRoot"
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "Python is required to regenerate SHA256SUMS.txt from Git index blobs."
}

$Code = @'
from pathlib import Path
import hashlib
import subprocess

paths_raw = subprocess.check_output(["git", "ls-files", "-z"])
paths = [p.decode("utf-8") for p in paths_raw.split(b"\0") if p]

lines = []
for path in sorted(paths):
    if path == "SHA256SUMS.txt":
        continue
    data = subprocess.check_output(["git", "show", f":{path}"])
    digest = hashlib.sha256(data).hexdigest()
    lines.append(f"{digest}  {path}")

Path("SHA256SUMS.txt").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
    newline="\n",
)
'@

$Code | python -
if ($LASTEXITCODE -ne 0) {
    throw "SHA256 regeneration failed."
}

git add SHA256SUMS.txt

Write-Host "SHA256SUMS.txt regenerated from staged Git index blobs." -ForegroundColor Green
