from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, Tuple, List
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


@dataclass
class CsvAnalysisResult:
    summary: Dict[str, Any]
    kpis: Dict[str, Any]
    anomalies: pd.DataFrame
    cleaned_shape: Tuple[int, int]
    numeric_cols: List[str]


def analyze_csv(csv_path: str) -> CsvAnalysisResult:
    df = pd.read_csv(csv_path)
    original_shape = df.shape

    df.columns = [c.strip() for c in df.columns]
    df = df.dropna(how="all").copy()

    # Try to parse any column that looks like a date
    for c in df.columns:
        if "date" in c.lower() or "time" in c.lower():
            try:
                df[c] = pd.to_datetime(df[c], errors="ignore")
            except Exception:
                pass

    summary = {
        "rows_original": int(original_shape[0]),
        "cols_original": int(original_shape[1]),
        "rows_after_drop_empty": int(df.shape[0]),
        "missingness_top": df.isna().mean().sort_values(ascending=False).head(10).to_dict(),
        "column_dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "columns": list(df.columns),
    }

    # Generic KPI examples: you will tailor later once we see headers
    kpis: Dict[str, Any] = {}

    # ---------------------------------------------------------
    # NEW LOGIC: Reconcile Item IDs using Appendix A Rules
    # ---------------------------------------------------------
    if "item_id" in df.columns: # Or whichever column contains the messy IDs
        # 1. Create a mapping dictionary based on Appendix A from the Playbook.
        # (NOTE: You must look at the actual Playbook MD file and fill in these exact values!)
        appendix_a_mapping = {
            "LEGACY-ID-001": "STANDARD-ID-A",
            "OLD-TEMP-VAC": "VAC-100",
            "MISSING-999": "STANDARD-ID-B"
            # Add all the rules from Appendix A here...
        }
        
        # 2. Apply the mapping to the dataframe to standardize the IDs
        df["item_id"] = df["item_id"].replace(appendix_a_mapping)
        
        # Now your dataframe has clean data!
    # ---------------------------------------------------------

    # ENHANCEMENT LOGIC: Multi-corridor KPIs
    if "corridor_id" in df.columns and "is_planning_window" in df.columns:
        # Filter for only the next 48 hours
        planning_df = df[df["is_planning_window"] == True]
        
        # Calculate volume by corridor
        volume_by_corridor = planning_df.groupby("corridor_id").size().to_dict()
        kpis["volume_by_corridor_48h"] = volume_by_corridor
        
        # Now that the IDs are clean, you can calculate the mix!
        if "item_id" in planning_df.columns:
            item_mix = planning_df.groupby(["corridor_id", "item_id"]).size().unstack(fill_value=0).to_dict(orient="index")
            kpis["item_mix_by_corridor"] = item_mix
        
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if numeric_cols:
        kpis["numeric_columns_count"] = len(numeric_cols)
        kpis["rows_count"] = int(df.shape[0])

    # Anomalies on numeric cols
    anomalies = pd.DataFrame()
    if len(numeric_cols) >= 2 and df.shape[0] >= 20:
        X = df[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(0.0).values
        model = IsolationForest(
            n_estimators=200,
            contamination=0.03,
            random_state=42,
        )
        preds = model.fit_predict(X)
        scores = model.decision_function(X)

        df_anom = df.copy()
        df_anom["is_anomaly"] = (preds == -1)
        df_anom["anomaly_score"] = scores

        anomalies = df_anom[df_anom["is_anomaly"]].sort_values("anomaly_score").head(25)

    return CsvAnalysisResult(
        summary=summary,
        kpis=kpis,
        anomalies=anomalies,
        cleaned_shape=df.shape,
        numeric_cols=numeric_cols,
    )
