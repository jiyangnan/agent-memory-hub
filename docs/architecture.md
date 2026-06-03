# Architecture

`agent memory hub` separates shared memory into three independent actions:

```text
T1 upstream: agent writes inbox
T2 curator: merge inbox into canonical memory
T3 downstream: refresh canonical memory into agent-native memory
```

The safety rule:

```text
inbox is multi-writer
canonical memory is single-writer
agent-native memory is adapter-written by allowlist
```

The lifecycle:

```text
agent learns
  -> inbox note
  -> curator validates and merges
  -> canonical memory updates
  -> cloud handoff
  -> downstream refresh
  -> agent cold-start perception
```

