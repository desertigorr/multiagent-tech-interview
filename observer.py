import json
from typing import Any, Dict, List
from call_llm import call_llm
from interview_state import InterviewState
from topics import normalize_topic_group


def _safe_json_parse(text: str, fallback: dict) -> dict:
    try:
        return json.loads(text)
    except Exception:
        # попытка вырезать JSON-блок
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            cleaned = text[start:end]
            return json.loads(cleaned)
        except Exception:
            print("ERROR OCCURED IN JSON:", text)
            return fallback


def _llm_json(system_prompt: str, prompt: str, fallback: Dict[str, Any]) -> Dict[str, Any]:
    raw = call_llm(prompt, system=system_prompt)
    return _safe_json_parse(raw, fallback)


ANALYZER_SYSTEM = """
You are Observer_Analyzer Agent in a technical interview. You recieve Interviewer's QUESTION and candidate's ANSWER.

RELEVANCE (critical): You are given the last question from the interviewer. The user's message must answer that question. 
If the user does not answer (e.g. vague "I do ML" when asked "Which ML methods do you use?"), or evades, or only acknowledges without substance => status MUST be WEAK or FAIL, score 0.6 or 0.2. OK/1.0 only when the reply is relevant, specific, and actually addresses the question.

Return ONLY valid JSON with keys:
- status: "OK" | "WEAK" |"WRONG" |"OFFTOPIC" |"QUESTION_TO_COMPANY" |"END_INTERVIEW".
- topic: short string (examples: "python", "java", "go", etc.)
- topic_group: MUST BE one of ["language","coding","db","system_design","tools","testing","other"]. Synonyms: database -> db, ML -> tools.
- score: according to STATUS -> (OK=1.0 or 0.9 or 0.8, WEAK=0.6, WRONG/OFFTOPIC=0.2). Never 1.0 if the reply does not fully answer the question.
- notes: notes about candidate's answer: what was correct, what was incorrect and how he could fix the answer, and other important imformation for Hiring Manager, who makes a hiring decision.

Rules:
- If user asks about company/process/tasks/job terms or anything related to his potential job, status MUST ="QUESTION_TO_COMPANY"
  Examples: ["Какие задачи будут у меня на испытательном сроке?", "Какие условия работы в вашей компании?", "Какая будет зарплата?"] => status = "QUESTION_TO_COMPANY"!
- If user is off-topic/refuses to answer the question and NOT asks the Interviewer about company => status="OFFTOPIC"
- If user answers the question completely incorrectly or with major mistakes => status ="WRONG" and add a note with explanation of mistake.
- If user states false facts confidently => status="WRONG" and add a note with explanation of false fact.
IMPORTANT: Fact should be considered FALSE if you can check it. Example: "Python 4.0 is already out" is FALSE. "I have been working for 5 years" is NOT FALSE - you cannot verify it.
- If user says they don't know / затрудняюсь / не помню / не уверен => status WEAK, score 0.6 (or WRONG if completely evasive).
- If user asks you to end the interview and get to feedback and discussuion => status MUST BE "END_INTERVIEW".
- Otherwise you should set status to "OK" if the answer is full and correct or has minor mistakes OR "WEAK" if the answer isn't full or has mistakes
"""

def observer_analyze(state: InterviewState, user_message: str) -> tuple[Dict[str, Any], List[Dict[str, Any]]]:
    trace = []
    recent = "\n".join(f"- {m}" for m in list(state.user_history)[:-1])
    last_q = (state.last_question or "").strip()

    analyzer_prompt = f"""
        Position: {state.position}
        Target grade: {state.grade}
        Experience: {state.experience}

        Last question from interviewer (assess whether user's reply ANSWERS it):
        "{last_q}"

        Recent user messages:
        {recent}

        User message:
        {user_message}
    """

    analyzer_fallback = {
        "status": "ERROR",
        "topic": "other",
        "topic_group": "other",
        "score": 0,
        "notes": ""
    }

    analysis = _llm_json(ANALYZER_SYSTEM, analyzer_prompt, analyzer_fallback)

    # нормализация выходных значений
    allowed_status = {"OK","WEAK","WRONG","OFFTOPIC","QUESTION_TO_COMPANY","END_INTERVIEW"}

    if analysis.get("status") not in allowed_status:
        analysis["status"] = "ERROR"

    try:
        s = float(analysis.get("score", 0))
    except Exception:
        s = 0

    analysis["score"] = s
    analysis["topic_group"] = normalize_topic_group(analysis.get("topic_group") or "other")

    trace.append({
        "step": "analyzer",
        "output": analysis
    })

    return analysis, trace