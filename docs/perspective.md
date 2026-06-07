# Perspective Safety

Shared memory moves facts between different agent instances. A memory written by
`desktop/codex` may later be read by `laptop/codex`, but those two receivers are
not the same identity.

`agent memory hub` therefore preserves perspective in both directions:

```text
upstream inbox note:
  observer + applicability + source perspective

downstream managed sync:
  current receiver + source boundary
```

## Upstream Rule

Inbox notes include:

```yaml
observer: laptop/codex
applicability: all_agents
```

and a `Source Perspective` section:

```md
## Source Perspective

Observed by `laptop/codex`. Downstream receivers must not retell this as
first-person experience unless their identity matches the observer.
Applicability: `all_agents`.
```

When a rule applies across same-family agents, say so explicitly:

```text
For Codex-family agents, the expected role is...
```

Do not write ambiguous facts such as:

```text
Codex's role is...
```

unless the note is intentionally source-only:

```bash
agent-memory inbox-add ... --applicability source_only
```

## Downstream Rule

Managed sync renders an identity boundary into each receiver's memory:

```text
Current receiver: `laptop/codex`
```

Each downstream agent should treat `Source` as the observer/writer. If `Source`
differs from the current receiver, the agent should report the memory as shared
memory from that source, not as its own first-person experience.
