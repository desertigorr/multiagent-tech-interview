import json
from typing import Any


class InterviewLogger:
    def __init__(self, participant_name: str):
        self.data = {
            "participant_name": participant_name,
            "turns": [],
            "final_feedback": None
        }

    def log_turn(
        self,
        turn_id: int,
        agent_visible_message: str,
        user_message: str,
        internal_thoughts: Any,
        question_answered: str,
    ):
        turn = {
            "turn_id": turn_id,
            "agent_visible_message": agent_visible_message,
            "user_message": user_message,
            "internal_thoughts": internal_thoughts
        }
        if question_answered is not None:
            turn["agent_visible_message"] = question_answered
        self.data["turns"].append(turn)

    def set_final_feedback(self, final_feedback: Any):
        self.data["final_feedback"] = final_feedback

    def save(self, path: str = "interview_log.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)