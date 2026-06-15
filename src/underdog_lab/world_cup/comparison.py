"""Comparisons against publicly published third-party World Cup forecasts.

All numbers come from `data/world_cup_2026/external_forecasts.json`, a
one-time dated snapshot of independently published projections (an
analytics "supercomputer" model, a sports-data outlet's team projections,
and betting-market consensus). Nothing here is fetched live.
"""

from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

from underdog_lab.world_cup.flags import team_label

EXTERNAL_FORECASTS_PATH = Path("data/world_cup_2026/external_forecasts.json")


@lru_cache(maxsize=1)
def load_external_forecasts() -> dict:
    if not EXTERNAL_FORECASTS_PATH.exists():
        return {}
    return json.loads(EXTERNAL_FORECASTS_PATH.read_text(encoding="utf-8"))


def _normalize(*values: float) -> tuple[float, ...]:
    total = sum(values)
    if total <= 0:
        return values
    return tuple(value / total for value in values)


def match_comparison_html(fixture, forecast) -> str:
    """A small 'how does this compare?' table for one fixture, or '' if
    no third-party data is available for it."""
    data = load_external_forecasts().get("match_odds")
    if not data:
        return ""
    entry = data.get("fixtures", {}).get(fixture.fixture_id)
    if not entry:
        return ""

    our_home, our_draw, our_away = forecast.p_home, forecast.p_draw, forecast.p_away
    ext_home, ext_draw, ext_away = _normalize(
        entry["p_home"], entry["p_draw"], entry["p_away"]
    )

    rows = f"""
    <tr><td>Our model</td><td>{our_home:.0%}</td><td>{our_draw:.0%}</td><td>{our_away:.0%}</td>
    <td class="small">as of {html.escape(data.get('captured_at', ''))}</td></tr>
    <tr><td>{html.escape(data['label'])}</td><td>{ext_home:.0%}</td><td>{ext_draw:.0%}</td><td>{ext_away:.0%}</td>
    <td class="small">as of {html.escape(entry.get('captured_at', ''))}</td></tr>
    """
    return f"""
    <section class="lab-card">
      <div class="eyebrow">How does this compare?</div>
      <h3>{team_label(fixture.home)} vs {team_label(fixture.away)}</h3>
      <div class="table-scroll"><table>
        <thead><tr><th>Source</th><th>{team_label(fixture.home)}</th><th>Draw</th><th>{team_label(fixture.away)}</th><th></th></tr></thead>
        <tbody>{rows}</tbody>
      </table></div>
      <p class="small">{html.escape(data.get('note', ''))} Source:
      <a href="{html.escape(data['url'])}" target="_blank" rel="noopener">{html.escape(data['source'])}</a>.</p>
    </section>
    """


def tournament_comparison_html(probabilities: dict, repository) -> str:
    external = load_external_forecasts()
    title_data = external.get("tournament_title")
    group_data = external.get("group_stage")

    sections = ["""
    <section class="lab-card">
      <div class="eyebrow">Compare with other forecasters</div>
      <h2>How do our numbers stack up against other public predictions?</h2>
      <p class="context">These are independent, dated snapshots from other
      analysts and from betting markets. Not live odds, and not an
      endorsement: they're here so you can see where our model agrees with
      everyone else, and where it doesn't.</p>
    </section>
    """]

    if title_data:
        rows = []
        for team, ext_probability in sorted(
            title_data["title_probability"].items(),
            key=lambda item: item[1],
            reverse=True,
        ):
            our_probability = probabilities.get(team, {}).get("champion", 0.0)
            rows.append(
                f"<tr><td>{team_label(team)}</td>"
                f"<td>{our_probability:.1%}</td>"
                f"<td>{ext_probability:.1%}</td></tr>"
            )
        sections.append(f"""
        <section class="lab-card">
          <h3>Who's favourite to win it all?</h3>
          <p class="context">{html.escape(title_data.get('note', ''))}</p>
          <div class="table-scroll"><table>
            <thead><tr><th>Team</th><th>Our model</th><th>{html.escape(title_data['label'])}</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table></div>
          <p class="small">Snapshot captured {html.escape(title_data.get('captured_at', ''))}.
          Source: <a href="{html.escape(title_data['url'])}" target="_blank" rel="noopener">{html.escape(title_data['source'])}</a>.</p>
        </section>
        """)

    if group_data:
        rows = []
        teams_by_group = {team.team: team.group for team in repository.teams}
        for team, ext in sorted(
            group_data["teams"].items(),
            key=lambda item: teams_by_group.get(item[0], "Z") + item[0],
        ):
            ours = probabilities.get(team, {})
            rows.append(
                f"<tr><td>{team_label(team)}</td>"
                f"<td>{teams_by_group.get(team, '?')}</td>"
                f"<td>{ours.get('group_winner', 0.0):.1%}</td>"
                f"<td>{ext['group_win']:.1%}</td>"
                f"<td>{ours.get('advance', 0.0):.1%}</td>"
                f"<td>{ext['qualify']:.1%}</td></tr>"
            )
        sections.append(f"""
        <section class="lab-card">
          <h3>Group-stage chances</h3>
          <p class="context">{html.escape(group_data.get('note', ''))}</p>
          <div class="table-scroll"><table>
            <thead><tr><th>Team</th><th>Group</th>
            <th>Our group-win %</th><th>{html.escape(group_data['label'])} group-win %</th>
            <th>Our advance %</th><th>{html.escape(group_data['label'])} qualify %</th></tr></thead>
            <tbody>{''.join(rows)}</tbody>
          </table></div>
          <p class="small">Snapshot captured {html.escape(group_data.get('captured_at', ''))}.
          Source: <a href="{html.escape(group_data['url'])}" target="_blank" rel="noopener">{html.escape(group_data['source'])}</a>.</p>
        </section>
        """)

    return "".join(sections)
