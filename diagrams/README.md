# Design diagrams

- [Proposed production architecture](01-production-architecture.md): regional data flow, source ingestion, case review, the independent regulatory clock, and qualified delivery boundaries.
- [Case lifecycle](02-case-lifecycle.md): evidence waiting, review, signature, and explicit reopening. The regulatory clock is independent of this state flow.

The architecture diagram is proposed; the lifecycle diagram uses implemented state names. Neither is a UI map. See the [system architecture](../docs/02-system-architecture.md) and [case lifecycle](../docs/04-case-lifecycle.md) documents.

## Diagrams within the submission

The numbered documents render their diagrams inline, so evaluators do not need to leave the explanation:

| Document | Inline diagram | Status |
|---|---|---|
| [System architecture](../docs/02-system-architecture.md) | Local component flow; production data flow | Implemented / proposed, labeled separately |
| [Data model](../docs/03-data-model.md) | Tenant-scoped valid-time and recorded-time selection | Proposed production model |
| [Case lifecycle](../docs/04-case-lifecycle.md) | Evidence, review, approval and reopening | Implemented states |
| [Degradation and clock](../docs/05-degradation-and-regulatory-clock.md) | Independent obligations and outage fallback | Proposed production behavior |
| [Versioning and deployment](../docs/06-versioning-and-deployment.md) | Qualification, promotion and rollback gates | Proposed production pipeline |
| [Rollout](../docs/10-future-roadmap.md) | Bounded pilot and conditional expansion | Proposed rollout |

Maintain diagrams beside the prose they explain. The production architecture and implemented lifecycle are also retained here as standalone views; their Mermaid blocks must match the embedded versions. Keep the implemented/proposed labels and clock-independence caveats when updating either view. GitHub renders the fenced Mermaid blocks directly.
