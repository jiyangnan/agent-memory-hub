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
```

## Status

This repository is the open-source framework. User-specific memory state is created by `agent-memory setup`.

## Docs

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Adapters](docs/adapters.md)
- [Security](docs/security.md)
