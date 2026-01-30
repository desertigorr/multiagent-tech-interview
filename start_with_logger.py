from logger import InterviewLogger
from interview_state import InterviewState
from observer import observer_analyze
from strategy import strategy_decide
from interviewer import interviewer_respond
from build_summary import build_interview_summary
from hiring_manager import generate_final_feedback
from adapter import adapt_log_to_readable_submission


def main():
    state = InterviewState(
        position="JavaSript Developer",
        grade="Junior",
        experience="Пет-проекты на JS, базовый синтаксис"
    )
    participant_name = "Зиманов Игорь Андреевич"
    candidate_name = "Кирилл"
    logger = InterviewLogger(participant_name=participant_name)

    greeting = f"Привет, {candidate_name}! Мы рады пригласить тебя на собеседование в нашу компанию на позицию {state.grade} {state.position}. Кратко расскажи о себе и своём опыте программирования."
    print("Interviewer >", greeting)
    state.last_question = greeting
    turn_id = 0

    while True:
        user_message = input("\nYOU > ").strip()
        state.user_history.append(state.last_question)

        obs, trace = observer_analyze(state, user_message)
        decision = strategy_decide(state, obs, user_message)

        # FINISH early
        if decision.get("action") == "FINISH":
            bot_message = "Окей, завершаю интервью. Сейчас сформирую финальный фидбэк."
            print("\nBOT>", bot_message)

            internal_thoughts = []
            if trace:
                internal_thoughts.append({"from":"Observer_Analyzer","to":"Strategy_Module","content": trace[0]["output"]})
            internal_thoughts.append({"from":"Strategy_Module","to":"Interviewer_Agent","content": decision})

            logger.log_turn(
                turn_id=turn_id,
                agent_visible_message=bot_message,
                user_message=user_message,
                internal_thoughts=internal_thoughts,
                question_answered=state.last_question,
            )

            summary = build_interview_summary(logger.data)

            final_feedback = generate_final_feedback(
                position=state.position,
                target_grade=state.grade,
                declared_experience=state.experience,
                interview_summary=summary,
            )

            logger.set_final_feedback(final_feedback)
            break

        # update metrics (ignore company/offtopic)
        if obs.get("status") not in {"QUESTION_TO_COMPANY", "OFFTOPIC"}:
            state.scored_turns += 1
            state.sum_score += float(obs.get("score", 0.6))

        bot_message = interviewer_respond(state, user_message, obs, decision)
        print("\nBOT>", bot_message)

        # internal thoughts
        internal_thoughts = []
        if trace:
            internal_thoughts.append({"from":"Observer_Analyzer","to":"Strategy_Module","content": trace[0]["output"]})
            # if len(trace) > 1:
            #     internal_thoughts.append({"from":"Observer_Verifier","to":"Strategy_Module","content": trace[1]["output"]})
            # else:
            #     internal_thoughts.append({"from":"Observer","to":"Strategy_Module","content":""})

        internal_thoughts.append({"from":"Strategy_Module","to":"Interviewer_Agent","content": decision})
        internal_thoughts.append({"from":"Orchestrator","to":"Logger","content": {
            "scored_turns": state.scored_turns,
            "sum_score": state.sum_score,
            "avg_score": (state.sum_score / state.scored_turns) if state.scored_turns else None,
            "topic_depth": getattr(state, "topic_depth", None),
            "current_topic_group": getattr(state, "current_topic_group", None),
        }})

        logger.log_turn(
            turn_id=turn_id,
            question_answered=state.last_question,
            user_message=user_message,
            agent_visible_message=bot_message,
            internal_thoughts=internal_thoughts
        )

        state.last_question = bot_message
        turn_id += 1
    logger.save("interview_log.json")
    print("\nSaved interview_log.json")

if __name__ == "__main__":
    main()