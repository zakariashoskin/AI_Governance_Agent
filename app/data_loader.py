"""Data access helpers for synthetic advisory workflow data."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def read_csv(name: str) -> pd.DataFrame:
    """Load a CSV file from the synthetic data directory."""

    return pd.read_csv(DATA_DIR / name)


def dataframe_records(name: str) -> list[dict[str, Any]]:
    """Return CSV data as dictionaries for agent tools."""

    return read_csv(name).to_dict(orient="records")


def get_customer_by_name(customer_name: str) -> dict[str, Any]:
    customers = read_csv("customers.csv")
    match = customers[customers["customer_name"].str.lower() == customer_name.lower()]
    if match.empty:
        raise ValueError(f"Customer not found: {customer_name}")
    return match.iloc[0].to_dict()


def get_customer_by_id(customer_id: str) -> dict[str, Any]:
    customers = read_csv("customers.csv")
    match = customers[customers["customer_id"] == customer_id]
    if match.empty:
        raise ValueError(f"Customer not found: {customer_id}")
    return match.iloc[0].to_dict()


def get_customer_names() -> list[str]:
    return read_csv("customers.csv")["customer_name"].tolist()


def get_signal_sources(customer_id: str | None = None) -> list[str]:
    signals = read_csv("signals.csv")
    if customer_id:
        signals = signals[signals["customer_id"] == customer_id]
    return signals["signal_source"].drop_duplicates().tolist()
