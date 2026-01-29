from dataclasses import dataclass, field
from collections import deque

@dataclass
class InterviewState:
    position: str
    grade: str
    experience: str

    turn_id: int = 0

    # последние 3 сообщения пользователя
    user_history: deque[str] = field(default_factory=lambda: deque(maxlen=3))

    # метрики
    topics_covered: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    scored_turns: int = 0
    sum_score: float = 0.0  # OK/WEAK/FAIL -> 1/0.6/0.2
    current_topic_group: str = "other"
    topic_depth: int = 0

    # последний вопрос интервьюера (для Analyzer: оценка релевантности ответа)
    last_question: str = ""
