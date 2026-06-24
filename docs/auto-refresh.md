# Session Auto-Refresh Playbook

> Optional pattern: have every agent automatically pull the latest canonical shared memory and downstream-sync it into its own primary memory file at session start — so a new conversation never works against stale shared memory.

This document is **opt-in advice**, not enforced behavior. Hub does not auto-install any hooks; you decide whether to wire this into your agent and how.

## Why this exists

The manual flow looks like:

```text
1. Pull AgentMemory git → 2. agent-memory refresh --apply → 3. start agent conversation
```

In practice, most users skip step 1 and step 2 most days. The agent then perceives a managed `<!-- BEGIN/END shared -->` section that is hours-to-days out of date, while peer agents on other machines have already pushed new lessons / projects / infra entries to canonical.

Auto-refresh wraps steps 1 + 2 inside the agent's cold start, so the moment the conversation begins the perceived shared memory is current.

## Reference shell command

```bash
cd $AGENT_MEMORY_ROOT \
  && git pull --rebase --autostash --quiet 2>/dev/null \
  && ./scripts/agent-memory refresh --machine "$MACHINE" --agent "$AGENT" --apply 2>/dev/null \
  || true
```

Three deliberate choices:

| Choice | Why |
|---|---|
| `--autostash` | If you have uncommitted inbox notes, plain `git pull --rebase` aborts. `--autostash` parks them, rebases, and replays them on top — the auto-refresh stops being mutually exclusive with "I'm working on a new inbox note right now". |
| `--quiet 2>/dev/null` | Auto-refresh is best-effort. Network outages, detached HEAD, dirty worktrees with unresolvable conflicts — none of these should block the user's actual session. |
| Trailing `|| true` | The whole expression exits 0 regardless. Suitable for use in startup hooks where a non-zero exit aborts the agent. |

## Agent-specific wiring

### Claude Code

Add a `PreToolUse` hook in `~/.claude/settings.json` (or `settings.local.json`):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          {
            "type": "command",
            "command": "/usr/local/bin/agent-memory-autorefresh"
          }
        ]
      }
    ]
  }
}
```

Where `/usr/local/bin/agent-memory-autorefresh` is:

```bash
#!/bin/bash
# Run at most once per 60 seconds, regardless of how many PreToolUse hooks fire.
MARKER=/tmp/.agent-memory-autorefresh
NOW=$(date +%s)
if [ -f "$MARKER" ]; then
  LAST=$(cat "$MARKER")
  AGE=$(( NOW - LAST ))
  [ "$AGE" -lt 60 ] && exit 0
fi
echo "$NOW" > "$MARKER"

cd "$AGENT_MEMORY_ROOT" \
  && git pull --rebase --autostash --quiet 2>/dev/null \
  && agent-memory refresh --machine "$MACHINE" --agent "$AGENT" --apply 2>/dev/null
exit 0
```

Why a **TTL-keyed** marker instead of `/tmp/.agentmemory-refreshed-$$`:
- PID-keyed markers (`$$`) never clean up — `/tmp` accumulates one stale file per session until the Mac reboots. TTL files cap reuse to one per minute regardless of how many sessions.
- TTL gives you back-pressure: 60 long-running sessions in parallel issue at most one refresh per minute total.

### Codex CLI

Codex executes a `pre_session` shell hook configured in `~/.codex/config.toml`:

```toml
[hooks]
pre_session = "/usr/local/bin/agent-memory-autorefresh"
```

Same `/usr/local/bin/agent-memory-autorefresh` script as above.

### Hermes

Hermes installs its boot hook via `~/.hermes/boot.sh`. Append:

```bash
/usr/local/bin/agent-memory-autorefresh &
```

The `&` lets the rest of Hermes boot continue in parallel — auto-refresh races with the agent's normal startup and writes to the managed shared section just before the first user message is processed.

### OpenClaw

OpenClaw runs `~/.openclaw/workspace/scripts/session-start.sh` on every new session. Add at the top:

```bash
/usr/local/bin/agent-memory-autorefresh
```

OpenClaw's session-start is synchronous (it blocks the first message), so do not background it — wait for the refresh to complete so the first message sees fresh canonical memory.

## When NOT to use this

- **Offline-first deployments**: if the host machine has no internet at session start, the `git pull` blocks 5-10 seconds while ssh times out. Disable on those.
- **Air-gapped or sensitive environments**: any network reachable side effect at session start is an information leak by default. Auto-refresh against a local file:// remote is fine; against github.com is not.
- **CI / batch agents**: agents that spawn one-shot for a fixed prompt do not benefit — the cost is paid every invocation.

## Observability

To know whether auto-refresh actually ran in a given session:

```bash
agent-memory status
# In the JSON output, check `.curator.manifest_version` and compare to the
# version recorded in the agent's local memory file via:
grep AgentMemory:BEGIN <PRIMARY_MEMORY> | head -1
```

The TTL marker file is also a tell: `ls -l /tmp/.agent-memory-autorefresh` gives you the last successful auto-refresh time.

## Known limitations

- **Race condition during simultaneous pushes**: two agents on the same machine starting within 60 seconds of each other both bypass the TTL and may concurrently `git pull --rebase`. In practice this is harmless (one wins, the other gets `up_to_date`), but the corner case exists.
- **`--autostash` can still fail** if your stash contains conflicting changes against the incoming rebase. The hook logs nothing in that case — you discover staleness only when a curated entry is missing. A follow-up could write the last refresh status to `~/.agent-memory/last-refresh.json` for explicit visibility.
- **Doesn't fix `--ssh-key` / `gpg-sign` prompts**: if your git pull requires interactive auth, the hook will hang. Use `git pull --no-edit` and pre-configure non-interactive credentials.
