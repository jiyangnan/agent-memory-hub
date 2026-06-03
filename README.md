# agent memory hub

Open-source shared memory infrastructure for multi-agent, multi-device AI workflows.

`agent memory hub` helps local AI agents share durable memory safely across machines without syncing private runtime state, raw transcripts, credentials, or agent-specific databases.

The lifecycle:

```text
agent learns
  -> inbox
  -> curator
  -> canonical memory
  -> cloud handoff
  -> downstream refresh
  -> agent cold-start perception
```

## Quickstart

```bash
python3 -m pip install -e .
agent-memory setup --workspace my-agent-memory --machine laptop --adapter codex
agent-memory register-agent \
  --machine laptop \
  --agent codex \
  --adapter codex \
  --primary-memory '~/.codex/memory/shared.md'
agent-memory bootstrap --machine laptop --agent codex
agent-memory sync --machine laptop --agent codex --install-marker
agent-memory trigger "保存到共享记忆"
agent-memory trigger "拉取一下云端的记忆"
agent-memory trigger "记住这个"
agent-memory inbox-add \
  --machine laptop \
  --agent codex \
  --type lesson \
  --scope global \
  --fact "Shared memory should be curated." \
  --why "Direct canonical edits can conflict." \
  --evidence "first setup" \
  --destination memory/lessons.md
agent-memory status
agent-memory curate-dry-run
agent-memory curate-apply --machine laptop --agent codex
agent-memory cloud-status
agent-memory cloud-save --message "Update shared memory"
agent-memory cloud-push
agent-memory refresh --machine laptop --agent codex
agent-memory refresh --machine laptop --agent codex --apply
```

## Status

This repository is the open-source framework. User-specific memory state is created by `agent-memory setup`.

## Docs

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Adapters](docs/adapters.md)
- [Onboarding](docs/onboarding.md)
- [Sync](docs/sync.md)
- [Refresh](docs/refresh.md)
- [Cloud](docs/cloud.md)
- [Security](docs/security.md)
