import re


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bghp_[A-Za-z0-9_]+"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"\b(api[_-]?key|token|cookie|authorization)\b", re.IGNORECASE),
)


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def has_ambiguous_agent_family_wording(text: str, *, agent_names: tuple[str, ...] = ()) -> bool:
    names = tuple(dict.fromkeys((*agent_names, "codex", "claude", "openclaw", "hermes")))
    if not names:
        return False
    escaped = "|".join(re.escape(name) for name in names)
    pattern = re.compile(rf"\b({escaped})(?:'s|\s+的)\b", re.IGNORECASE)
    if not pattern.search(text):
        return False

    disambiguators = (
        "family",
        "families",
        "agent family",
        "agents",
        "instances",
        "adapter family",
        "source_only",
        "当前接收者",
        "接收者",
        "实例",
        "家族",
        "同类",
    )
    lowered = text.lower()
    return not any(term.lower() in lowered for term in disambiguators)
