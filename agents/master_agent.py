from datetime import datetime, timezone


def prepare_application(state):
    application = dict(state["application"])
    income = application["income"]
    monthly_expenses = application["monthly_expenses"]
    existing_emi = application["existing_emi"]
    disposable_income = max(income - monthly_expenses - existing_emi, 0)

    application["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
    application["income_to_loan_ratio"] = round(income / application["loan_amount"], 4) if application["loan_amount"] else 0
    application["expense_ratio"] = round((monthly_expenses / income) * 100, 2) if income else 0
    application["disposable_income"] = round(disposable_income, 2)

    state["application"] = application
    state["audit_log"] = ["Application normalized by master agent"]
    return state
