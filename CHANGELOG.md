# Changelog

All notable changes to **agent-memory-hub** are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0] — 2026-06-24

### Added
- **`agent-memory archive` subcommand** (`curator.archive_canonical_entry`). Excises a line range from a canonical memory file (`memory/*.md`) and persists the original block to `archive/superseded/<machine>/<agent>/<timestamp>-<slug>.md` with provenance frontmatter (`source_file`, `source_lines`, `supersede_reason`, `archived_by`, `archived_at`).

  Closes the architectural gap exposed by the curator being append-only: until 0.4.0, removing a superseded canonical entry required out-of-band file edits, which violated the "canonical changes only through the curator flow" rule. The new primitive makes archival a first-class curator operation.

  Usage:
  ```bash
  agent-memory archive \
    --file memory/workflows.md \
    --start-line 26 \
    --end-line 34 \
    --reason "Superseded by L35 same-day OBSOLETE declaration" \
    --archived-by laptop/codex
  ```

- **CLI `--help` groups**: required flags now appear under their own `required arguments` section in every subcommand's help output, separated from optional flags. Previously argparse lumped everything under `options:` and users had to run the command to discover required flags via error messages. Routed through a new `_required(parser)` helper.

- **`docs/auto-refresh.md`** session auto-refresh playbook. Optional pattern for wiring `git pull --rebase --autostash` + `agent-memory refresh --apply` into agent cold-start hooks (Claude Code, Codex, Hermes, OpenClaw). Documents the TTL-keyed marker pattern (vs the PID-leak pattern of an earlier draft) and lists known limitations explicitly.

### Tests
- 2 new tests in `tests/test_curator.py`:
  - `test_archive_canonical_entry_excises_block_and_records_provenance`
  - `test_archive_canonical_entry_rejects_invalid_inputs`
- Full suite 44/44 passing.

### Notes
- The archive primitive intentionally does NOT chain with `curate-apply`. Curate is for additions; archive is for removals. Composing both requires explicit ordering by the curator.
- Auto-refresh playbook ships as docs/, not code. The hook implementation is one bash script the user installs at `/usr/local/bin/agent-memory-autorefresh`; hub does not modify the user's home directory.

## [0.3.0] — 2026-06-24

### Added
- **Condensed downstream rendering** (`agent_memory.sync._condense_canonical`).
  When canonical memory entries contain structured `- Fact:` / `- Source:`
  fields, the downstream-sync rendering now keeps only the Fact text (truncated
  to 300 chars) and the Source tag, stripping the curator audit trail (`Why`,
  `Evidence`, `Source Perspective`, `Scope`, `Type`, `Applicability`).

  Unstructured sections (plain markdown under headings) pass through
  unchanged.

  **Empirical impact** measured on the upstream runtime: 398 → 91 lines
  (-77%) on a 14-entry canonical corpus. Keeps managed shared sections
  within cold-start context windows.

- Three new tests in `tests/test_sync.py`:
  - `test_condense_canonical_compresses_structured_entries`
  - `test_condense_canonical_passes_through_unstructured`
  - `test_render_shared_memory_uses_condensed_form`

### Why this matters
Downstream agents need to know **what** shared facts exist, not the full
curator audit trail — Why/Evidence are signals for the curator, not for
the receiving agent. Without compression, sync output grew unboundedly
and pushed managed shared sections past cold-start truncation thresholds.

### Source of change
Ported from the upstream private runtime (Ferdinand's AgentMemory)
commit `828af59 feat: 压缩渲染 — downstream sync 生成精简摘要而非完整原文`,
validated end-to-end on macmini/claude with a 77% downstream reduction
before release.

## [0.2.0] — 2026-06-07
Initial public release. See `README.md` for the full lifecycle and CLI surface.
