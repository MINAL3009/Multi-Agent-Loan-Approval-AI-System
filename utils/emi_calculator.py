def calculate_emi(principal, annual_rate=10.0, years=5):
    if principal <= 0 or years <= 0:
        return 0.0

    monthly_rate = annual_rate / (12 * 100)
    months = years * 12

    if monthly_rate == 0:
        return round(principal / months, 2)

    emi = (principal * monthly_rate * (1 + monthly_rate) ** months) / (((1 + monthly_rate) ** months) - 1)
    return round(emi, 2)
