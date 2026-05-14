from __future__ import annotations
import pandas as pd
import os
from typing import TypedDict, Dict, Any

from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from tools.pdf_tools import PdfRag
from tools.csv_tools import analyze_csv
from tools.weather_tools import get_weather_forecast, derive_dispatch_weather_risk
from tools.email_tools import send_email_smtp
from agents import run_context_agent, run_ops_agent, run_planner_agent, run_report_agent

load_dotenv()

class AppState(TypedDict, total=False):
    pdf_path: str
    csv_path: str
    what_if_scenario: str # NEW: Field to hold the hypothetical disruption

    business_context: str
    csv_summary: Dict[str, Any]
    csv_kpis: Dict[str, Any]
    anomalies_md: str
    ops_insights: str

    weather_forecast: Dict[str, Any]
    weather_risk: Dict[str, Any]

    dispatch_plan: str
    report_html: str

    resource_csv_path: str
    resource_constraints: str # NEW: To hold the parsed constraints


def node_pdf_context(state: AppState) -> AppState:
    rag = PdfRag(persist_dir="chroma_db")
    vectordb = rag.build(state["pdf_path"])
    retriever = rag.retriever(vectordb, k=6)

    query = "Extract KPI definitions, thresholds, SLAs, constraints, dispatch rules, exceptions."
    docs = retriever.invoke(query)
    snippets = "\n\n---\n\n".join(d.page_content for d in docs)

    business_context = run_context_agent(snippets)
    return {"business_context": business_context}


def node_csv_analysis(state: AppState) -> AppState:
    res = analyze_csv(state["csv_path"])

    anomalies_md = "(none detected or insufficient numeric data)"
    if not res.anomalies.empty:
        anomalies_md = res.anomalies.head(12).to_markdown(index=False)

    ops_insights = run_ops_agent(summary=res.summary, kpis=res.kpis, anomalies_md=anomalies_md)

    return {
        "csv_summary": res.summary,
        "csv_kpis": res.kpis,
        "anomalies_md": anomalies_md,
        "ops_insights": ops_insights,
    }


def node_weather(state: AppState) -> AppState:
    lat = os.getenv("WEATHER_LAT", "40.7282")
    lon = os.getenv("WEATHER_LON", "-74.0776")
    tz = os.getenv("WEATHER_TZ", "America/New_York")

    forecast = get_weather_forecast(lat, lon, tz)
    risk = derive_dispatch_weather_risk(forecast)
    return {"weather_forecast": forecast, "weather_risk": risk}


def node_planner(state: AppState) -> AppState:
    # Pass all required variables to the planner, including the new resources
    plan = run_planner_agent(
        business_context=state.get("business_context", ""),
        ops_insights=state.get("ops_insights", ""),
        weather_risk=state.get("weather_risk", {}),
        what_if_scenario=state.get("what_if_scenario", "No disruptions reported."),
        resource_constraints=state.get("resource_constraints", "No constraints provided.") # <--- NEW ARGUMENT PASSED
    )
    return {"dispatch_plan": plan}


def node_report(state: AppState) -> AppState:
    # NEW: Pass the what-if scenario to the report agent for executive context
    html = run_report_agent(
        business_context=state.get("business_context", ""),
        kpis=state.get("csv_kpis", {}),
        anomaly_highlights=state.get("anomalies_md", "(none)"),
        weather_risk=state.get("weather_risk", {}),
        dispatch_plan=state.get("dispatch_plan", ""),
        what_if_scenario=state.get("what_if_scenario", "No disruptions reported.")
    )
    return {"report_html": html}


def node_email(state: AppState) -> AppState:
    to_email = os.getenv("REPORT_EMAIL_TO", "").strip()
    if not to_email:
        print("REPORT_EMAIL_TO not set -> skipping email send.")
        return {}

    subject = "MSBA Ops Multi-Agent Dispatch Report"
    send_email_smtp(subject=subject, html_body=state["report_html"], to_email=to_email)
    return {}

def node_load_resources(state: AppState) -> AppState:
    try:
        df = pd.read_csv(state["resource_csv_path"])
        # Convert the dataframe to a readable string format for the LLM
        constraints = df.to_markdown(index=False) 
    except Exception as e:
        constraints = f"Error loading resources: {e}"
    
    return {"resource_constraints": constraints}


def build_graph():
    g = StateGraph(AppState)

    g.add_node("pdf_context", node_pdf_context)
    g.add_node("csv_analysis", node_csv_analysis)
    g.add_node("weather", node_weather)
    g.add_node("resources", node_load_resources) # NEW NODE
    g.add_node("planner", node_planner)
    g.add_node("report", node_report)

    g.set_entry_point("pdf_context")
    g.add_edge("pdf_context", "csv_analysis")
    g.add_edge("csv_analysis", "weather")
    g.add_edge("weather", "resources")           # NEW EDGE
    g.add_edge("resources", "planner")           # NEW EDGE
    g.add_edge("planner", "report")
    g.add_edge("report", END)

    return g.compile()
