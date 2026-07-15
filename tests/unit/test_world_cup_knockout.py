from datetime import datetime

import pytest

from underdog_lab.world_cup.data import TournamentRepository


def test_repository_exposes_group_and_knockout_fixture_sets():
    repository = TournamentRepository()

    assert len(repository.fixtures) == 72
    assert len(repository.knockout_fixtures) == 32
    assert len(repository.tournament_fixtures) == 104
    assert {fixture.match_number for fixture in repository.knockout_fixtures} == set(
        range(73, 105)
    )


def test_repository_preserves_played_semifinal_and_unresolved_final():
    repository = TournamentRepository()

    semifinal = next(
        fixture for fixture in repository.knockout_fixtures if fixture.match_number == 101
    )
    final = next(
        fixture for fixture in repository.knockout_fixtures if fixture.match_number == 104
    )

    assert semifinal.stage == "semifinal"
    assert {semifinal.home, semifinal.away} == {"Spain", "France"}
    assert sorted((semifinal.home_goals, semifinal.away_goals)) == [0, 2]
    assert semifinal.winner == "Spain"
    assert final.stage == "final"
    assert final.home == "Spain"
    assert final.away == "Semifinal 2 Winner"
    assert not final.played


def test_knockout_fixture_rejects_invalid_match_number():
    from underdog_lab.world_cup.models import KnockoutFixture

    with pytest.raises(ValueError):
        KnockoutFixture(
            fixture_id="WC26-072",
            match_number=72,
            stage="final",
            date="2026-07-19",
            kickoff_utc=datetime.fromisoformat("2026-07-19T19:00:00+00:00"),
            home="Spain",
            away="England",
        )
