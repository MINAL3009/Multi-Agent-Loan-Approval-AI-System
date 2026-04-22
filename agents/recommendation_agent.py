def build_recommendations(state):
    application = state["application"]
    kyc = state["kyc"]
    verification = state["verification"]
    underwriting = state["underwriting"]
    risk = state["risk"]

    recommendations = []

    if application["credit_score"] < 700:
        recommendations.append("Improve your credit score by clearing dues on time and reducing card utilization.")

    if risk["foir"] > 45:
        recommendations.append("Lower your overall EMI burden before reapplying so your fixed-obligation-to-income ratio improves.")

    if application["collateral_value"] <= 0 and application["loan_amount"] >= application["income"] * 12:
        recommendations.append("Consider adding collateral or applying for a smaller unsecured amount.")

    if verification["disposable_income"] < application["income"] * 0.3:
        recommendations.append("Increase your repayment cushion by reducing expenses or applying after a higher income cycle.")

    if application["existing_loans"] >= 2:
        recommendations.append("Closing one existing loan can strengthen your leverage profile for the next application.")

    if kyc["status"] != "verified":
        recommendations.append("Complete KYC documentation cleanly to avoid manual review or rejection.")

    if application["work_experience_years"] < 2:
        recommendations.append("A longer stable work history can improve confidence in repayment continuity.")

    if not recommendations:
        recommendations.append("Maintain your current repayment discipline and document readiness to preserve eligibility.")

    state["recommendations"] = recommendations
    state["next_steps"] = recommendations[:3]
    return state
