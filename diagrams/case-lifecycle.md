# Case lifecycle

Production proposal; only the local kernel and demonstration workflow are implemented.

```mermaid
stateDiagram-v2
  [*] --> RECEIVED
  RECEIVED --> TRIAGE: persist and create obligation
  TRIAGE --> CLOSED_NON_ACTIONABLE: qualified rule and complete basis
  TRIAGE --> GATHERING: evidence required
  GATHERING --> WAITING: named owner and wake condition
  WAITING --> GATHERING: evidence or reminder
  GATHERING --> REVIEW_READY: complete or explicit senior QA exception
  REVIEW_READY --> SIGNING: freeze decision hash
  SIGNING --> GATHERING: evidence changed
  SIGNING --> DISPOSED: authorised signatures
  DISPOSED --> REOPENED: bulletin or new evidence
  CLOSED_NON_ACTIONABLE --> REOPENED: challenge or late evidence
  REOPENED --> GATHERING: append new episode
  note right of WAITING
    Notification timer continues
    Original signed basis never changes
  end note
```
