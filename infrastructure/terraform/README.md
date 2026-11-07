# Terraform implementation contract

No resources are applied by this case study. Implement one independently governed stack per permitted residency cell, using remote encrypted/locked state within that geography. Modules should own network boundaries, multi-AZ PostgreSQL, encrypted broker/outbox infrastructure, versioned Object-Lock buckets, tenant KMS keys and workload identities.

Use least-privilege service roles: compiler reads only approved tenant evidence, signer writes frozen bundles, obligation worker accesses only duties/receipts, and global control receives health/version metadata only. Prevent cross-region backups and accidental public buckets through policy-as-code. Require a reviewed plan, drift checks, restore drill and destructive-change approval before apply. Separate data-retention locks from routinely replaceable compute to avoid destroying audit evidence during rollback.
