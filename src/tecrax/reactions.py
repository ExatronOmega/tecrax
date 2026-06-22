from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping

from rexecop.profile.loader import load_profile
from rexecop.reaction.compiler import compile_reaction_pack
from sclite import build_observation_envelope


def build_monitoring_host_observation(
    *,
    operation_id: str,
    target_id: str,
    diagnosis: Mapping[str, Any],
    observed_at: str | None = None,
) -> dict[str, Any]:
    """Project one bounded Tecrax diagnosis into the canonical SCLite envelope."""
    profile = load_profile(Path(__file__).resolve().parent / "profile")
    pack = compile_reaction_pack(profile)
    return build_observation_envelope(
        observation_id=f"observation:{operation_id}:monitoring-host",
        observed_at=observed_at or datetime.now(UTC).isoformat(),
        profile_ref={
            "id": profile.name,
            "version": profile.version,
            "digest": pack.profile_digest,
        },
        operation_id=operation_id,
        intent_id="diagnose_monitoring_host",
        target_id=target_id,
        facts=dict(diagnosis),
    )
