# Publish V11.1

## 1. Extract the package

Extract `QSM_QTE_FATE_V11_1_Release_Package.zip` to a local folder.

## 2. Install the V11.1 files into the repository

Open PowerShell and run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

& "D:\path\to\QSM_QTE_FATE_V11_1_Release_Package\scripts\apply_v11_1_documentation.ps1" `
    -RepoRoot "D:\Github Pool\QSM-QTE-FATE-Integrated-Seismic-Field-Observation"
```

## 3. Review the change

```powershell
cd "D:\Github Pool\QSM-QTE-FATE-Integrated-Seismic-Field-Observation"

git status
git diff --check
git diff -- README.md CITATION.cff V11_1_CHANGELOG.md THEORY_IMPLEMENTATION_MAP_V11_1.md RELEASE_NOTES_V11_1.md
```

The update should change documentation only. The numerical engine and generated case artifacts should remain untouched.

## 4. Commit and push

```powershell
git add README.md `
    CITATION.cff `
    V11_1_CHANGELOG.md `
    THEORY_IMPLEMENTATION_MAP_V11_1.md `
    RELEASE_NOTES_V11_1.md

git commit -m "Release V11.1 theory and implementation disclosure"
git push origin main
```

## 5. Confirm the working tree

```powershell
git status
```

Expected:

```text
On branch main
Your branch is up to date with 'origin/main'.
nothing to commit, working tree clean
```

## 6. Create the V11.1 tag

```powershell
git tag -a v11.1.0 `
    -m "QSM-QTE-FATE Integrated Seismic Field Observation — Formal Release V11.1"

git push origin v11.1.0
```

Confirm that the tag points to the current commit:

```powershell
git rev-parse HEAD
git rev-list -n 1 v11.1.0
```

The two hashes should be identical.

## 7. Create the GitHub Release

With GitHub CLI:

```powershell
gh release create v11.1.0 `
    --repo "alaric-kuo/QSM-QTE-FATE-Integrated-Seismic-Field-Observation" `
    --title "QSM–QTE–FATE Integrated Seismic Field Observation — V11.1" `
    --notes-file "RELEASE_NOTES_V11_1.md" `
    --latest `
    --verify-tag
```

Open the published release:

```powershell
gh release view v11.1.0 `
    --repo "alaric-kuo/QSM-QTE-FATE-Integrated-Seismic-Field-Observation" `
    --web
```

## Release boundary

V11.1 is a theory-disclosure and implementation-mapping release.

```text
Numerical engine: unchanged from V11
Formal numerical outputs: unchanged from V11
Documentation and theory visibility: expanded
Recommended tag: v11.1.0
```
