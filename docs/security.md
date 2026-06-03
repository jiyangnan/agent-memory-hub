# Security

`agent memory hub` is not a secret manager, transcript archive, or filesystem sync tool.

Do not sync:

- API keys
- tokens
- cookies
- authorization headers
- SQLite databases
- browser profiles
- runtime caches
- raw session transcripts
- raw logs

Default safety mechanisms:

- secret-like content rejection
- inbox before canonical memory
- manual curation
- adapter allowlists
- managed sections
- backup before writes
- dry-run before apply

