from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from underdog_lab.config import DATA_DIR
from underdog_lab.world_cup.data import TournamentRepository
from underdog_lab.world_cup.providers import normalize_football_data_response

API_URL = "https://api.football-data.org/v4/competitions/WC/matches"
MAPPING_PATH = (
    DATA_DIR / "world_cup_2026/provider_mappings/football_data.json"
)
UPDATE_PATH = DATA_DIR / "world_cup_2026/result_updates/pending-football-data.json"


def fetch_payload(token: str) -> dict:
    query = urllib.parse.urlencode({"season": 2026, "stage": "GROUP_STAGE"})
    request = urllib.request.Request(
        f"{API_URL}?{query}",
        headers={"X-Auth-Token": token, "User-Agent": "underdog-lab-results"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"football-data.org returned HTTP {error.code}"
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-json", type=Path)
    parser.add_argument("--output", type=Path, default=UPDATE_PATH)
    args = parser.parse_args()
    token = os.getenv("FOOTBALL_DATA_API_KEY")
    if args.input_json:
        payload = json.loads(args.input_json.read_text(encoding="utf-8"))
    elif token:
        payload = fetch_payload(token)
    else:
        parser.error("FOOTBALL_DATA_API_KEY or --input-json is required")

    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    normalized = normalize_football_data_response(
        payload,
        TournamentRepository(),
        mapping["aliases"],
        fetched_at=datetime.now(timezone.utc),
    )
    for fixture_id in normalized.get("unscored_finished", []):
        print(
            f"::warning::{fixture_id} is reported FINISHED but the provider "
            "has not published a score yet; skipping for this poll."
        )

    if not normalized["results"] and not normalized["corrections"]:
        print("no new results")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(normalized, indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    print(
        f"additions={len(normalized['results'])} "
        f"corrections={len(normalized['corrections'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
