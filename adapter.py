import json
from typing import Dict, Any, List


def format_observer(obs: Dict[str, Any]) -> str:
    if not obs:
        return "Нет данных от Observer."

    status_map = {
        "OK": "Ответ хороший.",
        "WEAK": "Ответ слабый.",
        "WRONG": "Ответ неверный.",
        "FALSE_INFO": "Обнаружена неверная информация.",
        "OFFTOPIC": "Ответ не по теме.",
        "QUESTION_TO_COMPANY": "Вопрос о компании.",
        "END_INTERVIEW": "Кандидат завершил интервью."
    }

    status = obs.get("status", "UNKNOWN")
    notes = obs.get("notes", "")

    lines = [status_map.get(status, f"Статус: {status}")]
    if notes:
        lines.append(f"Комментарий: {notes}")

    return "\n".join(lines)


def format_strategy(decision: Dict[str, Any]) -> str:
    if not decision:
        return "Нет решения стратегии."

    lines = []
    if decision.get("action"):
        lines.append(f"Действие: {decision['action']}")
    if decision.get("instruction"):
        lines.append(f"Инструкция: {decision['instruction']}")

    return "\n".join(lines)


def format_orchestrator(meta: Dict[str, Any]) -> str:
    if not meta:
        return "Нет метрик."

    lines = []
    if meta.get("scored_turns") is not None:
        lines.append(f"Оценённых ответов: {meta['scored_turns']}")
    if meta.get("avg_score") is not None:
        lines.append(f"Средний балл: {round(meta['avg_score'], 2)}")

    return "\n".join(lines)


def format_internal_thoughts(thoughts: List[Dict[str, Any]]) -> str:
    blocks = []

    for t in thoughts:
        agent = t.get("from")
        content = t.get("content", {})

        if agent == "Observer_Analyzer":
            blocks.append(f"[Observer]:\n{format_observer(content)}")

        elif agent == "Strategy_Module":
            blocks.append(f"[Strategy]:\n{format_strategy(content)}")

        elif agent == "Orchestrator":
            blocks.append(f"[Orchestrator]:\n{format_orchestrator(content)}")

        else:
            blocks.append(f"[{agent}]: {str(content)}")

    return "\n\n".join(blocks)


def format_final_feedback(feedback: Dict[str, Any]) -> str:
    if not feedback:
        return "Финальный фидбэк отсутствует."

    d = feedback.get("decision", {})
    hard = feedback.get("hard_skills", {})
    soft = feedback.get("soft_skills", {})
    roadmap = feedback.get("roadmap", [])

    lines = []

    lines.append("ИТОГОВОЕ РЕШЕНИЕ")
    lines.append(f"Уровень: {d.get('final_grade')}")
    lines.append(f"Рекомендация: {d.get('hiring_recommendation')}")
    lines.append(f"Уверенность: {d.get('confidence_score')}")

    lines.append("\nСИЛЬНЫЕ СТОРОНЫ:")
    for s in hard.get("confirmed", []):
        lines.append(f"– {s}")

    lines.append("\nЗОНЫ РОСТА:")
    for g in hard.get("gaps", []):
        if isinstance(g, dict):
            lines.append(f"– {g.get('topic')}")
        else:
            lines.append(f"– {g}")

    lines.append("\nСОФТ-СКИЛЛЫ:")
    for k, v in soft.items():
        lines.append(f"{k.capitalize()}: {v}")

    lines.append("\nРЕКОМЕНДАЦИИ:")
    for i, step in enumerate(roadmap, 1):
        if isinstance(step, dict):
            lines.append(f"{i}. {step.get('step')}")
        else:
            lines.append(f"{i}. {step}")

    return "\n".join(lines)


def adapt_log_to_readable_submission(input_path: str, output_path: str):
    with open(input_path, "r", encoding="utf-8") as f:
        raw_log = json.load(f)

    adapted = {
        "participant_name": raw_log.get("participant_name", ""),
        "turns": [],
        "final_feedback": ""
    }

    for turn in raw_log.get("turns", []):
        adapted_turn = {
            "turn_id": turn.get("turn_id"),
            "agent_visible_message": turn.get("agent_visible_message"),
            "user_message": turn.get("user_message"),
            "internal_thoughts": ""
        }

        thoughts = turn.get("internal_thoughts", [])
        if isinstance(thoughts, list):
            adapted_turn["internal_thoughts"] = format_internal_thoughts(thoughts)
        else:
            adapted_turn["internal_thoughts"] = str(thoughts)

        adapted["turns"].append(adapted_turn)

    adapted["final_feedback"] = format_final_feedback(
        raw_log.get("final_feedback", {})
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(adapted, f, ensure_ascii=False, indent=2)

    print(f"Saved readable submission log to: {output_path}")

if __name__ == "__main__":
    adapt_log_to_readable_submission(
        input_path="interview_log.json",
        output_path="interview_log_submission.json"
    )
