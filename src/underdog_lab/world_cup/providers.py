from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone

from underdog_lab.world_cup.data import TournamentRepository

GROUP_STAGE = "GROUP_STAGE"
FINISHED = "FINISHED"


def normalize_football_data_response(
    payload: dict,
    repository: TournamentRepository,
    aliases: dict[str, str],
    *,
    fetched_at: datetime | None = None,
    kickoff_tolerance_minutes: int = 180,
) -> dict:
    fetched_at = fetched_at or datetime.now(timezone.utc)
    competition = payload.get("competition") or {}
    matches = payload.get("matches") or []
    season = payload.get("season") or next(
        (match.get("season") for match in matches if match.get("season")),
        {},
    )
    if competition.get("code") != "WC":
        raise ValueError("football-data response is not competition WC")
    if not str(season.get("startDate", "")).startswith("2026-"):
        raise ValueError("football-data response is not the 2026 World Cup season")

    fixture_by_pair = {
        (fixture.home, fixture.away): (fixture, False)
        for fixture in repository.fixtures
    }
    fixture_by_pair.update(
        {
            (fixture.away, fixture.home): (fixture, True)
            for fixture in repository.fixtures
        }
    )
    existing = {
        (row["group"], row["home"], row["away"]): row
        for row in repository.snapshot["results"]
    }
    additions = []
    corrections = []
    provider_matches = []
    unscored_finished = []
    seen_fixture_ids = set()
    discovered_team_ids = {}
    discovered_match_ids = {}
    for match in matches:
        if match.get("stage") != GROUP_STAGE:
            continue
        home_team = match.get("homeTeam") or {}
        away_team = match.get("awayTeam") or {}
        home = _team_name(home_team, aliases)
        away = _team_name(away_team, aliases)
        fixture_match = fixture_by_pair.get((home, away))
        if fixture_match is None:
            raise ValueError(f"unmapped World Cup fixture: {home} vs {away}")
        fixture, reversed_orientation = fixture_match
        if fixture.fixture_id in seen_fixture_ids:
            raise ValueError(f"duplicate provider match for {fixture.fixture_id}")
        seen_fixture_ids.add(fixture.fixture_id)
        _record_team_id(discovered_team_ids, home_team, home)
        _record_team_id(discovered_team_ids, away_team, away)
        if match.get("id") is not None:
            discovered_match_ids[str(match["id"])] = fixture.fixture_id
        provider_kickoff = _timestamp(match.get("utcDate"))
        if provider_kickoff is None:
            raise ValueError(f"missing provider kickoff for {fixture.fixture_id}")
        delta = abs((provider_kickoff - fixture.kickoff_utc).total_seconds()) / 60
        if delta > kickoff_tolerance_minutes:
            raise ValueError(
                f"kickoff mismatch for {fixture.fixture_id}: {delta:.0f} minutes"
            )
        provider_matches.append(
            {
                "provider_match_id": match.get("id"),
                "fixture_id": fixture.fixture_id,
                "status": match.get("status"),
                "last_updated": match.get("lastUpdated"),
                "provider_kickoff_utc": provider_kickoff.isoformat(),
            }
        )
        if match.get("status") != FINISHED:
            continue
        score = match.get("score") or {}
        full_time = score.get("regularTime") or score.get("fullTime") or {}
        home_goals = full_time.get("home")
        away_goals = full_time.get("away")
        if home_goals is None or away_goals is None:
            # football-data.org sometimes reports a match FINISHED before the
            # score fields are populated. Skip just this match so other
            # results in the same poll are not lost; it will be picked up on
            # a later poll once the provider backfills the score.
            unscored_finished.append(fixture.fixture_id)
            continue
        if reversed_orientation:
            home_goals, away_goals = away_goals, home_goals
        row = {
            "provider": "football-data.org",
            "provider_match_id": match.get("id"),
            "provider_last_updated": match.get("lastUpdated"),
            "fixture_id": fixture.fixture_id,
            "group": fixture.group,
            "home": fixture.home,
            "away": fixture.away,
            "home_goals": int(home_goals),
            "away_goals": int(away_goals),
        }
        old = existing.get((fixture.group, fixture.home, fixture.away))
        if old is None:
            additions.append(row)
        elif (
            old["home_goals"] != row["home_goals"]
            or old["away_goals"] != row["away_goals"]
        ):
            corrections.append(
                {
                    **row,
                    "previous_home_goals": old["home_goals"],
                    "previous_away_goals": old["away_goals"],
                }
            )

    cutoff = safe_information_cutoff(
        repository,
        additions,
        corrections,
        fetched_at=fetched_at,
    )
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return {
        "provider": "football-data.org",
        "fetched_at": fetched_at.isoformat(),
        "competition": {
            "id": competition.get("id"),
            "code": competition.get("code"),
            "name": competition.get("name"),
        },
        "season": {
            "id": season.get("id"),
            "startDate": season.get("startDate"),
            "endDate": season.get("endDate"),
        },
        "raw_response_sha256": hashlib.sha256(raw).hexdigest(),
        "information_cutoff": cutoff.isoformat().replace("+00:00", "Z"),
        "sources": ["https://api.football-data.org/v4/competitions/WC/matches"],
        "results": additions,
        "corrections": corrections,
        "unscored_finished": unscored_finished,
        "provider_matches": provider_matches,
        "mapping_discovery": {
            "provider_team_ids": discovered_team_ids,
            "provider_match_ids": discovered_match_ids,
        },
    }


def safe_information_cutoff(
    repository: TournamentRepository,
    additions: list[dict],
    corrections: list[dict],
    *,
    fetched_at: datetime,
) -> datetime:
    recorded = {
        (row["group"], row["home"], row["away"])
        for row in repository.snapshot["results"]
    }
    recorded.update(
        (row["group"], row["home"], row["away"])
        for row in additions + corrections
    )
    missing = [
        fixture
        for fixture in repository.fixtures
        if (fixture.group, fixture.home, fixture.away) not in recorded
        and fixture.kickoff_utc <= fetched_at
    ]
    if not missing:
        return fetched_at
    earliest = min(fixture.kickoff_utc for fixture in missing)
    return min(fetched_at, earliest - timedelta(seconds=1))


def _team_name(team: dict, aliases: dict[str, str]) -> str:
    candidates = [
        str(team.get("id", "")),
        team.get("name"),
        team.get("shortName"),
        team.get("tla"),
    ]
    for candidate in candidates:
        if candidate in aliases:
            return aliases[candidate]
    raise ValueError(f"unmapped provider team: {team}")


def _record_team_id(discovered: dict[str, str], team: dict, name: str) -> None:
    provider_id = team.get("id")
    if provider_id is not None:
        discovered[str(provider_id)] = name


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
