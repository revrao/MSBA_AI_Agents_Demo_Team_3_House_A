# UCLA MSBA AI Agents Project Challenge 2026

## Team [Team Name]

### Enhancement 2: What-If Scenario Simulation

# Project Overview

This repository contains a multi-agent operational planning system for SeeWeeS Specialty Distribution.

Starting from the baseline LangGraph dispatch-planning prototype, we enhanced the architecture into a constraint-aware "What-If" simulation engine capable of:

- Simulating operational disruptions
- Enforcing resource constraints
- Analyzing multi-corridor shipment demand
- Generating contingency dispatch plans
- Producing executive-ready HTML reports

Our enhancement focuses on operational stress testing under hypothetical disruptions such as:
- Demand spikes
- Driver shortages
- Temperature-controlled truck failures

# Core Enhancements

## 1. What-If Scenario Simulation

The workflow now accepts dynamic disruption scenarios injected into the application state.

Example:

```python
scenario = "A 20% demand spike occurred in Corridor C2_NJ_PHL while 2 temp-controlled trucks failed on Day0."
```

The PlannerAgent dynamically adjusts dispatch recommendations based on the simulated disruption.

## 2. Resource Constraint Integration

A new LangGraph node (`node_load_resources`) loads operational resource limits from:

```text
Resource_availability_48h.csv
```

The PlannerAgent must now respect constraints for:
- Drivers
- Standard trucks
- Temperature-controlled trucks

## 3. Multi-Corridor Analytics

The enhanced CSV pipeline:
- Filters the 48-hour planning window
- Groups shipments by `corridor_id`
- Calculates corridor-level KPIs
- Evaluates shipment mix and operational risk

## 4. Appendix A Data Standardization

The CSV analysis engine now standardizes legacy identifiers using the SeeWeeS Playbook Appendix A mapping rules.

This includes:
- Legacy item ID reconciliation
- Canonical item mapping
- Item-level normalization for analytics

# Multi-Agent Workflow

```text
PDF Context Agent
        ↓
CSV Operations Analysis Agent
        ↓
Weather Risk Tool
        ↓
Resource Constraint Node
        ↓
Planner Agent
        ↓
Executive Report Agent
```

# Agent Responsibilities

## Context Agent

Extracts:
- SLAs
- Dispatch heuristics
- Planning constraints
- Weather policies

from the operational playbook using RAG.

## OpsDataAgent

Processes shipment CSV data:
- Cleans records
- Standardizes item IDs
- Calculates KPIs
- Detects anomalies using Isolation Forest

## Weather Tool

Retrieves forecast data and derives:
- Precipitation risk
- Wind risk
- Freezing risk

for dispatch corridors.

## Resource Node

Loads daily operational limits:
- Drivers
- Standard trucks
- Temperature-controlled trucks

and passes constraints into planning.

## PlannerAgent

Combines:
- Business rules
- Shipment KPIs
- Weather risk
- Resource constraints
- Hypothetical disruptions

to generate dispatch recommendations and tradeoff decisions.

## ReportAgent

Produces a skimmable HTML executive report containing:
- KPI impacts
- Dispatch plans
- SLA risks
- Resource tradeoffs
- Contingency recommendations

# Project Structure

```text
.
├── data-for-enhancement/
│   ├── SeeWeeS Specialty Dispatch Playbook.pdf
│   ├── Incoming_shipments_14d_multi_corridor.csv
│   └── Resource_availability_48h.csv
│
├── src/
│   ├── main.py
│   ├── graph.py
│   ├── agents.py
│   ├── prompts.py
│   └── tools/
│
├── chroma_db/
├── requirements.txt
├── .env.example
└── README.md
```

# Setup Instructions

## 1. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Create a `.env` file:

```env
OPENAI_API_KEY="your-api-key"
LANGCHAIN_TRACING_V2=false
```

## 4. Run the System

From the repository root:

```bash
python src/main.py
```

# Example Scenario

```python
scenario = "A 20% demand spike occurred in Corridor C2_NJ_PHL while 2 temp-controlled trucks failed on Day0."
```

The system generates:
- KPI impact analysis
- Dispatch recommendations
- Corridor prioritization
- Contingency planning
- HTML executive reports

# Output

The workflow produces:
- Terminal report preview
- Full HTML report (`output_report.html`)
- Operational recommendations under simulated disruptions

# Key Technologies

- Python
- LangGraph
- LangChain
- OpenAI API
- ChromaDB
- Pandas
- Scikit-learn
- Open-Meteo API