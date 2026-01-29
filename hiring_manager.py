import json
from typing import Dict, Any

from call_llm import call_llm


HIRING_MANAGER_SYSTEM = """
You are a Hiring Manager reviewing the results of a technical interview.

You did NOT participate in the interview.
You ONLY analyze structured interview summaries provided by the system.

Your task:
- Assess the candidate's demonstrated level.
- Decide whether to recommend hiring.
- Identify confirmed skills and knowledge gaps.
- Provide a constructive learning roadmap.
- Create an elaborate analysis report.

STRICT RULES:
- Base conclusions ONLY on the provided data.
- Do NOT assume skills that were not demonstrated.
- Junior candidates are allowed to have gaps.
- Confident false technical statements are critical red flags.

Return ONLY valid JSON.
Do NOT include explanations, markdown, or chain-of-thought.
"""


def _safe_json_parse(text: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return json.loads(text)
    except Exception:
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except Exception:
            return fallback


def generate_final_feedback(
    position: str,
    target_grade: str,
    declared_experience: str,
    interview_summary: Dict[str, Any],
) -> Dict[str, Any]:

    prompt = f"""
Position: {position}
Target grade: {target_grade}
Declared experience: {declared_experience}

Interview summary:
{json.dumps(interview_summary, ensure_ascii=False, indent=2)}

Generate final interview feedback according to this structure:
"OK" | "WEAK" |"WRONG" |"OFFTOPIC" |"QUESTION_TO_COMPANY"
{{
  "decision": {{
    "final_grade": "Junior | Middle | Senior",
    "hiring_recommendation": "Hire | No Hire | Strong Hire",
    "confidence_score": 0.0,
    "sum_score": sum_score of the candidate,
    "avg_score": avg_score of the candidate,
  }},
  "answers": {{
    "OK": int,
    "WEAK": int,
    "WRONG": int,
    "OFFTOPIC": int,
    "QUESTION_TO_COMPANY": int,
  }},
  "hard_skills": {{
    "confirmed": [],
    "gaps": []
  }},
  "soft_skills": {{
    "clarity": EXCELLENT | GOOD | OK | POOR,
    "honesty": EXCELLENT | GOOD | OK | POOR,
    "engagement": HIGH | MEDIUM | LOW
  }},
  "roadmap": []
}}
"""

    fallback = {
        "decision": {
            "final_grade": target_grade,
            "hiring_recommendation": "No Hire",
            "confidence_score": 0.5,
        },
        "hard_skills": {
            "confirmed": [],
            "gaps": [],
        },
        "soft_skills": {
            "clarity": "Не удалось оценить",
            "honesty": "Не удалось оценить",
            "engagement": "Не удалось оценить",
        },
        "roadmap": [],
    }

    raw = call_llm(prompt, system=HIRING_MANAGER_SYSTEM)
    return _safe_json_parse(raw, fallback)