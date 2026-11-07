# Regional evidence architecture

Production proposal; only the local kernel and demonstration workflow are implemented.

```mermaid
flowchart TB
  Sources[Telemetry and business sources] --> Adapter[Regional adapters and raw landing]
  Manual[Controlled manual document intake] --> Adapter
  Adapter --> Registry[Tenant identity and temporal reference registry]
  Adapter --> Bus[Durable broker and transactional outbox]
  Bus --> Case[Case workflow and evidence compiler]
  Registry --> Case
  Case --> Bundle[Immutable signed basis store]
  Case --> QA[Authorised reviewer and signer]
  QA --> Case
  Case --> Search[Tenant-only retrieval and optional language adapter]
  Bus --> Clock[Independent obligation ledger and timer sweeper]
  Clock --> RA[Regulatory Affairs and approved filing channel]
  RA --> Receipt[Receipt evidence]
  Receipt --> Bundle
  Case --> Claims[Separate commercial investigation]
  Control[Global control plane - versions and health only] -. policy .-> Case
  Control -. routing .-> Adapter
```
