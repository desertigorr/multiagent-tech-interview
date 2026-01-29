from interview_state import InterviewState
from topics import ALLOWED_TOPIC_GROUPS, normalize_topic_group

TOPIC_ROTATION = list(ALLOWED_TOPIC_GROUPS)
MAX_DEPTH = 2

_DONT_KNOW_PHRASES = (
    "не знаю", "затрудняюсь", "не помню", "не уверен", "трудно сказать",
    "не могу ответить", "не помню точно", "затрудняюсь ответить",
)

def strategy_decide(state: InterviewState, obs: dict, user_message: str = "") -> dict:
    if "стоп игра" in (user_message or "").lower():
        return {"action": "FINISH", "instruction": "Finish interview and generate final feedback.", "next_difficulty": None}

    status = obs.get("status", "WEAK")
    score = float(obs.get("score", 0.6))
    obs_group = normalize_topic_group(obs.get("topic_group") or "other")
    user_lower = (user_message or "").lower()
    dont_know = any(p in user_lower for p in _DONT_KNOW_PHRASES)

    # 0) Вычисляем target_group ВСЕГДА (кроме FINISH)
    # Вопросы к компании / оффтоп не должны менять тему и глубину
    if status in {"QUESTION_TO_COMPANY", "OFFTOPIC"}:
        target_group = state.current_topic_group or obs_group or "other"
    else:
        # обновляем depth
        if obs_group == getattr(state, "current_topic_group", None):
            state.topic_depth += 1
        else:
            state.current_topic_group = obs_group
            state.topic_depth = 1

        # ротация
        if state.topic_depth > MAX_DEPTH and score >= 0.6:
            try:
                idx = TOPIC_ROTATION.index(state.current_topic_group)
            except ValueError:
                idx = len(TOPIC_ROTATION) - 1
            target_group = TOPIC_ROTATION[(idx + 1) % len(TOPIC_ROTATION)]
            state.current_topic_group = target_group
            state.topic_depth = 1
        else:
            target_group = state.current_topic_group

    # 1) Теперь выбираем action (и везде прикладываем target_group)

    if status == "END_INTERVIEW":
        return {"action": "FINISH", "instruction": "Finish interview and generate final feedback.", "next_difficulty": None}

    if status == "QUESTION_TO_COMPANY":
        return {
            "action": "ANSWER_QUESTION_THEN_ASK",
            "instruction": "You have to answer the candidate's question about the company briefly, then ask a technical question according to the topic and difficulty.",
            "next_difficulty": None,
            "target_topic_group": target_group
        }

    if status == "WRONG":
        return {
            "action": "CORRECT_AND_REDIRECT",
            "instruction": "Do NOT agree with the USER. Correct USER according to Observer's message. Then ask a simple technical question to continue the interview.",
            "next_difficulty": 1,
            "target_topic_group": target_group
        }

    if status == "OFFTOPIC":
        return {
            "action": "REDIRECT",
            "instruction": "Politely redirect to the interview and ask a basic technical question.",
            "next_difficulty": 1,
            "target_topic_group": target_group
        }

    if dont_know:
        return {
            "action": "ASK_NEXT_EASIER",
            "instruction": "User said they don't know or struggle. Ask an easier question or give a brief hint, then ask again.",
            "next_difficulty": 1,
            "target_topic_group": target_group
        }

    if score >= 1.0:
        return {
            "action": "ASK_NEXT_HARDER",
            "instruction": "User is strong. Ask a harder question on same/near topic.",
            "next_difficulty": 2,
            "target_topic_group": target_group
        }

    if score <= 0.5:
        return {
            "action": "ASK_NEXT_EASIER",
            "instruction": "User struggled. Ask an easier question or provide a hint.",
            "next_difficulty": 1,
            "target_topic_group": target_group
        }

    return {
        "action": "ASK_NEXT",
        "instruction": "Ask the next relevant technical question.",
        "next_difficulty": None,
        "target_topic_group": target_group
    }