# The whole thing in plain English

*Read this first if you are not an engineer. Nothing here needs code.*

## The problem

A company moves medicines in refrigerated trucks and planes. Sensors in every shipment report the temperature. When a reading goes out of range, an **alert** is raised. About 11,400 alerts a month; roughly four in five turn out to be harmless (a door opened for a minute, a sensor with a flat battery).

For the real ones, a qualified person must decide what happens to the medicine: release it, release it with a note, quarantine it, send it back, or destroy it. That decision is regulated. A named human signs it and is accountable for it.

The company's problem is **not** that people decide badly. It is that before they can decide, they spend about an hour and a half per case hunting through seven different systems for the evidence — which procedure applied that day, what the product's stability study allows, whether the sensor was trustworthy, who is allowed to sign, which carrier contract governs the claim. And after they decide, the reasoning is not kept: months later, an inspector asks "show me what you relied on" and the company can only produce the outcome.

Two more things make it hard:

- **A regulatory clock.** In some markets the regulator must be told about a deviation within 72 hours of the alert, no matter how long the decision takes. Those are two separate clocks on the same case, and fourteen notifications were late last half-year because the case was stuck in a queue behind a flat battery.
- **Thirty-four customers who must never see each other's data.** Two of them are direct competitors, and one contract says nothing built from its data may ever serve another customer.

## What we built

A small, working program that does the evidence hunt — carefully — and refuses to pretend.

Give it one alert and it answers, in a fixed structure:

1. **What is this?** Which product, which facilities, which carrier contract — found only in *this customer's own* records. If the name on the alert matches nothing, or matches two things, it says so instead of guessing.
2. **Which procedure applied that day?** It picks the procedure revisions in force at the moment the temperature went out of range. If two revisions overlap on that day (and in this data they often do), it reports a **conflict** for the document-control team to settle. It never silently picks "the newest".
3. **Which stability study is relevant?** It checks the study belongs to this customer (by the ownership column, not by which folder it was found in), that it is for the same presentation (a vial study does not cover a syringe), and that it is readable and actually answers the question "how long may this sit warm". If not, it says why it is not usable.
4. **Can the temperature readings be trusted?** If the sensor's firmware is covered by a calibration bulletin, it says the readings may be wrong by *up to* a stated amount and that the exact error is unknown — it does not "correct" them.
5. **When must the regulator be told?** The clock starts when the alert arrived, not when someone decides. Waiting for evidence, reviewing, or reopening the case never pauses it.
6. **What is still missing, and what must a person do next.**

It then signs its own answer with a fingerprint. The same inputs always give the same fingerprint, so anyone can prove later that an answer was not altered.

Two things it can do that the company could not:

- **"What did we know at the time?"** Ask the same question as of an earlier date, and anything learned later (such as a calibration bulletin issued in April) disappears from the answer. That is how you answer an inspector honestly about a decision made in August of the previous year.
- **Corrections create new answers, never edited ones.** If a record is later corrected, you get a new assessment with a new fingerprint; the original stays exactly as it was.

## What it deliberately does not do

- It **never proposes a decision**. Every one of the 420 alerts in the supplied workbook ends in "abstain", with the list of what a person must settle. That is the point: the software assembles and checks evidence; the human decides.
- It does not call any AI model. The design allows one later, for writing narrative only, and never in the decision path — because the company's own history shows a prompt edit for one customer silently changed decisions for 31 others.
- It does not file anything with a regulator; it records the obligation and reminds. A reminder is not a filing.
- It does not read documents, connect to live systems, or run in the cloud. Those are designed (in the technical documents) but not built.

## What the supplied data showed

The workbook is a hand-assembled evidence pack, not a random sample, so none of these are population statistics:

- 420 alerts, all of which end in "abstain": 234 because something contradicts itself, 186 because evidence is missing.
- The most common blockers: temperature records from building systems that carry no customer tag (96), sensor firmware under a calibration bulletin (91), and overlapping procedure revisions (dozens).
- 23 products whose master record points at a stability study for a different presentation.
- 118 historical decisions were signed while one of these conflicts was open. They are *candidates for a second look*, not evidence that anyone was wrong.

## What we recommend

Start with one European customer whose contract renewal already depends on exactly this capability, in a shadow mode where the tool only assembles evidence and humans check it, for 90 days; go live only if the checks pass; then add customers in waves, hardest regulatory calendars last. Treat the board's "70% of alerts closed automatically" as closing *harmless* alerts — never as automating product decisions — and measure late notifications as a count, not an average, because an average hides the dangerous tail.

## Glossary

| Term | Meaning here |
|---|---|
| Alert / excursion | A sensor reading outside the allowed temperature range (excursion = the physical event; alert = when the system noticed it) |
| Disposition | The regulated decision about the product: release, release with note, quarantine, return, rework, destroy |
| Non-actionable closure | Closing a harmless alert without a person. Not a disposition. |
| Notification obligation | The duty to tell a regulator about a deviation within a window that starts at the alert |
| Tenant | One customer. Every record belongs to exactly one tenant and is never visible to another. |
| SOP | Standard operating procedure — the controlled document that says what limits apply and what to do |
| Stability study | A laboratory study that says how long a product tolerates being out of range |
| Presentation | The physical form of a product: vial, pre-filled syringe, pen, … |
| Calibration bulletin | A sensor vendor's notice that a firmware build reported wrong temperatures |
| As-at (valid time) | "Which rule applied at the moment it happened?" |
| Known-at (knowledge time) | "What did we know at the moment we decided?" |
| Abstain | The software's only possible conclusion: it lists evidence and problems; it does not decide |
| Fingerprint (hash) | A short code computed from the whole answer; any change to the answer changes the code |
| Evidence package | The assessment plus its fingerprints, saved as a file that can be checked later |
| Stub | A stand-in for a real external system (e.g. the regulator filing) that records the attempt but does nothing real |

## Where to go next

- Want to run it? [Quick start](../README.md#quick-start) — one command.
- Want to follow every step with real output? [Step-by-step working](17-step-by-step-working.md).
- Reviewing the submission? [Reading guide](README.md) in the order the evaluators asked for.
