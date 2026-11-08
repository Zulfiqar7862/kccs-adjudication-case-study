$ErrorActionPreference = 'Stop'
$Root = Split-Path $PSScriptRoot -Parent
Push-Location $Root
try {
    $Python = Join-Path $Root '.venv/Scripts/python.exe'
    if (-not (Test-Path $Python)) {
        py -3 -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed' }
    }
    & $Python -m pip install -e ./prototype
    if ($LASTEXITCODE -ne 0) { throw 'Package installation failed' }
    if ($args.Count -eq 0) { & $Python -m sentinel demo }
    else { & $Python -m sentinel @args }
    if ($LASTEXITCODE -ne 0) { throw 'Sentinel command failed' }
} finally {
    Pop-Location
}
