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

## 3. Register An Agent

```bash
agent-memory register-agent \
  --machine laptop \
  --agent codex \
  --adapter codex \
  --primary-memory '~/.codex/memory/shared.md'
```

## 4. Install The Managed Memory Section

```bash
agent-memory sync \
  --machine laptop \
  --agent codex \
  --install-marker
```

This adds the shared-memory marker block to the agent's memory file and keeps the rest of that file local.

## 5. Classify Memory Intent

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

## 6. Write An Inbox Note

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

## 7. Curate And Save

```bash
agent-memory status
agent-memory curate-dry-run
agent-memory curate-apply --machine laptop --agent codex
agent-memory cloud-save --message "Update shared memory"
agent-memory cloud-push
```

## 8. Refresh Downstream Memory

```bash
agent-memory refresh --machine laptop --agent codex
agent-memory refresh --machine laptop --agent codex --apply
```
