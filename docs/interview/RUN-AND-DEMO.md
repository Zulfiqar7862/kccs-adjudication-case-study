# Install, run and demo: Windows first

Everything below was run end to end on the supplied data pack; the results are in section 5. The same commands run on Windows in CI on every push (job `interview-windows`).

## 1. Install (one time, about 5 minutes)

1. Install **Python 3.11 or newer** from <https://www.python.org/downloads/windows/>. On the first installer screen, tick **"Add python.exe to PATH"**.
2. Install **Git** from <https://git-scm.com/download/win>, or use GitHub's **Code → Download ZIP** and unzip it.
3. Open **PowerShell** (Start → type "PowerShell") and run:

```powershell
git clone https://github.com/Zulfiqar78634/kccs-adjudication-case-study.git
cd kccs-adjudication-case-study
python --version          # must print 3.11 or newer
```

If PowerShell says *"running scripts is disabled on this system"*, run this once for the current window only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 2. Run everything with one command

```powershell
.\interview.ps1
```

This creates `.venv`, installs the package, runs **all tests** and runs the **narrated lifecycle demo**. The final line should read `=== ALL STEPS PASSED ===`.

With the real data pack (keep the file outside the repository folder, because it is confidential):

```powershell
.\interview.ps1 -Workbook "C:\Users\<you>\Downloads\KCCS_Sentinel_Reference_Data_Pack.xlsx"
```

This also runs demos 2–8 below on the real data. Add `-SkipTests` during the interview to save about 20 seconds.

## 3. Or run step by step (better for explaining)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # prompt now starts with (.venv)
python -m pip install -e .\prototype

python scripts\check.py               # tests: "Ran 55 tests ... OK", then "All requested checks passed"
python -m sentinel demo --explain     # Steps 1-9 in plain English, then JSON with "result": "PASS"
```

Real data pack (`$PACK` is just a variable holding the path):

```powershell
$PACK = "C:\Users\<you>\Downloads\KCCS_Sentinel_Reference_Data_Pack.xlsx"
$DB   = "prototype\output\interview.db"     # delete this file to start again

python -m sentinel --db $DB import $PACK
python -m sentinel --db $DB assess-all --compare-history --output artifacts\private\summary.json
python -m sentinel --db $DB assess --tenant T-VIRENT --event EXC-110336 --output artifacts\private\EXC-110336.json
python -m sentinel --db $DB verify-assessment artifacts\private\EXC-110336.json
python -m sentinel --db $DB assess --tenant T-AURA --event EXC-110336                 # -> not available (tenant isolation)
python -m sentinel --db $DB assess --tenant T-VIRENT --event EXC-110336 --known-at 2026-01-01T00:00:00+00:00
python -m sentinel --db $DB report --output artifacts\private\report.json
```

Optional: run the live API and call it yourself.

```powershell
python -m sentinel sample --output prototype\output\walk\sample.xlsx
python -m sentinel --db prototype\output\walk\cases.db import prototype\output\walk\sample.xlsx
python -m sentinel credentials --tenant DEMO-ALPHA --output prototype\output\walk\creds.json
python -m sentinel --db prototype\output\walk\cases.db serve --credentials prototype\output\walk\creds.json
# second PowerShell window (activate .venv first):
python scripts\api_example.py --tenant DEMO-ALPHA --credentials prototype\output\walk\creds.json
# browser: http://127.0.0.1:8080/health     Ctrl+C stops the server
```

macOS/Linux: the same commands work with `source .venv/bin/activate` and `/` paths, or `make setup check demo`. With PowerShell installed, `pwsh ./interview.ps1` also works.

## 4. What each demo proves (what to say)

| # | You run | You see | Say this |
|---|---|---|---|
| 1 | `demo --explain` | Steps 1–9, `PASS` | "A real HTTP server and a real DB go through the full case life: premature sign blocked, evidence, review, **two independent signatures**, audit verified, reopen keeps history, reminder retry." |
| 2 | `import` | `created: 420` | "Atomic import, file hashed; importing the same file again is a no-op." |
| 3 | `assess-all` | all 420 `ABSTAIN`: 234 conflicts, 186 incomplete | "It never decides. It tells the reviewer exactly what blocks a signature. This is coverage, not accuracy." |
| 4 | `assess` one alert | 3 named conflicts (overlapping SOP revisions, vial vs syringe study, firmware bulletin) | "These are the brief's EXC-107133 problems, found automatically." |
| 5 | `verify-assessment` | valid; tampered copy → invalid | "The evidence file is hash-sealed, so QA can trust it weeks later." |
| 6 | other tenant | "not available" | "Another tenant's data is invisible, and the system does not reveal that the event exists." |
| 7 | `--known-at` | different hash | "We can replay what we knew on a past date, for an audit." |
| 8 | `report` | 28 obligations `OVERDUE` | "The regulator clock runs from the alert, independent of the case. (Overdue because today is after the pack's 2026 dates.)" |

## 5. Evidence: results on the supplied pack (2026-11-09)

```
Ran 55 tests in 19.2s  OK   (includes the private-workbook integration test)
import:  created 420, import_hash 9fe3fad7d0f7...
assess-all: total 420, ABSTAIN 420, BLOCKED_BY_CONFLICTS 234, INCOMPLETE_EVIDENCE 186, review candidates 118
EXC-110336 (T-VIRENT): ABSTAIN / BLOCKED_BY_CONFLICTS
  - SOP SOP-VIR-9115 has overlapping revisions ['Rev 04', 'Rev 05'] in force at the excursion start.
  - Product master points at study STB-4417 for a different presentation (['vial'] vs ['syringe']).
  - Logger firmware TT-2.14.3 is subject to TT-CB-114; recorded temperatures cannot be relied on ...
  assessment hash today       7c7a3e0534e4...   verify: valid; tampered copy: invalid
  assessment hash 2026-01-01  1b6163c7986f...
T-AURA asking for EXC-110336: Error: Event 'EXC-110336' is not available to tenant 'T-AURA'
report: 420 WAITING_EVIDENCE; notifications OVERDUE 28
```

Outputs are written to `artifacts\private\` and `prototype\output\`, both git-ignored, so confidential data never gets committed.

## 6. Troubleshooting

| Problem | Fix |
|---|---|
| `python` opens the Microsoft Store | Install from python.org with "Add to PATH" ticked, or use `py -3` instead of `python` |
| Scripts are disabled | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `Only one workbook snapshot is supported` | Delete `prototype\output\interview.db` (or pick another `--db`) |
| Port 8080 in use | Stop the other server, or use `serve --port 8090` |
| Credentials file already exists | Reuse it, or delete `prototype\output\walk\creds.json` |

## 7. Likely interview questions (short answers)

- **"Why not use an LLM to recommend dispositions?"** Tab 14 shows a prompt edit shifted destroy decisions from 11% to 19% across 31 tenants. The decision isn't the bottleneck; evidence is. An LLM could later draft narrative only, never decisions.
- **"Everything abstains, so is it useless?"** No. The pack lacks raw telemetry, SOP documents and batch history. Abstaining with *named* reasons is correct, and it turns 100 minutes of searching into a checklist.
- **"How does it scale?"** 2,000 real cases a month is small. Production uses PostgreSQL plus a separate deadline worker per region, and stays a modular monolith because state, audit and outbox must commit together.
- **"Change request: a new market with a 24 h window."** The window is data (`reg_window_hours` on the event row), so the obligation deadline changes without code. Today `DUE_SOON` is a fixed 24 h before the deadline; production would page at percentages (50/75/90%) of the window so short windows still get early warnings.
- **"What if two QA staff sign at once?"** `BEGIN IMMEDIATE` plus `expected_version`: one wins, the other gets 409 and must reload.
