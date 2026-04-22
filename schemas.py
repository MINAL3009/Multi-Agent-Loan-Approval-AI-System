from typing import Literal, Optional

from pydantic import BaseModel, Field


class LoanRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: str
    phone: str = Field(..., min_length=8, max_length=16)
    age: int = Field(..., ge=18, le=70)
    income: float = Field(..., gt=0, description="Monthly income in INR")
    credit_score: int = Field(..., ge=300, le=900)
    loan_amount: float = Field(..., gt=0)
    loan_tenure_years: int = Field(5, ge=1, le=30)
    existing_loans: int = Field(0, ge=0, le=20)
    existing_emi: float = Field(0, ge=0)
    monthly_expenses: float = Field(0, ge=0)
    bank_balance: float = Field(0, ge=0)
    employment_type: Literal["salaried", "self-employed", "business", "freelancer", "student"] = "salaried"
    employer_name: Optional[str] = None
    work_experience_years: float = Field(0, ge=0, le=50)
    collateral_type: str = "none"
    collateral_value: float = Field(0, ge=0)
    loan_purpose: str = "general"
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    state: str = Field(..., min_length=2)
    country: str = "India"
    has_pan: bool = True
    has_aadhaar: bool = True
    consent_to_verify_contacts: bool = True
    consent_to_fetch_financial_signals: bool = True


class HealthResponse(BaseModel):
    status: str


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1)
    context: dict
