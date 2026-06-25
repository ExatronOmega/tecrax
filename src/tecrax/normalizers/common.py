from __future__ import annotations

from typing import Any

from rexecop.execution.backend import StepExecutionContext

from tecrax.contracts import finalize_facts


def connector_results(context: StepExecutionContext) -> dict[str, Any]:
    results = context.shared_state.get("connector_results", {})
    return results if isinstance(results, dict) else {}


def store_facts(
    context: StepExecutionContext,
    state_key: str,
    facts: dict[str, Any],
) -> dict[str, Any]:
    context.shared_state[state_key] = facts
    return facts


def finalize_and_store(
    context: StepExecutionContext,
    state_key: str,
    payload: dict[str, Any],
    **metadata: Any,
) -> dict[str, Any]:
    return store_facts(
        context,
        state_key,
        finalize_facts(payload, **metadata),
    )


def stdout(results: dict[str, Any], step_id: str) -> str:
    payload = results.get(step_id)
    if not isinstance(payload, dict):
        return ""
    value = payload.get("stdout")
    return str(value) if value is not None else ""


def single_line(value: str, *, limit: int = 512) -> str:
    return " ".join(value.split())[:limit]


def integer(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def bounded_float(value: Any) -> float | None:
    try:
        result = float(str(value))
    except (TypeError, ValueError):
        return None
    return round(max(-1_000_000.0, min(result, 1_000_000.0)), 6)


def float_value(value: str) -> float | None:
    try:
        return float(value)
    except ValueError:
        return None
