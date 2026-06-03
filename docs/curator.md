# Curator

The curator is the single-writer merge process for canonical shared memory.

Agents write inbox notes. The curator validates and merges accepted notes.

```bash
agent-memory status
agent-memory curate-dry-run
agent-memory curate-apply --machine laptop --agent codex
```

Current deterministic routing:

```text
preference -> memory/profile.md
project    -> memory/projects.md
lesson     -> memory/lessons.md
workflow   -> memory/workflows.md
infra      -> memory/infra.md
```

Unsafe or malformed notes move to:

```text
archive/needs_user_review/
```

Accepted notes move to:

```text
archive/accepted/
```

