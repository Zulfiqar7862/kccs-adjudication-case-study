# Security and data handling

Sentinel is a local prototype, not a production security boundary. Treat all imported workbooks, evidence references, case notes, exports, and generated reports as potentially confidential, even when the repository itself is public.

## Public repository hygiene

- Do not commit source workbooks, PDFs, raw records, case-specific narratives, generated reports, local databases, credentials, or private test output.
- Keep private inputs outside the checkout where possible. The repository ignores common local-data formats and artifact directories; ignore rules are a safeguard, not authorization to publish those files.
- Use fictional synthetic fixtures for public examples and tests. Inspect staged files and diffs before every commit; never force-add private inputs.
- The authorized written submission may include anonymized analysis, aggregate planning assumptions and source section/sheet/row references. Do not publish source text, customer names, identifying record values or case-level incident details in documentation, fixtures, logs or commit messages.

## Local prototype controls

The HTTP server binds to loopback and uses locally generated static bearer identities. These credentials are for local development only: protect the generated credential file, keep it out of version control, and do not expose the server to a network. The prototype does not provide production identity management, TLS, secrets rotation, or a hardened deployment configuration.

Notification `tick` is an internal reminder/outbox stub, not an external delivery or regulatory-filing integration. A receipt recorded through the workflow is a human attestation and is not independently verified. Audit hash chaining detects some changes to the recorded chain but is not WORM storage and does not prove the truth or completeness of the underlying records.

The dual-signature behavior is currently selected by a local regular-expression match on policy text. It is not a validated authorization policy mechanism. Do not rely on this prototype for regulated production decisions or external filing.

## Reporting a security issue

Do not publish sensitive input data or a potentially exploitable issue in a public issue. Provide a minimal, sanitized description through the repository's private security-reporting channel, if available. Include only enough detail to reproduce the software behavior; omit real records, credentials, and private attachments.
