# Kubernetes deployment contract

Production scheduling is not implemented. Deploy modular case/evidence workers separately from deadline workers, with independent quotas, priority classes, health checks and disruption budgets. Regional namespaces alone are not a data-residency control: enforce network egress, identity, encrypted storage and backup placement as well.

Use immutable image digests, non-root/read-only containers, dropped capabilities, workload identity, denied default egress and tenant-aware queue policies. Readiness must fail before accepting non-durable intake; liveness must not restart healthy workers waiting on external evidence. Graceful shutdown releases leases without acknowledging incomplete work. Canary by tenant cohort with a pinned qualification manifest; rollback code/model only to an already qualified release and preserve database compatibility through expand/contract migrations.
