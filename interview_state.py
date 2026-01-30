from dataclasses import dataclass, field
from collections import deque

@dataclass
class InterviewState:
    position: str
    grade: str
    experience: str

    turn_id: int = 0

    # последние n сообщений пользователя (например 5)
    user_history: deque[str] = field(default_factory=lambda: deque(maxlen=6))

    # метрики и логи
    topics_covered: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    scored_turns: int = 0
    sum_score: float = 0.0 
    current_topic_group: str = "other"
    topic_depth: int = 0
    last_question: str = ""
