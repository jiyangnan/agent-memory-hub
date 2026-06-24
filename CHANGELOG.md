# Changelog

All notable changes to **agent-memory-hub** are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and versioning follows
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
