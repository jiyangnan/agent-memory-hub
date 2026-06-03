# Quickstart

`agent memory hub` creates a private shared-memory workspace for your own agents.

## 1. Install

```bash
python3 -m pip install -e .
```

## 2. Initialize Your Workspace

```bash
agent-memory setup \
  --workspace my-agent-memory \
  --machine laptop \
  --adapter codex
```

This creates:

```text
agentmemory.yaml
memory/
registry/
inbox/
.curator/
```

## 3. Classify Memory Intent

```bash
agent-memory trigger "保存到共享记忆"
agent-memory trigger "拉取一下云端的记忆"
agent-memory trigger "记住这个"
```

Expected results:

```text
shared
refresh
local
```

## 4. Write An Inbox Note

```bash
agent-memory inbox-add \
  --machine laptop \
  --agent codex \
  --type lesson \
  --scope global \
  --fact "Shared memory should be curated." \
  --why "Direct canonical edits can conflict." \
  --evidence "quickstart" \
  --destination memory/lessons.md
```

