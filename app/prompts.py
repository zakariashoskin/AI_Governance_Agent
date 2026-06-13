"""Prompt templates and placeholder LLM wrapper for the MVP."""

from __future__ import annotations

import os
from typing import Any


SYSTEM_PROMPT = """
You are an AI advisor agent for financial-sector advisory work.
You may generate hypotheses from aggregated synthetic data, but you must not
make final strategic recommendations without human validation.
"""


class LLMClient:
    """Replaceable LLM wrapper.

    The MVP uses deterministic placeholder generation unless OPENAI_API_KEY is
    present and a real provider is added later.
    """

    def __init__(self) -> None:
        self.api_key_available = bool(os.getenv("OPENAI_API_KEY"))

    def generate_advisory_hypotheses(
        self,
        customer_context: dict[str, Any],
        claims_analysis: dict[str, Any],
        benchmark_comparison: dict[str, Any],
    ) -> list[str]:
        stress_direction = "above" if benchmark_comparison["stress_gap"] > 0 else "at or below"
        absence_direction = "above" if benchmark_comparison["absence_gap"] > 0 else "at or below"

        hypotheses = [
            (
                f"Stress-related claims are {stress_direction} the industry benchmark "
                f"with a gap of {benchmark_comparison['stress_gap']} per 100 employees."
            ),
            (
                f"Absence levels are {absence_direction} benchmark with a gap of "
                f"{benchmark_comparison['absence_gap']} days per employee."
            ),
            (
                "The next advisory step should validate whether internal workload, "
                "organizational change, leadership practices, or benefit awareness "
                "explain the observed pattern."
            ),
        ]

        if not customer_context["organizational_context_available"]:
            hypotheses.append(
                "Organizational context is missing, so HR or stakeholder input is needed "
                "before proposing a specific intervention."
            )

        return hypotheses
