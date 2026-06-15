from __future__ import annotations

import json

from underdog_lab.world_cup.data import TournamentRepository
from underdog_lab.world_cup.predictions import scored_track_records


def _metrics(summary: dict) -> dict:
    return {
        key: summary[key]
        for key in (
            "n",
            "mean_log_loss",
            "mean_brier",
            "mean_rps",
            "uniform_log_loss",
        )
    }


def main() -> int:
    repository = TournamentRepository()
    records = scored_track_records(
        repository.fixtures,
        repository.team_by_name,
    )
    report = {
        "recorded_fixtures": sum(fixture.played for fixture in repository.fixtures),
        "artifact_audit": records["artifact_audit"],
        "prospective_latest": _metrics(records["prospective"]),
        "prospective_by_horizon": {
            horizon: _metrics(summary)
            for horizon, summary in records["prospective_by_horizon"].items()
        },
        "retrospective": _metrics(records["retrospective"]),
    }
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
