from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()
from tracing import init_langsmith_tracing
init_langsmith_tracing()
from graph import build_graph

if __name__ == "__main__":
 
    app = build_graph()

    # Define the scenario you want to test
    scenario = "A severe driver shortage occurred in corridor A, resulting in 30% fewer available standard trucks. At the same time, we experienced a 20% demand spike."

    state = {
        "pdf_path": "data/SeeWeeS Specialty distribution.pdf",
        "csv_path": "data/Incoming_shipment_02_08.csv",
        "what_if_scenario": scenario, # NEW: Inject scenario here
    }

    final = app.invoke(state)

    report_html = final.get("report_html", "")
    print("\n=== REPORT (first 2000 chars) ===\n")
    print(report_html[:2000])
