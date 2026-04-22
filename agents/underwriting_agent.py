from utils.emi_calculator import calculate_emi


def underwrite_application(state):
    application = state["application"]
    verification = state["verification"]
    kyc = state["kyc"]

    collateral_value = application["collateral_value"]
    loan_amount = application["loan_amount"]
    ltv = (loan_amount / collateral_value) * 100 if collateral_value else None

    base_rate = 10.5
    rate_adjustments = 0
    decision = "APPROVED"
    reasons = []

    if application["credit_score"] < 600:
        decision = "REJECTED"
        reasons.append("Credit score is below the minimum underwriting threshold")
        rate_adjustments += 3
    elif application["credit_score"] < 700:
        rate_adjustments += 1.5
        reasons.append("Moderate credit score increased pricing")
    else:
        reasons.append("Credit score supports the requested facility")

    if verification["disposable_income"] < application["income"] * 0.15:
        decision = "REJECTED"
        reasons.append("Insufficient repayment cushion after obligations")
    elif verification["disposable_income"] < application["income"] * 0.3:
        rate_adjustments += 1
        reasons.append("Thin repayment cushion increased pricing")

    if ltv is not None:
        if ltv <= 70:
            rate_adjustments -= 0.5
            reasons.append("Strong collateral coverage improved the offer")
        elif ltv > 90:
            rate_adjustments += 1.5
            reasons.append("High loan-to-value ratio increased risk")

    if kyc["status"] == "failed":
        decision = "REJECTED"
        reasons.append("KYC screening failed")
    elif kyc["status"] == "manual_review":
        rate_adjustments += 0.5
        reasons.append("KYC requires manual follow-up")

    interest_rate = round(max(base_rate + rate_adjustments, 7.5), 2)
    emi = calculate_emi(
        principal=loan_amount,
        annual_rate=interest_rate,
        years=application["loan_tenure_years"],
    )

    state["underwriting"] = {
        "decision": decision,
        "interest_rate": interest_rate,
        "emi": emi,
        "ltv_ratio": round(ltv, 2) if ltv is not None else None,
        "reasons": reasons,
    }
    return state
