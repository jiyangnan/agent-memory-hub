DEFAULT_TRIGGER_ALIASES = {
    "shared": (
        "保存到共享记忆",
        "写到共享记忆",
        "同步给其他 agent",
        "同步给其他agent",
        "share with other agents",
        "save to shared memory",
    ),
    "refresh": (
        "拉取云端记忆",
        "拉取一下云端的记忆",
        "拉取共享记忆",
        "刷新共享记忆",
        "更新共享记忆",
        "同步一下云端记忆",
        "refresh shared memory",
        "pull cloud memory",
    ),
    "local": (
        "记住这个",
        "保存到记忆",
        "remember this",
        "save to memory",
    ),
}


def aliases_for(config: dict | None) -> dict[str, tuple[str, ...]]:
    aliases = {key: tuple(value) for key, value in DEFAULT_TRIGGER_ALIASES.items()}
    configured = (config or {}).get("trigger_aliases", {})
    for trigger_type in ("shared", "refresh", "local"):
        if configured.get(trigger_type):
            aliases[trigger_type] = tuple(configured[trigger_type])
    return aliases


def classify_trigger(text: str, *, config: dict | None = None) -> str:
    normalized = " ".join(text.strip().split()).lower()
    aliases = aliases_for(config)
    for trigger_type in ("shared", "refresh", "local"):
        if any(alias.lower() in normalized for alias in aliases[trigger_type]):
            return trigger_type
    return "none"

