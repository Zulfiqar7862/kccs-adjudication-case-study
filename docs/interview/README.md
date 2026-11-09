# Interview pack: start here

Three short documents, in the order to read them:

1. **[HLD.md](HLD.md)**: the problem, what was built and why, the architecture diagram and key decisions (5 minutes).
2. **[LLD.md](LLD.md)**: tables, state machine, request flow, assessment algorithm, clock, hash chain and API, each mapped to the code (15 minutes).
3. **[RUN-AND-DEMO.md](RUN-AND-DEMO.md)**: Windows install, the one-command demo (`.\interview.ps1`), what to say at each step, evidence from the real pack, and likely questions.

## A 20-minute walkthrough script

| Minutes | Show | Point |
|---|---|---|
| 0–3 | HLD §1 | "The decision is easy; assembling evidence is the cost (EXC-107133: 10 min answer, 100 min proof)." |
| 3–6 | HLD §2 | What I built, and what I deliberately did not (no auto-decide, no fuzzy match, no microservices). |
| 6–9 | HLD §3 diagram | Five components; only the Engine writes; the clock is separate from the case. |
| 9–14 | `.\interview.ps1 -Workbook <pack> -SkipTests` | Lifecycle demo, then the real pack: 420 abstain with named reasons, tamper check, tenant isolation, known-at replay. |
| 14–18 | LLD §3–4 | State machine and one transactional write (version, idempotency, audit). |
| 18–20 | HLD §4, §6 | Path to production and how failures would be detected. |

The longer original documents (`docs/00`–`17`) remain the full submission; this folder is the simplified view of them.
