from services.external_data import get_macro_signals


def assess_risk(state):
    application = state["application"]
    underwriting = state["underwriting"]
    verification = state["verification"]
    kyc = state["kyc"]
    macro = get_macro_signals(enabled=application["consent_to_fetch_financial_signals"])

    factors = []
    score = 0

    credit_score = application["credit_score"]
    if credit_score < 600:
        score += 28
        factors.append("Weak credit score materially raised risk")
    elif credit_score < 700:
        score += 15
        factors.append("Average credit score moderately raised risk")
    else:
        score += 5
        factors.append("Strong credit score supported the case")

    income = application["income"]
    total_emi = application["existing_emi"] + underwriting["emi"]
    foir = (total_emi / income) * 100 if income else 100
    if foir > 55:
        score += 24
        factors.append("FOIR is above comfort range")
    elif foir > 40:
        score += 14
        factors.append("FOIR is acceptable but somewhat stretched")
    else:
        score += 6
        factors.append("FOIR is healthy")

    collateral_value = application["collateral_value"]
    if collateral_value > 0:
        ltv = (application["loan_amount"] / collateral_value) * 100
        if ltv > 90:
            score += 12
            factors.append("Collateral coverage is thin")
        elif ltv <= 70:
            score -= 4
            factors.append("Collateral meaningfully reduced risk")
    else:
        score += 8
        factors.append("Loan is unsecured")

    if verification["document_consistency"] != "clear":
        score += 8
        factors.append("Verification raised consistency concerns")

    if kyc["status"] == "failed":
        score += 20
        factors.append("KYC failure sharply increased risk")
    elif kyc["status"] == "manual_review":
        score += 8
        factors.append("KYC needs manual review")

    if application["work_experience_years"] < 1:
        score += 6
        factors.append("Limited employment history increased risk")

    if application["existing_loans"] >= 3:
        score += 8
        factors.append("Multiple active loans increased leverage risk")

    if application["bank_balance"] >= application["loan_amount"] * 0.2:
        score -= 3
        factors.append("Liquidity buffer improved resilience")

    score += macro.get("risk_adjustment", 0)

    score = max(0, min(round(score, 2), 100))
    band = "LOW" if score <= 30 else "MEDIUM" if score <= 60 else "HIGH"

    final_decision = underwriting["decision"]
    if band == "HIGH" and final_decision == "APPROVED":
        final_decision = "REVIEW"

    state["risk"] = {
        "score": score,
        "band": band,
        "foir": round(foir, 2),
        "macro_signals": macro,
        "factors": factors,
        "final_decision": final_decision,
    }
    return state
