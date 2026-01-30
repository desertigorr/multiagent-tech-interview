ALLOWED_TOPIC_GROUPS = (
    "coding", "db", "system_design", "tools", "testing", "interview"
)

_ALIASES = {
    "database": "db", "databases": "db", "sql": "db", "storage": "db",
    "ml": "tools", "machine learning": "tools", "machinelearning": "tools",
    "llm": "tools", "rag": "tools", "ai": "tools",
    "design": "system_design", "architecture": "system_design",
    "backend": "coding", "code": "coding", "algorithms": "coding",
    "testing": "testing", "tests": "testing", "qa": "testing",
}


def normalize_topic_group(s: str | None) -> str:
    if not s or not isinstance(s, str):
        return "other"
    t = s.strip().lower().replace(" ", "_").replace("-", "_")
    if t in ALLOWED_TOPIC_GROUPS:
        return t
    return _ALIASES.get(t, "other")
