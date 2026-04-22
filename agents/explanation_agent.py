from services.llm_service import llm_service


def _fallback_explanation(state):
    application = state["application"]
    kyc = state["kyc"]
    verification = state["verification"]
    underwriting = state["underwriting"]
    risk = state["risk"]
    recommendations = state.get("recommendations", [])

    lines = [
        f"Application for {application['name']} was assessed through KYC, verification, underwriting, and risk stages.",
        f"KYC status: {kyc['status']}.",
        f"Final decision: {risk['final_decision']} with risk score {risk['score']} ({risk['band']}).",
        f"Interest rate considered: {underwriting['interest_rate']}% and estimated EMI: INR {underwriting['emi']}.",
    ]

    if underwriting["reasons"]:
        lines.append("Key underwriting reasons: " + "; ".join(underwriting["reasons"]) + ".")
    if verification["issues"]:
        lines.append("Verification concerns: " + "; ".join(verification["issues"]) + ".")
    if risk["factors"]:
        lines.append("Risk drivers: " + "; ".join(risk["factors"][:4]) + ".")
    if recommendations:
        lines.append("Recommendations: " + "; ".join(recommendations[:3]) + ".")

    return " ".join(lines) + "\n\nSincerely,\nUnderWriting agent Ms. Ishita"


def build_explanation(state):
    application = state["application"]
    kyc = state["kyc"]
    verification = state["verification"]
    underwriting = state["underwriting"]
    risk = state["risk"]
    recommendations = state.get("recommendations", [])

    system_prompt = (
        "You are a bank underwriting explanation agent. "
        "Write a concise, professional explanation for a loan decision. "
        "Do not invent facts and do not mention unsupported legal claims. "
        "End the response exactly with:\nSincerely,\nUnderWriting agent Ms. Ishita"
    )
    user_prompt = f"""
Applicant: {application['name']}
Income: {application['income']}
Credit score: {application['credit_score']}
Loan amount: {application['loan_amount']}
Tenure: {application['loan_tenure_years']} years
Employment type: {application['employment_type']}
Collateral: {application['collateral_type']} worth {application['collateral_value']}
KYC: {kyc}
Verification: {verification}
Underwriting: {underwriting}
Risk: {risk}
Recommendations: {recommendations}

Write a customer-safe explanation in 120-180 words.
"""

    explanation = llm_service.generate(system_prompt, user_prompt) or _fallback_explanation(state)
    if "Sincerely," not in explanation:
        explanation = explanation.rstrip() + "\n\nSincerely,\nUnderWriting agent Ms. Ishita"
    explanation = explanation.replace("Sincerely,\n[Your Name]\nUnderwriting Agent", "Sincerely,\nUnderWriting agent Ms. Ishita")
    explanation = explanation.replace("Sincerely,\r\n[Your Name]\r\nUnderwriting Agent", "Sincerely,\nUnderWriting agent Ms. Ishita")
    explanation = explanation.replace("[Your Name] Underwriting Agent", "UnderWriting agent Ms. Ishita")
    explanation = explanation.replace("[Your Name]", "Ms. Ishita")
    explanation = explanation.replace("Underwriting Agent", "UnderWriting agent Ms. Ishita")
    state["explanation_text"] = explanation
    state["llm_provider"] = llm_service.provider_name
    return state
