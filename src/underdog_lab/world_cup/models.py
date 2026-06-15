from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, Field


class TournamentTeam(BaseModel):
    group: str
    position: int
    team: str
    rank: int
    elo: float
    host: bool = False

    @property
    def rating(self) -> float:
        return self.elo


class TournamentFixture(BaseModel):
    fixture_id: str
    group: str
    matchday: int
    date: date
    kickoff_utc: datetime | None = None
    home: str
    away: str
    home_goals: int | None = Field(default=None, ge=0)
    away_goals: int | None = Field(default=None, ge=0)

    @property
    def played(self) -> bool:
        return self.home_goals is not None and self.away_goals is not None


class Standing(BaseModel):
    team: str
    played: int = 0
    wins: int = 0
    draws: int = 0
    losses: int = 0
    goals_for: int = 0
    goals_against: int = 0
    points: int = 0

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against
