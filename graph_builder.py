from langgraph.graph import END, START, StateGraph

from agents.explanation_agent import build_explanation
from agents.kyc_agent import perform_kyc
from agents.master_agent import prepare_application
from agents.recommendation_agent import build_recommendations
from agents.risk_agent import assess_risk
from agents.sales_agent import build_customer_message
from agents.underwriting_agent import underwrite_application
from agents.verification_agent import verify_application


def build_graph():
    workflow = StateGraph(dict)

    workflow.add_node("master", prepare_application)
    workflow.add_node("kyc", perform_kyc)
    workflow.add_node("verification", verify_application)
    workflow.add_node("underwriting", underwrite_application)
    workflow.add_node("risk", assess_risk)
    workflow.add_node("recommendation", build_recommendations)
    workflow.add_node("explanation", build_explanation)
    workflow.add_node("sales", build_customer_message)

    workflow.add_edge(START, "master")
    workflow.add_edge("master", "kyc")
    workflow.add_edge("kyc", "verification")
    workflow.add_edge("verification", "underwriting")
    workflow.add_edge("underwriting", "risk")
    workflow.add_edge("risk", "recommendation")
    workflow.add_edge("recommendation", "explanation")
    workflow.add_edge("explanation", "sales")
    workflow.add_edge("sales", END)

    return workflow.compile()
