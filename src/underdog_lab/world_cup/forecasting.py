from __future__ import annotations

from underdog_lab.forecasting.calibration import apply_temperature
from underdog_lab.forecasting.dixon_coles import (
    DixonColesEloModel,
    top_scorelines_dc,
)
from underdog_lab.world_cup.models import TournamentFixture, TournamentTeam

# Fit by scripts/fit_elo_dixon_coles.py on 11,094 real matches (2015-01-03 to
# 2026-06-12, eloratings.net) via time-decayed MLE with a 180-day half-life
# -- see models/elo_fit_report.json. The 180-day half-life was selected by
# scripts/upgrade_evaluation.py over the previous 1095-day (3 year) setting:
# it beats the 1095-day fit on mean log loss across 2018-2025 selection
# folds AND on the held-out 2026 confirmation fold, both overall and on the
# neutral-venue subset (models/upgrade_evaluation.json). Walk-forward
# backtested in scripts/backtest_walk_forward.py
# (models/backtest_report.json): beats both the uniform baseline and the
# previous hand-set model on log loss, Brier, and RPS across 2018-2026.
# home_advantage_elo has no effect on World Cup group fixtures, which are
# always neutral_venue=True.
MODEL = DixonColesEloModel(
    intercept=0.15344112308888175,
    elo_scale=0.0020741972184725598,
    home_advantage_elo=65.62880408367505,
    rho=-0.09976156493949083,
)

# Post-hoc temperature scaling (forecasting/calibration.py) selected by
# scripts/recalibration_evaluation.py over the T=1 (no-op) baseline: it beats
# T=1 on mean log loss across 2018-2025 selection folds AND on the held-out
# 2026 confirmation fold, both overall and on the neutral-venue subset
# (models/recalibration_evaluation.json). T<1 sharpens MODEL's forecasts.
CALIBRATION_TEMPERATURE = 0.8857253661047012


def match_forecast(
    fixture: TournamentFixture,
    team_by_name: dict[str, TournamentTeam],
):
    home = team_by_name[fixture.home]
    away = team_by_name[fixture.away]
    forecast = MODEL.forecast(home.rating, away.rating, neutral_venue=True)
    return apply_temperature(forecast, CALIBRATION_TEMPERATURE)


def top_scorelines(forecast, limit: int = 3) -> list[tuple[str, float]]:
    return top_scorelines_dc(
        forecast.lambda_home,
        forecast.lambda_away,
        MODEL.rho,
        limit=limit,
    )
