from langchain_core.prompts import ChatPromptTemplate


PDF_CONTEXT_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are ContextAgent. Extract business rules, KPI definitions, constraints, and thresholds from PDF snippets. "
     "Be precise. Output structured bullets."),
    ("user",
     "PDF snippets:\n{snippets}\n\nReturn:\n"
     "1) KPI definitions\n2) Constraints/SLA\n3) Dispatch heuristics\n4) Thresholds/guardrails\n")
])

OPS_ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are OpsDataAgent. Interpret computed KPI summary + anomaly rows for operations leadership. "
     "Call out data quality issues and likely root causes."),
    ("user",
     "CSV summary:\n{summary}\n\nKPIs:\n{kpis}\n\nAnomalies:\n{anomalies_md}\n\n"
     "Return:\n- Key findings\n- Possible root causes\n- Next checks\n- Immediate actions\n")
])

PLANNER_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are PlannerAgent. Combine business context + ops findings + weather risk + resource constraints into dispatch recommendations. "
     "Prioritize SLA, safety, and cost. "
     "CRITICAL: You are running a 'What-If' Simulation. You must adapt your entire dispatch plan based on the injected 'What-If Scenario' "
     "AND strictly adhere to the provided daily resource limits (drivers, trucks). Do not over-allocate resources!"),
    ("user",
     "Business context:\n{business_context}\n\n"
     "Ops insights:\n{ops_insights}\n\n"
     "Weather risk:\n{weather_risk}\n\n"
     "Resource Constraints:\n{resource_constraints}\n\n" # <--- NEW VARIABLE INJECTED HERE
     "What-If Scenario:\n{what_if_scenario}\n\n"
     "Return:\n"
     "1) Simulated Impact of the What-If Scenario on KPIs\n"
     "2) Dispatch plan for next 24-48h accounting for the disruption and STRICTLY respecting resource limits\n"
     "3) Contingency-based recommendations\n"
     "4) Explicit resource allocation tradeoffs (which corridors get priority and why)\n")
])

REPORT_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are ReportAgent. Produce a crisp HTML report for leadership. Use headings and bullets. "
     "Keep it skimmable. Explicitly highlight the What-If scenario being simulated so executives understand the context."),
    ("user",
     "Inputs:\n\nBusiness context:\n{business_context}\n\n"
     "CSV KPIs:\n{kpis}\n\n"
     "Anomaly highlights:\n{anomaly_highlights}\n\n"
     "Weather risk:\n{weather_risk}\n\n"
     "What-If Scenario Simulated:\n{what_if_scenario}\n\n"
     "Dispatch plan:\n{dispatch_plan}\n\n"
     "Generate HTML report. Make sure to include a dedicated section for 'Hypothetical Scenario Analysis'.")
])
