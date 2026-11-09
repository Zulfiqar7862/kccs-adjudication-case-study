<#
.SYNOPSIS
  One command for the interview: set up, run all tests, run the narrated demo and,
  if you pass the data pack, show the evidence on the real workbook.

.EXAMPLE
  .\interview.ps1
  .\interview.ps1 -Workbook C:\path\KCCS_Sentinel_Reference_Data_Pack.xlsx
  .\interview.ps1 -Workbook C:\path\pack.xlsx -SkipTests
#>
param(
    [string]$Workbook,
    [string]$Tenant = 'T-VIRENT',
    [string]$OtherTenant = 'T-AURA',
    [string]$EventId = 'EXC-110336',
    [switch]$SkipTests
)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot
Push-Location $Root

function Section($title) { Write-Host ''; Write-Host "=== $title ===" -ForegroundColor Cyan }
function Run([string[]]$arguments, [int]$expected = 0) {
    Write-Host "> python $($arguments -join ' ')" -ForegroundColor DarkGray
    & $Python @arguments
    if ($LASTEXITCODE -ne $expected) { throw "Expected exit code $expected, got $LASTEXITCODE" }
}

try {
    # Windows venvs use Scripts\, macOS/Linux use bin/.
    $Python = Join-Path $Root '.venv/Scripts/python.exe'
    if (-not (Test-Path $Python)) { $Python = Join-Path $Root '.venv/bin/python' }
    if (-not (Test-Path $Python)) {
        Section 'Creating virtual environment (.venv)'
        if (Get-Command py -ErrorAction SilentlyContinue) { py -3 -m venv .venv } else { python -m venv .venv }
        if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ is required: install it from python.org and tick "Add to PATH"' }
        $Python = Join-Path $Root '.venv/Scripts/python.exe'
        if (-not (Test-Path $Python)) { $Python = Join-Path $Root '.venv/bin/python' }
    }
    Section 'Installing the sentinel package'
    & $Python -m pip install --quiet --disable-pip-version-check -e ./prototype
    if ($LASTEXITCODE -ne 0) { throw 'Package installation failed' }
    Run @('--version')

    if (-not $SkipTests) {
        Section 'Running the automated tests'
        if ($Workbook) { $env:SENTINEL_WORKBOOK = (Resolve-Path $Workbook).Path }
        try { Run @('scripts/check.py') } finally { Remove-Item Env:SENTINEL_WORKBOOK -ErrorAction SilentlyContinue }
    }

    Section 'Demo 1: full case lifecycle over HTTP (fictional data)'
    Run @('-m', 'sentinel', 'demo', '--explain')

    if ($Workbook) {
        $Pack = (Resolve-Path $Workbook).Path
        $Out = Join-Path $Root 'artifacts/private/interview'
        $Db = Join-Path $Root 'prototype/output/interview.db'
        New-Item -ItemType Directory -Force -Path $Out | Out-Null
        # Generated database only; a new snapshot needs a fresh database.
        Remove-Item "$Db*" -ErrorAction SilentlyContinue

        Section 'Demo 2: import the real data pack'
        Run @('-m', 'sentinel', '--db', $Db, 'import', $Pack)

        Section 'Demo 3: assess every alert (expect: all ABSTAIN with named reasons)'
        Run @('-m', 'sentinel', '--db', $Db, 'assess-all', '--compare-history', '--output', "$Out/assessment-summary.json")
        $summary = Get-Content "$Out/assessment-summary.json" -Raw | ConvertFrom-Json
        Write-Host "Total alerts:      $($summary.total)"
        Write-Host "Readiness:         $($summary.readiness | ConvertTo-Json -Compress)"
        Write-Host "Disposition:       $($summary.disposition | ConvertTo-Json -Compress)"
        Write-Host "Review candidates: $($summary.review_candidates.count) (historical decision vs open conflicts)"

        Section "Demo 4: one alert in detail ($EventId for $Tenant)"
        Run @('-m', 'sentinel', '--db', $Db, 'assess', '--tenant', $Tenant, '--event', $EventId, '--output', "$Out/$EventId.json")
        $package = Get-Content "$Out/$EventId.json" -Raw | ConvertFrom-Json
        Write-Host "Conclusion: $($package.assessment.conclusion.disposition) / $($package.assessment.conclusion.readiness)"
        Write-Host 'Conflicts:'
        $package.assessment.conflicts | ForEach-Object { Write-Host "  - $_" }
        Write-Host "Assessment hash: $($package.assessment.assessment_sha256)"

        Section 'Demo 5: package verifies; a tampered copy fails'
        Run @('-m', 'sentinel', '--db', $Db, 'verify-assessment', "$Out/$EventId.json")
        $package.assessment.event_id = 'EXC-TAMPERED'
        $package | ConvertTo-Json -Depth 100 | Set-Content "$Out/tampered.json" -Encoding utf8
        Run @('-m', 'sentinel', '--db', $Db, 'verify-assessment', "$Out/tampered.json") 1

        Section "Demo 6: tenant isolation ($OtherTenant asks for $Tenant's alert -> not found)"
        Run @('-m', 'sentinel', '--db', $Db, 'assess', '--tenant', $OtherTenant, '--event', $EventId) 1

        Section 'Demo 7: knowledge cutoff (what did we know on 2026-01-01?) -> different hash'
        Run @('-m', 'sentinel', '--db', $Db, 'assess', '--tenant', $Tenant, '--event', $EventId,
              '--known-at', '2026-01-01T00:00:00+00:00', '--output', "$Out/$EventId-known-2026-01-01.json")
        $early = Get-Content "$Out/$EventId-known-2026-01-01.json" -Raw | ConvertFrom-Json
        Write-Host "Today's hash:      $($package.assessment.assessment_sha256)"
        Write-Host "2026-01-01 hash:   $($early.assessment.assessment_sha256)"

        Section 'Demo 8: regulator notification clock (independent of case state)'
        Run @('-m', 'sentinel', '--db', $Db, 'report', '--output', "$Out/report.json")
        $report = Get-Content "$Out/report.json" -Raw | ConvertFrom-Json
        Write-Host "Cases by state:       $($report.states | ConvertTo-Json -Compress)"
        Write-Host "Notification status:  $($report.notification_status | ConvertTo-Json -Compress)"
        Write-Host "Outputs (private, git-ignored): $Out"
    }
    Section 'ALL STEPS PASSED'
} finally {
    Pop-Location
}
