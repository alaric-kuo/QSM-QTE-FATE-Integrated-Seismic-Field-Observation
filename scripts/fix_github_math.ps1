param(
    [string]$RepoRoot = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$MarkdownFiles = Get-ChildItem `
    -Path $RepoRoot `
    -Recurse `
    -File `
    -Filter "*.md" |
    Where-Object {
        $_.FullName -notmatch "[\\/]\.git[\\/]"
    }

$Changed = @()

foreach ($File in $MarkdownFiles) {
    $Original = [System.IO.File]::ReadAllText($File.FullName)

    # GitHub reliably renders block mathematics with $$ ... $$.
    # Convert LaTeX-style \[ ... \] blocks without touching Markdown links.
    $Updated = [System.Text.RegularExpressions.Regex]::Replace(
        $Original,
        '(?s)\\\[\s*(.*?)\s*\\\]',
        {
            param($Match)
            $Formula = $Match.Groups[1].Value.Trim()
            return "`r`n`r`n`$`$`r`n$Formula`r`n`$`$`r`n`r`n"
        }
    )

    if ($Updated -ne $Original) {
        [System.IO.File]::WriteAllText(
            $File.FullName,
            $Updated,
            [System.Text.UTF8Encoding]::new($false)
        )

        $Changed += $File.FullName.Substring($RepoRoot.Length).TrimStart("\", "/")
    }
}

Write-Host ""
Write-Host "GitHub math conversion completed."
Write-Host "Markdown files changed: $($Changed.Count)"

foreach ($RelativePath in $Changed) {
    Write-Host "  $RelativePath"
}
