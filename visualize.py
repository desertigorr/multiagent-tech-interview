import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st

st.set_page_config(page_title="Interview Chat", layout="wide")
st.title("💬 Interview Chat (log viewer)")


def load_json(uploaded, path: str) -> Optional[Dict[str, Any]]:
    if uploaded is not None:
        return json.loads(uploaded.read().decode("utf-8"))
    p = Path(path)
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    return None


def pick(thoughts: List[Dict[str, Any]], who: str) -> List[Dict[str, Any]]:
    return [t for t in thoughts if t.get("from") == who]


with st.sidebar:
    uploaded = st.file_uploader("Upload interview_log.json", type=["json"])
    path = st.text_input("или путь к файлу", value="interview_log.json")

data = load_json(uploaded, path)
if data is None:
    st.info("Загрузите JSON или укажите корректный путь.")
    st.stop()

st.caption(f"Team: **{data.get('team_name', 'UNKNOWN')}**")

turns: List[Dict[str, Any]] = data.get("turns", [])
final_feedback: Dict[str, Any] | None = data.get("final_feedback")

tab_chat, tab_report = st.tabs(["💬 Interview Log", "📊 Final Report"])

with tab_chat:
    for t in turns:
        turn_id = t.get("turn_id")
        bot_msg = t.get("agent_visible_message", "")
        user_msg = t.get("user_message", "")
        thoughts = t.get("internal_thoughts", [])

        st.divider()
        st.subheader(f"Turn {turn_id}")

        # Interviewer
        with st.chat_message("assistant"):
            st.markdown("**Interviewer**")
            st.write(bot_msg)

        # User
        with st.chat_message("user"):
            st.markdown("**User**")
            st.write(user_msg)

        # Observer Analyzer
        analyzer = pick(thoughts, "Observer_Analyzer")
        if analyzer:
            with st.chat_message("assistant"):
                st.markdown("**Observer_Analyzer**")
                st.json(analyzer[0].get("content", {}))

        # Strategy
        strat = pick(thoughts, "Strategy_Module")
        if strat:
            with st.chat_message("assistant"):
                st.markdown("**Strategy_Module**")
                st.json(strat[0].get("content", {}))


with tab_report:
    if not final_feedback:
        st.info("Финальный отчёт отсутствует.")
        st.stop()

    st.subheader("🧠 Hiring Manager Decision")

    decision = final_feedback.get("decision", {})
    cols = st.columns(4)
    cols[0].metric("Final Grade", decision.get("final_grade", "—"))
    cols[1].metric("Recommendation", decision.get("hiring_recommendation", "—"))
    cols[2].metric("Confidence", decision.get("confidence_score", 0.0))
    cols[3].metric("Avg Score", decision.get("avg_score", "—"))

    st.divider()

    # Answers distribution
    answers = final_feedback.get("answers", {})
    if answers:
        st.subheader("📈 Answer Quality")
        st.bar_chart(answers)

    st.divider()

    # Hard skills
    st.subheader("🛠 Hard Skills")

    hs = final_feedback.get("hard_skills", {})
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**✅ Confirmed**")
        for s in hs.get("confirmed", []):
            st.markdown(f"- {s}")

    with col2:
        st.markdown("**⚠️ Gaps**")
        for g in hs.get("gaps", []):
            st.markdown(f"- {g}")

    st.divider()

    # Soft skills
    st.subheader("🤝 Soft Skills")
    soft = final_feedback.get("soft_skills", {})
    st.json(soft)

    st.divider()

    # Roadmap
    st.subheader("🧭 Learning Roadmap")
    for i, step in enumerate(final_feedback.get("roadmap", []), start=1):
        st.markdown(f"{i}. {step}")