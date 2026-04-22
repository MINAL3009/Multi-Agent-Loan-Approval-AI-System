from services.external_data import validate_email, validate_phone


def perform_kyc(state):
    application = state["application"]
    checks = []
    flags = []

    if application["has_pan"]:
        checks.append("PAN provided")
    else:
        flags.append("PAN not provided")

    if application["has_aadhaar"]:
        checks.append("Aadhaar provided")
    else:
        flags.append("Aadhaar not provided")

    email_validation = validate_email(
        application["email"],
        enabled=application["consent_to_verify_contacts"],
    )
    phone_validation = validate_phone(
        application["phone"],
        enabled=application["consent_to_verify_contacts"],
    )

    if email_validation.get("is_valid_format"):
        checks.append("Email format valid")
    else:
        flags.append("Email format failed validation")

    if phone_validation.get("is_valid_format"):
        checks.append("Phone format valid")
    else:
        flags.append("Phone validation failed")

    status = "verified"
    if not application["has_pan"] or not application["has_aadhaar"]:
        status = "manual_review"
    if flags and len(flags) >= 2:
        status = "failed"

    state["kyc"] = {
        "status": status,
        "checks": checks,
        "flags": flags,
        "email_validation": email_validation,
        "phone_validation": phone_validation,
        "note": "This is a project-grade digital KYC screen, not a regulated government KYC substitute.",
    }
    return state
