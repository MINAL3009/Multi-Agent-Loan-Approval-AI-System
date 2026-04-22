from fastapi import FastAPI, File, UploadFile

from agents.chat_agent import answer_application_question
from graph_builder import build_graph
from init_db import init_db
from schemas import ChatRequest, HealthResponse, LoanRequest
from services.llm_service import llm_service
from services.repository import save_application

app = FastAPI(title="Multi-Agent Loan Approval System", version="2.0.0")
loan_graph = build_graph()


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(status="ok")


@app.post("/apply-loan")
def apply_loan(data: LoanRequest):
    result = loan_graph.invoke({"application": data.model_dump()})
    save_application(result)

    return {
        "decision": result["risk"]["final_decision"],
        "risk_score": result["risk"]["score"],
        "risk_band": result["risk"]["band"],
        "interest_rate": result["underwriting"]["interest_rate"],
        "emi": result["underwriting"]["emi"],
        "kyc_status": result["kyc"]["status"],
        "loan_to_value_ratio": result["underwriting"]["ltv_ratio"],
        "foir": result["risk"]["foir"],
        "message": result["customer_message"],
        "explanation": result["explanation_text"],
        "llm_provider": result["llm_provider"],
        "verification": result["verification"],
        "risk_factors": result["risk"]["factors"],
        "macro_signals": result["risk"]["macro_signals"],
        "underwriting_reasons": result["underwriting"]["reasons"],
        "recommendations": result["recommendations"],
        "kyc_checks": result["kyc"]["checks"],
        "kyc_flags": result["kyc"]["flags"],
        "application_snapshot": result["application"],
    }


@app.post("/chat-about-application")
def chat_about_application(payload: ChatRequest):
    answer = answer_application_question(payload.context, payload.question)
    return {"answer": answer}


@app.post("/transcribe-audio")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcript = llm_service.transcribe_audio(audio_bytes, filename=file.filename or "question.wav")
    return {"transcript": transcript}
