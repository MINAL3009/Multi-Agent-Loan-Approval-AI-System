def build_customer_message(state):
    application = state["application"]
    underwriting = state["underwriting"]
    risk = state["risk"]
    kyc = state["kyc"]
    explanation = state["explanation_text"]
    recommendations = state.get("recommendations", [])

    decision = risk["final_decision"]
    if decision == "APPROVED":
        intro = f"Dear {application['name']}, your loan request has been approved."
    elif decision == "REVIEW":
        intro = f"Dear {application['name']}, your application needs manual review before a final approval."
    else:
        intro = f"Dear {application['name']}, we are unable to approve the loan request right now."

    bullet_points = [
        f"Requested amount: INR {application['loan_amount']:,.2f}",
        f"Estimated EMI: INR {underwriting['emi']:,.2f}",
        f"Indicative interest rate: {underwriting['interest_rate']}%",
        f"Risk band: {risk['band']} ({risk['score']})",
        f"KYC status: {kyc['status']}",
    ]

    recommendation_block = ""
    if recommendations and decision != "APPROVED":
        recommendation_block = "\n\nWhat you can improve before the next application:\n" + "\n".join(
            f"- {item}" for item in recommendations
        )

    state["customer_message"] = (
        intro + "\n\n" + "\n".join(f"- {item}" for item in bullet_points) + recommendation_block + "\n\n" + explanation
    )
    return state
