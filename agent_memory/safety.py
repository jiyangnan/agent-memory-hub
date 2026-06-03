import re


SECRET_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_\-]{8,}"),
    re.compile(r"\bghp_[A-Za-z0-9_]+"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE),
    re.compile(r"\b(api[_-]?key|token|cookie|authorization)\b", re.IGNORECASE),
)


def contains_secret(text: str) -> bool:
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)

