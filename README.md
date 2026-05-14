# UCLA MSBA AI Agents Project Challenge 2026

**Team [Your Team Name / House Name]** **Core Focus:** Enhancement 2 — The "What-If" Scenario Simulation

## 🚀 Project Overview

This repository contains an advanced multi-agent system designed to manage operational and dispatch planning for SeeWeeS Specialty Distribution.

We transformed the baseline linear reporting prototype into a **dynamic, constraint-aware simulation engine**. By extending the LangGraph architecture, our system now ingests multi-corridor shipment data, strictly adheres to daily resource limits, standardizes messy legacy data, and allows leadership to inject hypothetical supply chain disruptions (e.g., driver shortages, demand spikes) to instantly generate contingency-based dispatch plans.

## 🧠 Key Enhancements & Technical Methodology

* **"What-If" Scenario Injection:** The user can pass dynamic disruption scenarios into the `AppState`, which the `PlannerAgent` processes to dynamically recalculate KPIs and adjust the dispatch strategy.
* **Resource Constraint Node (`node_load_resources`):** A new agentic step that parses `Resource_availability_48h.csv` to ensure the Planner strictly adheres to physical limitations (Drivers, Standard Trucks, Temp-Controlled Trucks).
* **Data Standardization (Appendix A):** Upgraded `csv_tools.py` to automatically reconcile legacy item IDs and missing identifiers based on the SeeWeeS Playbook Appendix A before calculating KPIs.
* **Multi-Corridor Analytics:** Re-engineered the ops data analysis to specifically slice the 48-hour planning window by `corridor_id` to evaluate workload mix and risk properly.

## 🏗️ Multi-Agent Architecture

Our LangGraph workflow operates as follows:

1. **Context Agent (RAG):** Extracts SLAs, dispatch heuristics, and routing waypoints from the SeeWeeS Playbook.
2. **Ops Data Agent:** Cleans the multi-corridor CSV feed, standardizes legacy IDs, isolates the 48h planning window, and identifies data anomalies via Isolation Forests.
3. **Weather Tool:** Pulls live forecast data and calculates weather-related routing risks.
4. **Resource Node (New):** Parses actual fleet and driver availability limits.
5. **Planner Agent (Enhanced):** Integrates business rules, clean corridor demand, weather risks, rigid resource constraints, and **user-defined "What-If" scenarios** to output an optimized, heavily constrained dispatch strategy.
6. **Report Agent:** Generates a skimmable HTML brief specifically highlighting the hypothetical scenario, tradeoffs made, and C-suite action items.

## 📂 Project Structure

```text
.
├── data-for-enhancement/          # Student artifacts for the simulation
│   ├── SeeWeeS Specialty Dispatch Playbook.md
│   ├── Incoming_shipments_14d_multi_corridor.csv
│   └── Resource_availability_48h.csv
├── src/                           # Core application code
│   ├── main.py                    # Graph execution & scenario injection
│   ├── graph.py                   # LangGraph nodes and edges
│   ├── agents.py                  # LLM wrappers and invocations
│   ├── prompts.py                 # System and user prompts
│   └── tools/                     # Utility scripts (csv, weather, email, pdf)
├── chroma_db/                     # Local vector store (Generated dynamically)
├── requirements.txt               # Dependencies
├── .env.example                   # Template for environment variables
└── README.md                      # Deployment guide

```

## 🛠️ Setup & Deployment Guide

### 1. Environment Setup

We recommend using Python 3.11+. Clone the repository and set up your virtual environment:

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

```

### 2. Configure API Keys

You must provide an OpenAI API key to run the agents. LangSmith tracing is highly recommended for viewing the agent thought process.

```bash
# Copy the example environment file
cp .env.example .env

```

Open `.env` and add your credentials:

```env
OPENAI_API_KEY="sk-your-api-key"
LANGCHAIN_TRACING_V2="true"
LANGCHAIN_API_KEY="lsv2_your-langsmith-key"
LANGCHAIN_PROJECT="SeeWeeS_Simulation"
REPORT_EMAIL_TO="executive@yourcompany.com" # Optional

```

### 3. Running a "What-If" Scenario

To test the simulation, open `main.py` and modify the `scenario` variable in the execution block.

```python
# Inside main.py
scenario = "A severe driver shortage occurred in Corridor A resulting in 30% fewer drivers. We also see a 15% demand spike for Temp-Controlled Vaccines."

```

Execute the system from the root directory:

```bash
python src/main.py

```

### 4. Viewing the Output

Upon completion, the application will:

1. Print the generated executive report (HTML format) directly to the console.
2. Email the report to the address specified in `REPORT_EMAIL_TO` (if SMTP is configured).
3. If tracing is enabled, you can view the step-by-step LLM inputs/outputs at [smith.langchain.com](https://smith.langchain.com).
