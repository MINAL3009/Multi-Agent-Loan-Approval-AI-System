def verify_application(state):
    application = state["application"]
    issues = []
    positives = []

    income = application["income"]
    monthly_expenses = application["monthly_expenses"]
    existing_emi = application["existing_emi"]
    loan_amount = application["loan_amount"]
    bank_balance = application["bank_balance"]

    disposable_income = max(income - monthly_expenses - existing_emi, 0)
    if disposable_income <= 0:
        issues.append("No disposable monthly income remains after expenses and obligations")
    elif disposable_income >= income * 0.35:
        positives.append("Healthy disposable income after obligations")
    else:
        issues.append("Disposable income is relatively thin")

    if bank_balance >= loan_amount * 0.1:
        positives.append("Bank balance supports repayment resilience")
    else:
        issues.append("Low balance compared with requested loan size")

    if application["work_experience_years"] >= 2:
        positives.append("Work experience suggests income stability")
    elif application["employment_type"] in {"student", "freelancer"}:
        issues.append("Employment profile is less stable and needs tighter underwriting")
    else:
        issues.append("Limited employment history")

    if application["collateral_type"].lower() != "none" and application["collateral_value"] > 0:
        positives.append("Collateral is available")
    elif loan_amount >= income * 18:
        issues.append("Unsecured request is large relative to monthly income")

    state["verification"] = {
        "issues": issues,
        "positives": positives,
        "disposable_income": round(disposable_income, 2),
        "document_consistency": "clear" if len(issues) <= 2 else "needs_review",
    }
    return state
