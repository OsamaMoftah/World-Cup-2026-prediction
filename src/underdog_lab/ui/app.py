from __future__ import annotations

import html
import json
from functools import lru_cache
from pathlib import Path

import gradio as gr
from gradio.themes import Soft

from underdog_lab.data.repository import MatchRepository
from underdog_lab.domain import Forecast
from underdog_lab.release.health import application_health
from underdog_lab.scenarios.adjustments import RULES, apply_extraction
from underdog_lab.scenarios.factory import build_extractor
from underdog_lab.scenarios.schemas import ScenarioExtraction
from underdog_lab.service import analyze_scenario, baseline_forecast
from underdog_lab.telemetry.traces import append_trace
from underdog_lab.ui.components import (
    derived_away_html,
    factors_html,
    forecast_html,
    hero_html,
    match_html,
    reveal_html,
)
from underdog_lab.world_cup.comparison import (
    match_comparison_html,
    tournament_comparison_html,
)
from underdog_lab.world_cup.data import TournamentRepository
from underdog_lab.world_cup.flags import team_label
from underdog_lab.world_cup.forecasting import match_forecast
from underdog_lab.world_cup.predictions import scored_track_records
from underdog_lab.world_cup.provenance import forecast_provenance
from underdog_lab.world_cup.simulation import simulate_tournament
from underdog_lab.world_cup.ui import (
    all_fixtures_html,
    awards_html,
    fixture_as_match,
    fixture_label,
    group_html,
    overdue_results_note,
    tournament_probabilities_html,
    upcoming_html,
)


repository = MatchRepository()
world_cup_repository = TournamentRepository()
extractor = build_extractor()
labels = repository.labels()
world_cup_fixtures = {
    fixture_label(fixture): fixture
    for fixture in world_cup_repository.fixtures
    if not fixture.played
}
world_cup_labels = list(world_cup_fixtures)

if hasattr(extractor, "warmup"):
    extractor.warmup()


@lru_cache(maxsize=64)
def _analyze_cached(match_id: str, text: str) -> tuple[dict, dict, dict, str, str | None]:
    match = repository.get(match_id)
    extraction, result, forecast = analyze_scenario(match, text, extractor)
    return (
        extraction.model_dump(mode="json"),
        result.model_dump(mode="json"),
        forecast.model_dump(mode="json"),
        getattr(extractor, "last_backend", extractor.name),
        getattr(extractor, "last_error", None),
    )


def select_match(label: str):
    match = repository.by_label(label)
    baseline = baseline_forecast(match)
    return (
        match.match_id,
        baseline.model_dump(mode="json"),
        baseline.model_dump(mode="json"),
        match_html(match),
        forecast_html(baseline, match, "Baseline forecast"),
        factors_html(ScenarioExtraction(), apply_extraction(match, ScenarioExtraction())),
        forecast_html(baseline, match, "Scenario forecast"),
        "",
        derived_away_html(45, 25),
    )


def run_scenario(label: str, text: str):
    match = repository.by_label(label)
    baseline = baseline_forecast(match)
    try:
        (
            extraction_data,
            result_data,
            forecast_data,
            actual_backend,
            backend_error,
        ) = _analyze_cached(
            match.match_id, text.strip()
        )
        extraction = ScenarioExtraction.model_validate(extraction_data)
        from underdog_lab.scenarios.schemas import AdjustmentResult

        result = AdjustmentResult.model_validate(result_data)
        adjusted = Forecast.model_validate(forecast_data)
    except Exception as error:
        actual_backend = "scenario pipeline error"
        backend_error = f"{type(error).__name__}: {error}"
        fallback = ScenarioExtraction(
            unsupported_claims=[f"Extractor unavailable: {type(error).__name__}"]
        )
        result = apply_extraction(match, fallback)
        extraction = fallback
        adjusted = baseline

    append_trace(
        {
            "event": "scenario_analyzed",
            "match_id": match.match_id,
            "extractor": extractor.name,
            "actual_backend": actual_backend,
            "backend_error": backend_error,
            "scenario": text,
            "extraction": extraction.model_dump(mode="json"),
            "forecast": adjusted.model_dump(mode="json"),
        }
    )
    return (
        adjusted.model_dump(mode="json"),
        factors_html(
            extraction,
            result,
            backend=actual_backend,
            backend_error=backend_error,
        ),
        forecast_html(adjusted, match, "Scenario forecast", comparison=baseline),
        "",
    )


def select_world_cup_group(group: str) -> str:
    return group_html(world_cup_repository, group)


def update_world_cup_upcoming(mode: str) -> str:
    return upcoming_html(world_cup_repository, mode=mode)


def select_world_cup_fixture(label: str):
    fixture = world_cup_fixtures[label]
    match = fixture_as_match(fixture, world_cup_repository)
    baseline = match_forecast(fixture, world_cup_repository.team_by_name)
    return (
        forecast_html(baseline, match, "2026 baseline forecast"),
        factors_html(
            ScenarioExtraction(),
            apply_extraction(match, ScenarioExtraction()),
        ),
        forecast_html(baseline, match, "Scenario forecast"),
        match_comparison_html(fixture, baseline),
    )


def run_world_cup_scenario(label: str, text: str):
    fixture = world_cup_fixtures[label]
    match = fixture_as_match(fixture, world_cup_repository)
    baseline = match_forecast(fixture, world_cup_repository.team_by_name)
    try:
        extraction, result, adjusted = analyze_scenario(
            match,
            text.strip(),
            extractor,
        )
        actual_backend = getattr(extractor, "last_backend", extractor.name)
        backend_error = getattr(extractor, "last_error", None)
    except Exception as error:
        actual_backend = "scenario pipeline error"
        backend_error = f"{type(error).__name__}: {error}"
        extraction = ScenarioExtraction(
            unsupported_claims=[f"Extractor unavailable: {type(error).__name__}"]
        )
        result = apply_extraction(match, extraction)
        adjusted = baseline
    append_trace(
        {
            "event": "world_cup_scenario_analyzed",
            "fixture_id": fixture.fixture_id,
            "actual_backend": actual_backend,
            "backend_error": backend_error,
            "scenario": text,
            "forecast": adjusted.model_dump(mode="json"),
        }
    )
    return (
        factors_html(
            extraction,
            result,
            backend=actual_backend,
            backend_error=backend_error,
        ),
        forecast_html(
            adjusted,
            match,
            "Scenario forecast (experimental)",
            comparison=baseline,
        ),
    )


def update_user_forecast(home: float, draw: float) -> str:
    return derived_away_html(home, draw)


def reveal(
    label: str,
    baseline_state: dict,
    adjusted_state: dict,
    home: float,
    draw: float,
) -> str:
    match = repository.by_label(label)
    baseline = Forecast.model_validate(baseline_state)
    adjusted = Forecast.model_validate(adjusted_state)
    output = reveal_html(match, baseline, adjusted, home, draw)
    append_trace(
        {
            "event": "forecast_revealed",
            "match_id": match.match_id,
            "user_home": home,
            "user_draw": draw,
            "user_away": 100.0 - home - draw,
        }
    )
    return output


def track_record_html(repository) -> str:
    records = scored_track_records(repository.fixtures, repository.team_by_name)

    def section(title: str, description: str, summary: dict) -> str:
        rows = "".join(
            "<tr>"
            f"<td>{row['fixture_id']}</td><td>{team_label(row['home'])}</td>"
            f"<td>{row['score']}</td><td>{team_label(row['away'])}</td>"
            f"<td>{row['p_home']:.1%}</td><td>{row['p_draw']:.1%}</td>"
            f"<td>{row['p_away']:.1%}</td><td>{row['log_loss']:.3f}</td>"
            f"<td>{row['brier']:.3f}</td><td>{row['rps']:.3f}</td></tr>"
            for row in summary["rows"]
        )
        if not rows:
            rows = "<tr><td colspan='10'>No matches in this group yet.</td></tr>"
        metrics = (
            (
                f"{summary['accuracy']:.1%}",
                f"{summary['mean_log_loss']:.3f}",
                f"{summary['mean_brier']:.3f}",
                f"{summary['mean_rps']:.3f}",
                f"{summary['log_loss_skill_vs_uniform']:+.1%}",
            )
            if summary["n"]
            else ("-", "-", "-", "-", "-")
        )
        sample_note = (
            "Fewer than 30 matches so far: a useful early signal, but too "
            "small to call a stable accuracy rate yet."
            if summary["n"] < 30
            else "Large enough for a descriptive comparison, while still "
            "subject to tournament-specific sample uncertainty."
        )
        skill_note = (
            "Positive skill means lower (better) log loss than equal 1/3 odds; "
            "negative skill means worse."
        )
        return f"""
        <section class="lab-card">
          <div class="eyebrow">Track record</div>
          <h2>{title}</h2>
          <p class="context">{description}</p>
          <div class="score-grid">
            <div class="score-box"><span>Matches</span><strong>{summary['n']}</strong></div>
            <div class="score-box"><span>Top-pick accuracy</span><strong>{metrics[0]}</strong></div>
            <div class="score-box"><span>Mean log loss</span><strong>{metrics[1]}</strong></div>
            <div class="score-box"><span>Mean Brier</span><strong>{metrics[2]}</strong></div>
            <div class="score-box"><span>Mean RPS</span><strong>{metrics[3]}</strong></div>
            <div class="score-box"><span>Log-loss skill vs equal odds</span><strong>{metrics[4]}</strong></div>
            <div class="score-box"><span>"Just guess equally" baseline</span><strong>{summary['uniform_log_loss']:.3f}</strong></div>
          </div>
          <p class="small">{skill_note} {sample_note}</p>
          <div class="table-scroll"><table>
            <thead><tr><th>ID</th><th>Home</th><th>Score</th><th>Away</th>
            <th>1</th><th>X</th><th>2</th><th>LogLoss</th><th>Brier</th><th>RPS</th></tr></thead>
            <tbody>{rows}</tbody>
          </table></div>
        </section>
        """

    coverage = records["coverage"]
    excluded = ", ".join(coverage["excluded_fixture_ids"])
    intro = f"""
    <section class="lab-card">
      <div class="eyebrow">Track record</div>
      <h2>How accurate have we been so far?</h2>
      <p class="context">Every row below is a prediction we made and froze
      <em>before</em> kickoff, compared against what actually happened.
      Proper scoring rules are the primary measure; top-pick accuracy is shown
      as a familiar secondary measure. Lower log loss, Brier, and RPS are
      better. See the Methodology tab for the artifact audit.</p>
      <div class="score-grid">
        <div class="score-box"><span>Completed group matches</span><strong>{coverage['completed']}</strong></div>
        <div class="score-box"><span>Verified forecasts scored</span><strong>{coverage['scored']}</strong></div>
        <div class="score-box"><span>Prospective coverage</span><strong>{coverage['rate']:.1%}</strong></div>
        <div class="score-box"><span>Excluded from scoring</span><strong>{coverage['excluded']}</strong></div>
      </div>
      <p class="small">Excluded because no valid pre-kickoff artifact exists:
      {excluded}. Historical forecast files remain immutable.</p>
    </section>
    """

    prospective_sections = "".join(
        section(
            f"Predictions made {horizon.replace('_', ' ')}",
            "Locked in before kickoff and compared to the final score.",
            summary,
        )
        for horizon, summary in records["prospective_by_horizon"].items()
    )

    aggregate = section(
        "All verified pre-kickoff predictions",
        "The honest headline score across all forecast horizons. Each match "
        "is counted once using its latest eligible artifact before kickoff.",
        records["prospective"],
    )

    return intro + aggregate + prospective_sections + section(
        "If we replayed every match with today's model",
        "This re-runs the current model over every match played so far. "
        "It's a useful diagnostic, but because it uses today's corrected "
        "ratings, treat it as 'how good is the current model', not as a "
        "pre-match prediction.",
        records["retrospective"],
    )


def model_summary_html() -> str:
    backtest = json.loads(Path("models/backtest_report.json").read_text(encoding="utf-8"))
    fitted = backtest["overall_mean_scores"]["fitted"]
    previous = backtest["overall_mean_scores"]["current"]
    comparison = (
        "a little sharper than the previous version"
        if fitted["log_loss"] < previous["log_loss"]
        else "about the same as the previous version"
    )
    return f"""
    <section class="lab-card" style="border-color:rgba(178,34,52,.25)">
      <div class="eyebrow">Why trust these numbers?</div>
      <h2>Checked against {backtest['total_test_matches']:,} real matches before going live</h2>
      <p class="context">The baseline forecast comes from Dixon-Coles, a
      well-known statistical model for football scorelines, fitted on each
      team's Elo rating. Before shipping it, we tested it on
      {backtest['total_test_matches']:,} real matches from 2018-2026, always
      predicting games it hadn't seen the result of yet. This version came
      out {comparison}.</p>
      <p class="small">Want the exact numbers, what we tried and didn't ship,
      and how we keep our own track record honest? Open the
      <strong>Methodology</strong> tab.</p>
    </section>
    """


def methodology_html() -> str:
    backtest = json.loads(Path("models/backtest_report.json").read_text(encoding="utf-8"))
    ship = json.loads(Path("results/ship_decision.json").read_text(encoding="utf-8"))
    fitted = backtest["overall_mean_scores"]["fitted"]
    previous = backtest["overall_mean_scores"]["current"]
    neutral = backtest["neutral_mean_scores"]

    live_path = Path("predictions/live/2026-06-13T190000Z-WC26-008")
    live = json.loads((live_path / "forecast.json").read_text(encoding="utf-8"))
    manifest = json.loads((live_path / "manifest.json").read_text(encoding="utf-8"))
    live_fixture = live["fixtures"][0]

    health = application_health()
    provenance = forecast_provenance()

    evaluation_path = repository.path.parents[1] / "scenarios" / "evaluation.json"
    metrics = (
        json.loads(evaluation_path.read_text(encoding="utf-8"))
        if evaluation_path.exists()
        else {}
    )
    tuned = ship.get("tuned_model", {})

    intro = """
    <section class="lab-card">
      <div class="eyebrow">Methodology &amp; receipts</div>
      <h2>How this works, and how we keep ourselves honest</h2>
      <p class="context">This tab is for the curious: the model behind the
      numbers, the benchmarks, the experiments we tried and didn't ship, and
      how we audit our own predictions so results can't be quietly rewritten
      after the fact.</p>
    </section>
    """

    numbers = f"""
    <section class="lab-card">
      <h3>The numbers behind "tested against real matches"</h3>
      <div class="score-grid">
        <div class="score-box"><span>Matches tested</span><strong>{backtest['total_test_matches']:,}</strong><span class="small">2018-2026, walk-forward</span></div>
        <div class="score-box"><span>Log loss now</span><strong>{fitted['log_loss']:.3f}</strong><span class="small">was {previous['log_loss']:.3f}</span></div>
        <div class="score-box"><span>Neutral-venue log loss</span><strong>{neutral['fitted']['log_loss']:.3f}</strong><span class="small">was {neutral['current']['log_loss']:.3f}</span></div>
      </div>
      <p class="small">Log loss measures how well the predicted probabilities
      matched what actually happened: lower means better-calibrated
      confidence. "Walk-forward" means every test prediction was made without
      letting the model see that match's result first.</p>
    </section>
    """

    live_proof = f"""
    <section class="lab-card">
      <h3>A prediction we can't take back</h3>
      <p class="context">To prove forecasts aren't adjusted after the fact,
      every prediction gets frozen and fingerprinted before kickoff. Take
      <strong>{html.escape(live_fixture['home'])} vs
      {html.escape(live_fixture['away'])}</strong>: we froze
      {live_fixture['p_home']:.0%} / {live_fixture['p_draw']:.0%} /
      {live_fixture['p_away']:.0%} at
      {live['generated_at'][:16].replace('T', ' ')} UTC, ahead of its
      {live_fixture['kickoff_utc'][11:16]} UTC kickoff. The fingerprint
      (<code>{manifest['sha256'][:16]}…</code>) is sitting in the repo, so
      anyone can check it wasn't touched afterwards.</p>
    </section>
    """

    ai_card_class = "lab-card warn" if ship.get("ship_decision") == "NO-SHIP" else "lab-card"
    ai_experiment = f"""
    <section class="{ai_card_class}">
      <h3>An AI experiment that didn't make the cut</h3>
      <p class="context">The "scenario reader" (the part that turns "star
      striker is out" into a number) is a small 360M-parameter language model
      running locally; nothing you type leaves this app. We tried fine-tuning
      a custom version on football-specific examples. It got better at
      recognising the right category of news, but its confidence scores came
      out unreliable, so our own safety check failed it
      (<strong>{html.escape(ship.get('ship_decision', 'PENDING'))}</strong>:
      {html.escape(ship.get('reason', ''))}). The app falls back to the
      original model plus a rule-based backup instead. Either way, the AI
      only ever reads the news; the statistics still decide the odds.</p>
      <div class="score-grid" style="margin-top:1rem">
        <div class="score-box"><span>Base model</span><strong>{metrics.get('factor_micro_f1', 0):.3f}</strong><span class="small">factor micro-F1</span></div>
        <div class="score-box{' warn' if tuned else ''}"><span>Fine-tuned attempt</span><strong>{tuned.get('factor_micro_f1', 0):.3f}</strong><span class="small">factor micro-F1</span></div>
        <div class="score-box"><span>Runtime</span><strong>{html.escape(extractor.name)}</strong><span class="small">swappable backend</span></div>
      </div>
    </section>
    """

    rejected = """
    <section class="lab-card">
      <h3>Other things we tried and didn't keep</h3>
      <ul class="context">
        <li><strong>A "host nation" bonus.</strong> Testing whether host
        teams deserve an Elo boost was inconclusive, so we removed the
        heuristic rather than guess.</li>
        <li><strong>A tournament-opener draw adjustment.</strong> Failed its
        historical check, so it's not applied.</li>
        <li><strong>Betting-market odds.</strong> Not used for our own
        forecasts yet. The Compare tab shows them for context, but they'd
        need to pass the same testing as everything else here before feeding
        into our model.</li>
      </ul>
    </section>
    """

    factor_rows = "".join(
        f"<tr><td>{html.escape(factor.value.replace('_', ' ').title())}</td>"
        f"<td>{html.escape(rule.rationale)}</td></tr>"
        for factor, rule in RULES.items()
    )
    factors = f"""
    <section class="lab-card">
      <h3>What kinds of news can move a forecast?</h3>
      <p class="context">When you describe a scenario, the reader checks it
      against this list of situations. Each one nudges expected goals by a
      small, fixed amount, so the AI never gets to invent a probability on
      its own.</p>
      <table><thead><tr><th>Situation</th><th>Why it matters</th></tr></thead>
      <tbody>{factor_rows}</tbody></table>
    </section>
    """

    audit = f"""
    <section class="lab-card">
      <h3>How we audit our own track record</h3>
      <p class="context">Every prediction is saved before its match is
      played. The Track Record tab only counts predictions frozen,
      fingerprinted, and timestamped <em>before</em> kickoff: {health['eligible_prospective_forecasts']}
      of them so far. Older test data doesn't count toward the headline
      numbers, so we can't quietly mix in easier after-the-fact comparisons.
      Current model version: <code>{provenance['model_version']}</code>.</p>
    </section>
    """

    return (
        intro + numbers + live_proof + ai_experiment + rejected + factors + audit
    )


def how_it_works_summary_markdown() -> str:
    return """
Every team carries an Elo rating, the same idea as a chess rating. That
number feeds into Dixon-Coles, a well-worn statistical model for football
scorelines, and we've checked the result against thousands of past matches so
that a "70% favourite" actually wins about 70% of the time.

When you describe a scenario, a small model running on this machine checks it
against a short list of situations we already understand, like *key player
out*, and nudges the expected goals by a fixed amount. It doesn't invent a
probability on its own; it just spots which situation applies, and the
statistics handle the rest.

Want the full walkthrough, the benchmark numbers, and how this compares to
other public predictions? That's all in the **Methodology** tab.
"""


def how_it_works_markdown() -> str:
    return """
## How this actually works

Every team carries an Elo rating, the same kind of number chess players use,
updated after each result. A higher rating means the model expects that team
to score more and concede less.

Those ratings feed into Dixon-Coles, a statistical model analysts have used
for football scorelines for decades. Rather than one guess, it produces a
full grid of scoreline probabilities: 0-0, 1-0, 2-1, and so on. Recent results
count for more than old ones, since a result from last month says more about
a team's current form than one from three years ago. We tried several "how
much more" settings against real results and kept whichever predicted best.

We then checked the model's confidence levels against thousands of matches
and applied a small correction, so a "70% favourite" really does win about
70% of the time rather than 85% or 55%.

### Reading the news

When you type a scenario like "star striker is out", a small language model
runs locally and checks it against a short list of situations we already
understand: a key attacker missing, a fatigue disadvantage, and so on. It
doesn't invent a probability. It just recognises which situation applies,
and each one nudges the expected goals by a small, fixed amount before
Dixon-Coles recalculates the odds. The AI reads; the statistics decide.

### Keeping score

Every prediction is frozen and timestamped before kickoff, so the Track
Record tab shows what the model actually said in advance, not a version
improved with hindsight.

---

These are probabilities, not certainties. Even a 60% favourite loses 4 times
out of 10. For the benchmark numbers, the experiments that didn't make the
cut, and how we audit ourselves, see the **Methodology** tab.
"""


initial_match = repository.by_label(labels[0])
initial_baseline = baseline_forecast(initial_match)
if world_cup_labels:
    initial_world_cup_label = world_cup_labels[0]
    initial_world_cup_fixture = world_cup_fixtures[initial_world_cup_label]
    initial_world_cup_match = fixture_as_match(
        initial_world_cup_fixture,
        world_cup_repository,
    )
    initial_world_cup_forecast = match_forecast(
        initial_world_cup_fixture,
        world_cup_repository.team_by_name,
    )
world_cup_probabilities = simulate_tournament(world_cup_repository)

LIGHT_THEME = Soft(
    primary_hue="blue",
    secondary_hue="red",
    neutral_hue="slate",
)

with gr.Blocks(title="World Cup 2026 Forecaster") as demo:
    match_id_state = gr.State(initial_match.match_id)
    baseline_state = gr.State(initial_baseline.model_dump(mode="json"))
    adjusted_state = gr.State(initial_baseline.model_dump(mode="json"))

    cutoff_display = world_cup_repository.snapshot.get("information_cutoff", "")
    gr.HTML(
        hero_html(
            extractor.name,
            cutoff=cutoff_display,
            overdue_note=overdue_results_note(world_cup_repository),
        )
    )

    with gr.Accordion("How this works", open=False):
        gr.Markdown(how_it_works_summary_markdown())

    with gr.Tabs():
        with gr.Tab("World Cup 2026"):
            with gr.Row():
                world_cup_mode = gr.Radio(
                    choices=[
                        ("Probability view", "probability"),
                        ("Compact view", "compact"),
                    ],
                    value="probability",
                    label="Forecast view",
                )
            upcoming_card = gr.HTML(
                upcoming_html(world_cup_repository, mode="probability")
            )

            world_cup_mode.change(
                update_world_cup_upcoming,
                inputs=world_cup_mode,
                outputs=upcoming_card,
                show_progress="hidden",
            )

            gr.HTML(model_summary_html())

            if world_cup_labels:
                gr.Markdown("## Apply late-breaking evidence to an upcoming match")
                gr.Markdown(
                    "Type in a piece of news and watch the forecast shift. This "
                    "is experimental — a small local model reads your text "
                    "and proposes adjustments, so check the extracted factors "
                    "below before trusting the result."
                )
                live_fixture_selector = gr.Dropdown(
                    choices=world_cup_labels,
                    value=initial_world_cup_label,
                    label="Upcoming fixture",
                )
                live_baseline_card = gr.HTML(
                    forecast_html(
                        initial_world_cup_forecast,
                        initial_world_cup_match,
                        "2026 baseline forecast",
                    )
                )
                live_scenario = gr.Textbox(
                    label="Pre-match report",
                    placeholder=(
                        f"Example: {initial_world_cup_fixture.home}'s first-choice "
                        "striker is confirmed out."
                    ),
                    lines=3,
                )
                live_analyze_button = gr.Button(
                    "Adjust 2026 forecast",
                    variant="primary",
                    elem_classes="primary-button",
                )
                live_factors_card = gr.HTML(
                    factors_html(
                        ScenarioExtraction(),
                        apply_extraction(
                            initial_world_cup_match,
                            ScenarioExtraction(),
                        ),
                    )
                )
                live_adjusted_card = gr.HTML(
                    forecast_html(
                        initial_world_cup_forecast,
                        initial_world_cup_match,
                        "Scenario forecast (experimental)",
                    )
                )
                live_comparison_card = gr.HTML(
                    match_comparison_html(
                        initial_world_cup_fixture, initial_world_cup_forecast
                    )
                )
                live_fixture_selector.change(
                    select_world_cup_fixture,
                    inputs=live_fixture_selector,
                    outputs=[
                        live_baseline_card,
                        live_factors_card,
                        live_adjusted_card,
                        live_comparison_card,
                    ],
                )
                live_analyze_button.click(
                    run_world_cup_scenario,
                    inputs=[live_fixture_selector, live_scenario],
                    outputs=[live_factors_card, live_adjusted_card],
                )
                live_scenario.submit(
                    run_world_cup_scenario,
                    inputs=[live_fixture_selector, live_scenario],
                    outputs=[live_factors_card, live_adjusted_card],
                )
            else:
                gr.HTML(
                    """
                    <section class="lab-card">
                      <div class="eyebrow">Scenario lab</div>
                      <h2>The group-stage scenario window is closed</h2>
                      <p class="context">All 72 group fixtures have been
                      played. The original pre-kickoff forecasts remain frozen
                      and are graded in the Track Record tab; this panel is
                      disabled so completed matches cannot be presented as
                      live prediction opportunities.</p>
                    </section>
                    """
                )

            with gr.Accordion("Group tables & standings", open=False):
                with gr.Row():
                    group_selector = gr.Dropdown(
                        choices=list("ABCDEFGHIJKL"),
                        value="A",
                        label="Group",
                    )
                group_card = gr.HTML(group_html(world_cup_repository, "A"))
                group_selector.change(
                    select_world_cup_group,
                    inputs=group_selector,
                    outputs=group_card,
                    show_progress="hidden",
                )

            with gr.Accordion("Complete 72-match group table", open=False):
                gr.HTML(all_fixtures_html(world_cup_repository))

            gr.HTML(
                tournament_probabilities_html(
                    world_cup_probabilities,
                    world_cup_repository,
                )
            )

        with gr.Tab("Player Awards"):
            gr.HTML(awards_html(world_cup_repository, world_cup_probabilities))

        with gr.Tab("Challenge"):
            match_selector = gr.Dropdown(
                choices=labels,
                value=labels[0],
                label="Hidden historical match",
            )
            match_card = gr.HTML(match_html(initial_match))
            baseline_card = gr.HTML(
                forecast_html(initial_baseline, initial_match, "Baseline forecast")
            )

            scenario = gr.Textbox(
                label="What changes before kickoff?",
                placeholder=(
                    "Example: Argentina's first-choice striker is confirmed out."
                ),
                lines=3,
            )
            with gr.Row():
                analyze_button = gr.Button(
                    "Translate scenario", variant="primary", elem_classes="primary-button"
                )
                clear_button = gr.ClearButton(
                    [scenario], value="Clear", elem_classes="secondary-button"
                )

            factors_card = gr.HTML(
                factors_html(
                    ScenarioExtraction(),
                    apply_extraction(initial_match, ScenarioExtraction()),
                )
            )
            adjusted_card = gr.HTML(
                forecast_html(
                    initial_baseline, initial_match, "Scenario forecast"
                )
            )

            gr.Markdown("### Commit your probabilities")
            with gr.Row():
                user_home = gr.Slider(
                    0, 100, value=45, step=1, label="Home win %"
                )
                user_draw = gr.Slider(
                    0, 100, value=25, step=1, label="Draw %"
                )
                user_away = gr.HTML(derived_away_html(45, 25))
            reveal_button = gr.Button(
                "Lock forecast and reveal result",
                variant="primary",
                elem_classes="primary-button",
            )
            reveal_card = gr.HTML()

            match_selector.change(
                select_match,
                inputs=match_selector,
                outputs=[
                    match_id_state,
                    baseline_state,
                    adjusted_state,
                    match_card,
                    baseline_card,
                    factors_card,
                    adjusted_card,
                    reveal_card,
                    user_away,
                ],
            )
            analyze_button.click(
                run_scenario,
                inputs=[match_selector, scenario],
                outputs=[adjusted_state, factors_card, adjusted_card, reveal_card],
            )
            scenario.submit(
                run_scenario,
                inputs=[match_selector, scenario],
                outputs=[adjusted_state, factors_card, adjusted_card, reveal_card],
            )
            user_home.change(
                update_user_forecast,
                inputs=[user_home, user_draw],
                outputs=user_away,
            )
            user_draw.change(
                update_user_forecast,
                inputs=[user_home, user_draw],
                outputs=user_away,
            )
            reveal_button.click(
                reveal,
                inputs=[
                    match_selector,
                    baseline_state,
                    adjusted_state,
                    user_home,
                    user_draw,
                ],
                outputs=reveal_card,
            )

        with gr.Tab("Track Record"):
            gr.HTML(track_record_html(world_cup_repository))

        with gr.Tab("Compare with other forecasters"):
            gr.HTML(
                tournament_comparison_html(
                    world_cup_probabilities, world_cup_repository
                )
            )

        with gr.Tab("Methodology"):
            gr.Markdown(how_it_works_markdown())
            gr.HTML(methodology_html())

demo.queue(default_concurrency_limit=2)
