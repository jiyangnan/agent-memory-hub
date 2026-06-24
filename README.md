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

## Install

```bash
# Install latest release directly from GitHub
pip install git+https://github.com/jiyangnan/agent-memory-hub.git@v0.4.0

# Or pin to main
pip install git+https://github.com/jiyangnan/agent-memory-hub.git
```

> **Note on PyPI**: the name `agent-memory-hub` on PyPI is currently held by an
> unrelated placeholder package (see `pypi.org/project/agent-memory-hub/`,
> maintainer `maintainers@example.com`, homepage `github.com/example/...`).
> A PEP 541 name dispute was filed 2026-06-24 at
> [pypi/support#11216](https://github.com/pypi/support/issues/11216). Until
> that resolves, install via the GitHub URL above — release artifacts
> (wheel + sdist) are also attached to every GitHub Release for offline /
> pinned installs.

## Quickstart

```bash
# Or clone + editable install if you want to hack on it
git clone https://github.com/jiyangnan/agent-memory-hub.git
cd agent-memory-hub
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
  --applicability all_agents \
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

## Perspective Safety

Shared memory preserves source perspective. Inbox notes record `observer` and
`applicability`; downstream sync renders the current receiver so an agent does
not mistake another instance's memory for first-person experience.

Prefer facts such as `For Codex-family agents...` over ambiguous wording such as
`Codex's role...`.

## Docs

- [Quickstart](docs/quickstart.md)
- [Architecture](docs/architecture.md)
- [Adapters](docs/adapters.md)
- [Onboarding](docs/onboarding.md)
- [Perspective Safety](docs/perspective.md)
- [Sync](docs/sync.md)
- [Refresh](docs/refresh.md)
- [Cloud](docs/cloud.md)
- [Security](docs/security.md)
