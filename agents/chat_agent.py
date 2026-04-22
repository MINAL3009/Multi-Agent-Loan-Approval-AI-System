from services.llm_service import llm_service


def _fallback_chat_answer(context, question: str) -> str:
    decision = context.get("decision", "UNKNOWN")
    risk_score = context.get("risk_score", "N/A")
    recommendations = context.get("recommendations", [])
    answer = (
        f"The current application outcome is {decision} with risk score {risk_score}. "
        f"You asked: {question}. "
    )
    if recommendations:
        answer += "Helpful next steps include: " + "; ".join(recommendations[:3]) + "."
    else:
        answer += "Please review the risk factors, underwriting reasons, and KYC status shown on the dashboard."
    return answer


def answer_application_question(context, question: str) -> str:
    system_prompt = (
        "You are a loan decision assistant embedded in a loan approval dashboard. "
        "Answer only using the supplied application outcome context. "
        "Be practical, concise, and helpful. If the result is rejected or review, explain improvements clearly. "
        "Do not invent bank policies beyond the provided context."
    )
    user_prompt = f"""
Application context:
{context}

User question:
{question}

Answer in under 180 words.
"""
    return llm_service.generate(system_prompt, user_prompt) or _fallback_chat_answer(context, question)
