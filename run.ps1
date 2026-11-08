# One-command runner for Windows PowerShell. Same commands as run.sh:
#   .\run.ps1                 set up and prove everything works (tests + demo, fictional data)
#   .\run.ps1 pack FILE.xlsx  run everything against the supplied workbook
#   .\run.ps1 explain EXC-ID  explain one alert in plain English (after pack)
#   .\run.ps1 serve           start the local API on http://127.0.0.1:8080
param([string]$Command = "check", [Parameter(ValueFromRemainingArguments = $true)][string[]]$Rest)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path ".venv\Scripts\python.exe")) { Write-Host "Creating a private Python environment in .venv ..."; py -3 -m venv .venv }
$V = ".venv\Scripts\python.exe"
& $V -c "import sentinel" 2>$null
if ($LASTEXITCODE -ne 0) { Write-Host "Installing the prototype ..."; & $V -m pip install -q -r requirements.txt }

switch ($Command) {
  "check" { & $V scripts\check.py; Write-Host "`nEverything works. Next: .\run.ps1 pack C:\path\to\KCCS_Sentinel_Reference_Data_Pack.xlsx" }
  "demo" { & $V -m sentinel demo }
  "pack" {
    $Pack = $Rest[0]; if (-not $Pack -or -not (Test-Path $Pack)) { throw "usage: .\run.ps1 pack C:\path\to\pack.xlsx" }
    New-Item -ItemType Directory -Force artifacts\private, prototype\output | Out-Null
    $Sha = & $V -c "from sentinel.ingestion.workbook import sha256; print(sha256(r'$Pack')[:12])"
    $Db = "prototype\output\pack-$Sha.db"
    Set-Content prototype\output\last-pack.txt $Db
    Write-Host "1/5  Running all tests against the workbook ..."
    $env:SENTINEL_WORKBOOK = (Resolve-Path $Pack).Path
    & $V -m unittest discover -s prototype\tests 2>&1 | Select-Object -Last 3
    Remove-Item Env:SENTINEL_WORKBOOK
    Write-Host "2/5  Inspecting the workbook ..."; & $V scripts\inspect_workbook.py $Pack --output-dir artifacts\private | Out-Null
    Write-Host "3/5  Importing one snapshot ..."; & $V -m sentinel --db $Db import $Pack | Select-String '"created"|"replayed"'
    Write-Host "4/5  Choosing example alerts and running the replays ..."; & $V scripts\select_demo_cases.py --db $Db --output-dir artifacts\private | Out-Null
    Write-Host "5/5  Assessing every alert ..."; & $V -m sentinel --db $Db assess-all --compare-history --output artifacts\private\assessment-summary.json | Out-Null
    $s = Get-Content artifacts\private\assessment-summary.json | ConvertFrom-Json
    $d = Get-Content artifacts\private\demo-cases.json | ConvertFrom-Json
    Write-Host "`nAssessed $($s.total) alerts. Decisions proposed by the software: 0 (it always abstains)."
    $s.readiness.PSObject.Properties | ForEach-Object { Write-Host ("  {0,-22} {1}" -f $_.Name, $_.Value) }
    Write-Host "Example alerts chosen automatically, one per failure type:"
    $d.cases.PSObject.Properties | ForEach-Object { Write-Host ("  {0,-12} {1}" -f $_.Value.event_id, ($_.Name -replace '_', ' ')) }
    $first = ($d.cases.PSObject.Properties | Select-Object -First 1).Value.event_id
    Write-Host "`nReports: artifacts\private\workbook-inspection.md, artifacts\private\assessment-summary.json"
    Write-Host "Next: .\run.ps1 explain $first"
  }
  "explain" { & $V scripts\explain.py @Rest }
  "serve" {
    if (-not (Test-Path prototype\output\sentinel.db)) { & $V -m sentinel sample | Out-Null; & $V -m sentinel import prototype\output\sample.xlsx | Out-Null }
    if (-not (Test-Path prototype\output\local-credentials.json)) { & $V -m sentinel credentials --tenant DEMO-ALPHA --tenant DEMO-BETA | Out-Null }
    Write-Host "Credentials are in prototype\output\local-credentials.json (local only). Try: $V scripts\api_example.py"
    & $V -m sentinel serve
  }
  "help" { Get-Content $PSCommandPath | Select-Object -First 5 }
  default { & $V -m sentinel $Command @Rest }
}
