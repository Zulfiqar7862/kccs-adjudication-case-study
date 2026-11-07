# Production infrastructure boundary

The Dockerfile and compose definition run the local kernel. The regional architecture is a proposal, not a production deployment. Do not mistake the Terraform/Kubernetes notes for applied infrastructure.

Before provisioning, agree residency/processor terms, source authority, tenancy keys, seven-year retained-basis policy, availability targets, legal calendars and emergency filing ownership. Split ingestion throughput from case volume; reserve independent obligation worker capacity. Logs and backups obey the same region and tenant policy as source data. Use workload identity and a secret manager in production; no cloud credential is required here.

The observability directory contains an importable Grafana dashboard specification and Prometheus alert rules for the **proposed** metric contract. The CLI does not expose a metrics endpoint. Validate/export those metrics when building production services; a dashboard file alone is not monitoring.
