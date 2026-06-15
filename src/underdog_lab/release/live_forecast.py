from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from underdog_lab.world_cup.data import TournamentRepository
from underdog_lab.world_cup.forecasting import match_forecast
from underdog_lab.world_cup.integrity import validate_snapshot_integrity
from underdog_lab.world_cup.provenance import forecast_provenance


def _commit() -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        text=True,
    ).strip()


def generate_live_forecast(
    fixture_id: str,
    output_dir: Path,
    *,
    now: datetime | None = None,
    snapshot_path: Path | None = None,
) -> tuple[Path, Path]:
    repository = TournamentRepository(snapshot_path=snapshot_path)
    validate_snapshot_integrity(repository, now=now)
    fixture = next(
        (item for item in repository.fixtures if item.fixture_id == fixture_id),
        None,
    )
    if fixture is None:
        raise ValueError(f"Unknown fixture: {fixture_id}")
    if fixture.played:
        raise ValueError(f"{fixture_id} already has a recorded result")
    if fixture.kickoff_utc is None:
        raise ValueError(f"{fixture_id} has no verified kickoff_utc")

    generated_at = now or datetime.now(timezone.utc)
    cutoff = datetime.fromisoformat(
        repository.snapshot["information_cutoff"].replace("Z", "+00:00")
    )
    if cutoff > generated_at:
        raise ValueError("information_cutoff cannot be after generated_at")
    if generated_at >= fixture.kickoff_utc:
        raise ValueError("Live forecast must be generated before kickoff")

    forecast = match_forecast(fixture, repository.team_by_name)
    fixture_payload = {
        "fixture_id": fixture.fixture_id,
        "group": fixture.group,
        "date": fixture.date.isoformat(),
        "kickoff_utc": fixture.kickoff_utc.isoformat(),
        "home": fixture.home,
        "away": fixture.away,
        "p_home": round(forecast.p_home, 8),
        "p_draw": round(forecast.p_draw, 8),
        "p_away": round(forecast.p_away, 8),
        "lambda_home": round(forecast.lambda_home, 8),
        "lambda_away": round(forecast.lambda_away, 8),
    }
    payload = {
        "schema_version": "live-forecast-v2",
        "forecast_date": fixture.date.isoformat(),
        "information_cutoff": repository.snapshot["information_cutoff"],
        "generated_at": generated_at.isoformat(),
        "forecast_horizon_seconds": int(
            (fixture.kickoff_utc - generated_at).total_seconds()
        ),
        "commit": _commit(),
        "model": "Elo-to-goals Dixon-Coles fitted model",
        "provenance": forecast_provenance(),
        "fixtures": [fixture_payload],
        "sources": list(
            dict.fromkeys(
                [
                    *repository.snapshot.get("sources", []),
                    repository.kickoff_schedule["source"],
                ]
            )
        ),
    }
    output_dir.mkdir(parents=True, exist_ok=False)
    forecast_path = output_dir / "forecast.json"
    forecast_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    digest = hashlib.sha256(forecast_path.read_bytes()).hexdigest()
    manifest = {
        "algorithm": "sha256",
        "file": "forecast.json",
        "sha256": digest,
        "immutable": True,
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return forecast_path, manifest_path
