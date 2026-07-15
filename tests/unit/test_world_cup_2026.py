from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

from underdog_lab.world_cup.bracket import (
    KNOCKOUT_PATH,
    ROUND_OF_32_SLOTS,
    THIRD_PLACE_MATCH,
    assign_third_place_groups,
    build_round_of_32,
)
from underdog_lab.world_cup.data import TournamentRepository
from underdog_lab.world_cup.forecasting import match_forecast
from underdog_lab.world_cup.simulation import (
    _knockout_win_probability,
    simulate_tournament,
)
from underdog_lab.world_cup.ui import (
    confidence_tier,
    normalize_forecast_view,
    overdue_results_note,
    upcoming_html,
)
from underdog_lab.world_cup.models import Standing
from underdog_lab.world_cup.standings import calculate_standings, rank_standings


def test_repository_contains_full_group_stage():
    repository = TournamentRepository()

    assert len(repository.teams) == 48
    assert len(repository.fixtures) == 72
    assert repository.team_by_name["Spain"].elo == 2157
    assert repository.team_by_name["Scotland"].elo == 1782
    assert all(len(repository.group_teams(group)) == 4 for group in "ABCDEFGHIJKL")
    assert all(
        len(repository.group_fixtures(group)) == 6 for group in "ABCDEFGHIJKL"
    )
    assert repository.group_fixtures("B")[1].date.isoformat() == "2026-06-13"
    assert repository.group_fixtures("D")[1].date.isoformat() == "2026-06-13"
    assert all(fixture.kickoff_utc is not None for fixture in repository.fixtures)


def test_overdue_results_note_reports_unresolved_fixtures():
    repository = TournamentRepository(
        snapshot_path=Path("tests/fixtures/world_cup/current_snapshot.json")
    )
    earliest_kickoff = min(
        fixture.kickoff_utc for fixture in repository.fixtures
    )

    assert overdue_results_note(repository, now=earliest_kickoff) == (
        "All recorded results are up to date."
    )

    much_later = datetime(2027, 1, 1, tzinfo=timezone.utc)
    note = overdue_results_note(repository, now=much_later)
    assert "match(es) have kicked off but a result has not been recorded" in note
    assert "WC26-025" in note


def test_complete_snapshot_produces_final_group_a_table():
    repository = TournamentRepository()
    standings = calculate_standings(
        [team.team for team in repository.group_teams("A")],
        repository.group_fixtures("A"),
    )

    assert standings[0].team == "Mexico"
    assert standings[0].points == 9
    assert standings[1].team == "South Africa"
    assert standings[1].points == 4
    assert sum(row.played for row in standings) == 12


def test_head_to_head_breaks_equal_points_before_overall_goal_difference():
    table = {
        "Alpha": Standing(team="Alpha", points=6, goals_for=10, goals_against=1),
        "Beta": Standing(team="Beta", points=6, goals_for=3, goals_against=2),
    }

    ranked = rank_standings(
        table,
        [("Beta", "Alpha", 1, 0)],
        fifa_ranks={"Alpha": 1, "Beta": 20},
    )

    assert [row.team for row in ranked] == ["Beta", "Alpha"]


def test_match_forecast_is_normalized():
    repository = TournamentRepository()
    forecast = match_forecast(repository.fixtures[0], repository.team_by_name)

    assert abs(forecast.p_home + forecast.p_draw + forecast.p_away - 1.0) < 1e-9
    assert forecast.lambda_home > 0
    assert forecast.lambda_away > 0


def test_host_flag_does_not_apply_an_ungated_rating_boost():
    repository = TournamentRepository()
    mexico = repository.team_by_name["Mexico"]

    assert mexico.host is True
    assert mexico.rating == mexico.elo


def test_upcoming_html_reports_completed_group_stage():
    repository = TournamentRepository()
    html = upcoming_html(repository, mode="compact")

    assert "All group-stage fixtures have been played" in html
    assert "Check the knockout bracket for upcoming matches" in html
    assert "What the model predicts next" not in html


def test_confidence_tiers_distinguish_signal_strength():
    assert confidence_tier(0.65, 0.2) == "Concentrated forecast"
    assert confidence_tier(0.52, 0.11) == "Moderate lean"
    assert confidence_tier(0.42, 0.06) == "Narrow lean"
    assert confidence_tier(0.36, 0.02) == "Near-even"


def test_forecast_view_accepts_gradio_values_and_legacy_labels():
    assert normalize_forecast_view("probability") == "probability"
    assert normalize_forecast_view("Probability view") == "probability"
    assert normalize_forecast_view("compact") == "compact"
    assert normalize_forecast_view("Pick mode") == "compact"
    assert normalize_forecast_view(None) == "probability"


def test_simulation_produces_one_champion_per_iteration():
    repository = TournamentRepository()
    probabilities = simulate_tournament(repository, iterations=100, seed=7)

    assert abs(sum(row["champion"] for row in probabilities.values()) - 1.0) < 1e-9
    assert all(0.0 <= row["advance"] <= 1.0 for row in probabilities.values())
    assert all(
        row["champion"] <= row["final"] <= row["semifinal"]
        for row in probabilities.values()
    )


def test_knockout_probability_is_compressed_and_symmetric():
    repository = TournamentRepository()
    spain = _knockout_win_probability("Spain", "South Africa", repository)
    south_africa = _knockout_win_probability(
        "South Africa",
        "Spain",
        repository,
    )

    # Spain vs South Africa is the largest Elo gap in the field (~650). The
    # fitted Dixon-Coles model clamps lambda_home at 4.0 for gaps this
    # large, so the result is compressed (well short of 1.0) but can
    # legitimately exceed the old hand-set model's ~0.97 ceiling -- the
    # calibration table (models/backtest_report.json) shows the 90-100%
    # bucket is itself well-calibrated (predicted 0.95, observed 0.948).
    assert 0.5 < spain < 0.99
    assert abs(spain + south_africa - 1.0) < 1e-8


def test_round_of_32_uses_published_slots_without_same_group_rematches():
    repository = TournamentRepository()
    groups = {team.team: team.group for team in repository.teams}
    ranked = {
        group: [
            type("Row", (), {"team": team.team})()
            for team in repository.group_teams(group)
        ]
        for group in "ABCDEFGHIJKL"
    }
    best_thirds = [ranked[group][2] for group in "ABCDEFGH"]
    matches = build_round_of_32(ranked, best_thirds, groups)

    assert [match for match, _, _ in matches] == list(range(73, 89))
    assert all(groups[first] != groups[second] for _, first, second in matches)
    assert len({team for _, first, second in matches for team in (first, second)}) == 32


def test_all_495_third_place_combinations_have_a_legal_assignment():
    third_slots = {
        slot.match: slot.second_groups
        for slot in ROUND_OF_32_SLOTS
        if slot.second_kind == "third"
    }
    checked = 0
    for groups in combinations("ABCDEFGHIJKL", 8):
        assignment = assign_third_place_groups(groups)
        assert set(assignment.values()) == set(groups)
        assert all(group in third_slots[match] for match, group in assignment.items())
        checked += 1
    assert checked == 495


def test_annex_c_reference_mapping_matches_the_published_first_row():
    assert assign_third_place_groups("EFGHIJKL") == {
        74: "F",
        77: "G",
        79: "E",
        80: "K",
        81: "I",
        82: "H",
        85: "J",
        87: "L",
    }


def test_knockout_path_contains_every_match_after_round_of_32():
    matches = {
        match
        for round_matches in KNOCKOUT_PATH.values()
        for match, _, _ in round_matches
    }

    assert matches | {THIRD_PLACE_MATCH[0]} == set(range(89, 105))
    assert KNOCKOUT_PATH["round_of_16"][0] == (89, 73, 75)
    assert THIRD_PLACE_MATCH == (103, 101, 102)
    assert KNOCKOUT_PATH["champion"] == ((104, 101, 102),)
