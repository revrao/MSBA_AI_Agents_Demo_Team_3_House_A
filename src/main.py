from __future__ import annotations
from dotenv import load_dotenv
load_dotenv()
from tracing import init_langsmith_tracing
init_langsmith_tracing()
from graph import build_graph
 
if __name__ == "__main__":
    app = build_graph()

    # Define the scenario you want to test
    scenario = "We are experiencing a 20% demand spike in Corridor B, but 2 of our temp-controlled trucks broke down today."

    state = {
        # Assuming you either convert the MD to PDF, or update pdf_tools.py to read text/markdown
        "pdf_path": "data-for-enhancement/SeeWeeS Specialty Dispatch Playbook.pdf", 
        "csv_path": "data-for-enhancement/Incoming_shipments_14d_multi_corridor.csv",
        "resource_csv_path": "data-for-enhancement/Resource_availability_48h.csv", # NEW
        "what_if_scenario": scenario,
    }

    final = app.invoke(state)

    report_html = final.get("report_html", "")
    print("\n=== REPORT (first 2000 chars) ===\n")
    print(report_html[:2000])
