# Onboarding New Machines And Agents

This guide explains how a new machine or a new local agent joins an existing `agent memory hub`.

## Roles

- The shared memory repository is the source of truth.
- Each machine has one or more registered agents.
- Each registered agent has one inbox path and one native memory target.
- The curator is the only process that merges inbox notes into canonical memory.

## Add A New Machine

Clone or fork your shared-memory repository, then run:

```bash
python3 -m pip install -e .
agent-memory cloud-pull
```

If the repository has no remote yet, add one with Git first.

## Register A New Agent

```bash
agent-memory register-agent \
  --machine macbook \
  --agent codex \
  --adapter codex \
  --primary-memory '~/.codex/memory/shared.md'
```

The command updates `registry/agents.json` and creates `inbox/macbook/codex/`.

## Install The Managed Section

```bash
agent-memory sync \
  --machine macbook \
  --agent codex \
  --install-marker
```

This prepares the agent's native memory file. The hub only edits the section between:

```text
<!-- agent-memory-hub:BEGIN shared -->
<!-- agent-memory-hub:END shared -->
```

## Pull Shared Memory Down

Preview first:

```bash
agent-memory refresh \
  --machine macbook \
  --agent codex
```

Apply after reviewing the JSON preview:

```bash
agent-memory refresh \
  --machine macbook \
  --agent codex \
  --apply
```

## Send New Shared Memory Up

When the user says `保存到共享记忆` or `同步给其他 agent`, write an inbox note:

```bash
agent-memory inbox-add \
  --machine macbook \
  --agent codex \
  --type lesson \
  --scope global \
  --fact "The durable fact or workflow to share." \
  --why "Why this helps future agents." \
  --evidence "Where this came from." \
  --destination memory/lessons.md
```

Then curate and publish:

```bash
agent-memory curate-dry-run
agent-memory curate-apply --machine macbook --agent codex
agent-memory cloud-save --message "Update shared memory"
agent-memory cloud-push
```

## Expected Feedback

Agents should tell the user:

- `inbox note created` after a successful upstream memory capture.
- `pull_blocked` when Git cannot pull safely.
- `sync_blocked` when the local target is missing, unsafe, or missing markers.
- `sync_ready` when a downstream preview is ready.
- `sync_applied` when shared memory was written into the local managed section.
