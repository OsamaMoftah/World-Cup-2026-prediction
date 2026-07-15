#!/usr/bin/env python3
"""Fetch and persist the live ESPN knockout bracket for the 2026 World Cup."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

from underdog_lab.world_cup.providers import normalize_espn_knockout_response


ENDPOINT = (
    "https://site.api.espn.com/apis/site/v2/sports/soccer/"
    "fifa.world/scoreboard?dates=2026&limit=1000"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/world_cup_2026/knockout.json"),
    )
    parser.add_argument(
        "--mapping",
        type=Path,
        default=Path("data/world_cup_2026/provider_mappings/espn.json"),
    )
    args = parser.parse_args()
    fetched_at = datetime.now(timezone.utc)
    request = Request(ENDPOINT, headers={"User-Agent": "underdog-lab/1.0"})
    with urlopen(request, timeout=30) as response:
        payload = json.load(response)
    mapping = json.loads(args.mapping.read_text(encoding="utf-8"))
    snapshot = normalize_espn_knockout_response(
        payload, mapping.get("aliases", {}), fetched_at=fetched_at
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(snapshot, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    played = sum(match["winner"] is not None for match in snapshot["matches"])
    print(f"wrote {len(snapshot['matches'])} knockout matches ({played} played) to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
