# Implemented case lifecycle

These are the actual persisted prototype states. Approval quorum is policy-dependent; adding evidence invalidates review and pending signatures. Regulatory obligations remain independent throughout. The richer proposed production states are described in [case lifecycle](../docs/04-case-lifecycle.md).

```mermaid
stateDiagram-v2
    [*] --> WAITING_EVIDENCE: import
    WAITING_EVIDENCE --> WAITING_EVIDENCE: record evidence
    WAITING_EVIDENCE --> READY_FOR_REVIEW: review resolves all blockers
    READY_FOR_REVIEW --> WAITING_EVIDENCE: new evidence invalidates approvals
    READY_FOR_REVIEW --> READY_FOR_REVIEW: first signature when dual approval required
    READY_FOR_REVIEW --> DISPOSED: independent approval quorum reached
    DISPOSED --> WAITING_EVIDENCE: explicit reopen creates new revision
```

Reopening preserves the previous signed revision. A successful reminder or recorded filing receipt does not change these case states or reset the original alert clock.
