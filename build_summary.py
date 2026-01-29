# interview_summary.py
from collections import Counter, defaultdict
from typing import Dict, Any, List


IGNORED_STATUSES = {"END_INTERVIEW", "QUESTION_TO_COMPANY"}


def build_interview_summary(interview_log: Dict[str, Any]) -> Dict[str, Any]:
    turns = interview_log.get("turns", [])

    status_counter = Counter()
    topic_groups = defaultdict(int)
    notes = []
    false_info_flags = 0

    scored_turns = 0
    score_sum = 0.0

    for turn in turns:
        thoughts = turn.get("internal_thoughts", [])
        for t in thoughts:
            if t.get("from") != "Observer_Analyzer":
                continue

            obs = t.get("content", {})
            status = obs.get("status")
            score = obs.get("score", 0)
            topic_group = obs.get("topic_group", "other")
            note = obs.get("notes", "")

            if status in IGNORED_STATUSES:
                continue

            status_counter[status] += 1
            topic_groups[topic_group] += 1

            scored_turns += 1
            try:
                score_sum += float(score)
            except Exception:
                pass

            if status in {"FALSE_INFO"}:
                false_info_flags += 1

            if note:
                notes.append(note)

    avg_score = (score_sum / scored_turns) if scored_turns else 0.0

    return {
        "metrics": {
            "scored_turns": scored_turns,
            "average_score": round(avg_score, 2),
            "status_distribution": dict(status_counter),
            "false_info_flags": false_info_flags,
        },
        "topics_covered": dict(topic_groups),
        "observer_notes": notes[:10],  # ограничим, чтобы не шуметь
    }