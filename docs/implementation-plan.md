# Underdog Lab Implementation Plan

_Date: June 12, 2026_

## Objective

Ship a polished Gradio Space by June 15, 2026 that demonstrates a small local language model converting football narratives into validated semantic factors, while a deterministic statistical engine owns all numerical probabilities.

Success means:

- the application runs end to end in a clean Hugging Face Space;
- the runtime model is at most 4B parameters;
- no cloud inference API is required;
- scenario outputs are grammar-constrained and validated;
- historical challenge mode is playable;
- base and fine-tuned extraction quality are measured on a frozen test set;
- the model, dataset or traces, field notes, demo, and social post are published before submission.

## Non-Goals Before Submission

- Proving superiority over bookmaker markets
- Live-data ingestion pipelines
- Dixon-Coles or large ML ensembles
- World Cup tournament simulation
- Coding-agent benchmark
- Betting recommendations
- Hyperparameter sweeps

## User Experience

### Primary Flow

1. User selects a hidden historical match.
2. App shows teams, venue, competition context, and baseline probabilities without revealing the result.
3. User writes a hypothetical or pre-match scenario.
4. Small model extracts typed semantic factors.
5. Validator rejects unsupported output and resolves team references.
6. Rule engine maps factors to bounded model adjustments.
7. Probability bars animate from baseline to adjusted forecast.
8. User submits home/draw/away probabilities.
9. App reveals the historical result.
10. App compares the baseline, adjusted model, and user with log loss and Brier score.

### Supporting Views

- **Scenario Stress Test:** vary one factor's severity and visualize monotonic probability movement.
- **Tiny Model Lab:** base-versus-tuned metrics, latency, example failures, model size, and training details.
- **How It Works:** concise explanation of semantic extraction, deterministic rules, and Poisson forecasting.

## System Architecture

```text
Gradio application
  -> historical match repository
  -> baseline forecast service
  -> scenario extractor interface
       -> llama.cpp base or fine-tuned GGUF
       -> grammar-constrained JSON
  -> Pydantic validation
  -> semantic factor normalizer
  -> deterministic adjustment rules
  -> Poisson forecast service
  -> scoring service
  -> visual components
  -> append-only local trace logger
```

The extractor must be swappable. The rest of the application must work with:

- a deterministic mock extractor for tests;
- the base SmolLM3-3B model;
- the fine-tuned SmolLM3-3B model.

## Repository Structure

```text
app.py
pyproject.toml
requirements.txt
README.md
src/underdog_lab/
  config.py
  domain.py
  data/
    repository.py
    schemas.py
  forecasting/
    poisson.py
    adjustments.py
    scoring.py
  scenarios/
    taxonomy.py
    schemas.py
    extractor.py
    llama_cpp_extractor.py
    mock_extractor.py
    grammar.gbnf
    prompts.py
  ui/
    app.py
    components.py
    charts.py
    theme.py
  telemetry/
    traces.py
scripts/
  prepare_matches.py
  generate_synthetic_data.py
  evaluate_extractor.py
  export_gguf.py
  smoke_test_space.py
training/
  modal_train.py
  configs/
    qlora.yaml
data/
  raw/
  processed/
    matches.parquet
    team_strengths.parquet
  scenarios/
    train.jsonl
    validation.jsonl
    test.jsonl
  traces/
models/
  README.md
tests/
  unit/
  property/
  integration/
  fixtures/
docs/
```

## Domain Contracts

### Match Record

```python
class MatchRecord(BaseModel):
    match_id: str
    kickoff_date: date
    competition: str
    home_team: str
    away_team: str
    neutral_venue: bool
    home_goals: int
    away_goals: int
    baseline_home_xg: float
    baseline_away_xg: float
    context: str
    reveal_notes: str | None = None
```

`home_goals` and `away_goals` must remain hidden from the UI until the user commits a forecast.

### Factor Taxonomy

Freeze the taxonomy before generating data:

```text
key_attacker_unavailable
key_defender_unavailable
goalkeeper_unavailable
multiple_starters_unavailable
squad_rotation
fatigue_disadvantage
rest_advantage
travel_disadvantage
altitude_disadvantage
heat_disadvantage
home_advantage
neutral_venue
defensive_game_state
must_win_incentive
```

Classification-only outputs:

```text
unsupported_claim
ambiguous_claim
irrelevant_text
```

### Extraction Schema

```python
class ExtractedFactor(BaseModel):
    factor_type: FactorType
    team: Literal["home", "away", "both", "unknown"]
    severity: float = Field(ge=0.0, le=1.0)
    certainty: float = Field(ge=0.0, le=1.0)
    evidence: str

class ScenarioExtraction(BaseModel):
    factors: list[ExtractedFactor] = Field(max_length=6)
    unsupported_claims: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
```

The model never emits expected-goal deltas or probabilities.

## Deterministic Adjustment Rules

Store the mapping in versioned Python data or YAML. Example starting ranges:

| Factor | Target | Maximum effect at severity 1.0 |
|---|---|---:|
| key_attacker_unavailable | affected attack | -12% |
| key_defender_unavailable | opponent attack | +8% |
| goalkeeper_unavailable | opponent attack | +10% |
| multiple_starters_unavailable | affected attack/defence | -8% / opponent +6% |
| squad_rotation | affected attack/defence | -6% / opponent +4% |
| fatigue_disadvantage | affected attack/defence | -5% / opponent +3% |
| rest_advantage | affected attack/defence | +4% / opponent -2% |
| travel_disadvantage | affected attack | -4% |
| altitude_disadvantage | affected attack/defence | -5% / opponent +3% |
| heat_disadvantage | affected attack | -3% |
| home_advantage | home attack | +6% |
| neutral_venue | home attack | -6% |
| defensive_game_state | both attacks | -6% |
| must_win_incentive | affected attack/defence | +5% / opponent +2% |

These values are product assumptions, not learned truths. Label them clearly and version them as `ruleset_v1`. Clamp final expected goals to a safe range such as `[0.15, 4.0]`.

## Forecasting Engine

### Baseline

Use precomputed expected goals per match. For a score grid from 0 to 8 goals:

```text
P(home=i, away=j) = Poisson(i; lambda_home) * Poisson(j; lambda_away)
```

Sum score cells into home-win, draw, and away-win probabilities. Normalize after truncation.

### Scenario Adjustment

1. Deduplicate equivalent factors.
2. Ignore `unknown` team assignments unless deterministically resolvable.
3. Multiply effects by `severity * certainty`.
4. Apply bounded multiplicative adjustments.
5. Clamp expected goals.
6. Recompute the score matrix and 1X2 probabilities.

### Scoring

Implement:

- multiclass log loss with probability clipping;
- multiclass Brier score;
- optional simple points for game presentation only.

Scientific tables use log loss and Brier score, never game points alone.

## Data Plan

### Historical Challenge Set

Prepare 20–30 matches, prioritizing variety rather than only famous upsets:

- favorites winning comfortably;
- draws;
- narrow favorites losing;
- neutral-venue tournament matches;
- high-scoring and low-scoring matches.

Do not expose result-bearing language in `context`. Famous showcase matches must be excluded from extraction training examples and the frozen extractor test set.

### Extraction Dataset

Target:

- 600–800 synthetic training examples;
- 50 validation examples;
- 80–100 frozen test examples.

Balance factor categories and include:

- single and multiple factors;
- pronouns and team-name references;
- negation;
- contradictions;
- irrelevant supporter commentary;
- unsupported facts;
- prompt-injection attempts;
- paraphrase groups;
- severity ladders.

Manually review every validation and test item. Store provenance and split before training.

Example record:

```json
{
  "id": "scenario-0042",
  "home_team": "Argentina",
  "away_team": "Saudi Arabia",
  "text": "Argentina's first-choice striker is confirmed out.",
  "expected": {
    "factors": [
      {
        "factor_type": "key_attacker_unavailable",
        "team": "home",
        "severity": 1.0,
        "certainty": 1.0
      }
    ],
    "unsupported_claims": [],
    "ambiguities": []
  }
}
```

## Constrained Inference

Use `llama.cpp` for both base and tuned models. Enforce the JSON structure with GBNF grammar.

Runtime settings:

- temperature: `0` or near zero;
- short maximum output;
- fixed system prompt;
- one retry only for semantic validation failures;
- deterministic empty extraction fallback;
- cache common demo scenarios.

Grammar guarantees syntax, not semantic correctness. Pydantic and domain validation remain mandatory.

## Fine-Tuning Plan

### Base Model

Start with `HuggingFaceTB/SmolLM3-3B` or its supported GGUF conversion.

### Method

Run one QLoRA supervised fine-tune on Modal:

- rank: 16;
- alpha: 32;
- dropout: 0.05;
- learning rate: approximately `2e-4`;
- 2–3 epochs;
- sequence length sized to the compact extraction task;
- early stopping or checkpoint selection using validation semantic metrics.

Exact settings may change for compatibility, but do not run a broad sweep.

### Artifacts

Publish:

- LoRA adapter;
- merged model if licensing and storage allow;
- GGUF runtime model;
- dataset or anonymized trace dataset;
- model card with taxonomy, training method, limitations, and evaluation.

### Decision Gate: June 13 Evening

Ship the tuned model only if it:

- improves factor micro-F1 by a meaningful amount;
- does not regress team attribution or unsupported-claim detection materially;
- passes every behavioral property test;
- fits Space memory and startup constraints;
- has acceptable median latency.

Otherwise ship the base model and report the negative result honestly. Do not risk the submission for the Well-Tuned badge.

## Evaluation Plan

### Extraction Metrics

- factor micro-F1 and macro-F1;
- team attribution accuracy;
- severity mean absolute error;
- certainty mean absolute error;
- unsupported-claim precision, recall, and F1;
- ambiguity detection F1;
- exact semantic match rate;
- paraphrase consistency;
- median and p95 latency.

Because constrained decoding guarantees schema shape, schema-validity rate is a runtime health metric, not the main fine-tuning result.

### Behavioral Property Tests

- An unavailable attacker never improves the affected attack.
- Higher severity never produces a smaller adjustment for the same factor.
- Unsupported or irrelevant text produces no forecast adjustment.
- Equivalent paraphrases map to equivalent factor sets within tolerance.
- Home/away references remain correctly attributed.
- Duplicate factors do not stack without bounds.
- Contradictory factors are flagged or handled deterministically.
- Forecast probabilities are finite, nonnegative, and sum to one.
- Hidden results cannot enter the pre-reveal state.

### Integration Tests

- Select match -> extract -> adjust -> score -> reveal.
- Extractor timeout returns a usable fallback state.
- Invalid model output cannot reach the forecast engine.
- Base and tuned adapters satisfy the same interface.
- Space starts without external inference credentials.

## Gradio UI Plan

### Screen 1: Challenge

- Match card with competition and venue context
- Baseline probability bars
- Scenario textbox with three examples
- Extracted-factor chips with severity and certainty
- Before/after probability animation
- User probability controls constrained to sum to 100%
- Commit and reveal action
- Score comparison

### Screen 2: Stress Test

- Match selector
- Factor selector
- Team selector
- Severity slider
- Live probability curve
- Plain-language explanation of deterministic assumptions

### Screen 3: Tiny Model Lab

- Base versus tuned metric table
- Confusion by factor category
- Example successes and failures
- Model size, quantization, latency, and Modal training compute
- Links to model, dataset, traces, and field notes

### Visual Direction

Use a broadcast-analysis aesthetic rather than default Gradio controls:

- dark pitch-inspired background;
- strong team-color probability bars;
- compact match cards;
- visible “baseline” and “scenario” states;
- restrained animation;
- mobile-safe layout.

Polish the primary challenge screen before secondary tabs.

## Delivery Schedule

### June 12: Submission-Safe Vertical Slice

- Scaffold repository and dependencies.
- Implement schemas, taxonomy, rules, Poisson model, and scoring.
- Prepare at least 10 historical matches.
- Implement mock extractor and base-model adapter.
- Add GBNF grammar and validation.
- Build minimal Challenge screen.
- Deploy the first working Space.
- Start synthetic-data generation only after taxonomy freeze.

Exit criteria: a clean user can complete one challenge on the deployed Space.

### June 13: Evaluation and Fine-Tuning

- Finalize 20–30 matches.
- Freeze and manually review extractor test set.
- Benchmark the base model.
- Run one QLoRA job on Modal.
- Build reveal, scoring, and stress-test features.
- Implement behavioral and integration tests.
- Evaluate tuned versus base model.
- Apply the decision gate.

Exit criteria: selected runtime model is known and the complete core experience works.

### June 14: Deployment and Submission Assets

- Merge and quantize the selected model.
- Publish model and dataset/trace artifacts.
- Verify llama.cpp inference in the Space.
- Build Tiny Model Lab.
- Finish custom styling.
- Test cold start, mobile layout, and failure paths.
- Record the 60–90 second demo.
- Draft field notes and social post.

Exit criteria: release candidate is frozen and all submission URLs exist.

### June 15: Buffer and Submit

- Fix only critical defects.
- Re-run smoke tests from a clean session.
- Publish field notes and social post.
- Submit Space, demo, and social links.
- Tag the release commit.

No new features on June 15.

## Acceptance Criteria

### Must Have

- Hosted Gradio Space
- Runtime model <=4B
- llama.cpp inference
- No cloud inference dependency
- Historical challenge playable end to end
- Grammar-constrained semantic extraction
- Deterministic validated adjustments
- Probability visualization and scoring
- At least 20 historical matches
- Automated unit and integration tests
- Demo video and social post

### Should Have

- Fine-tuned model with measured semantic improvement
- Stress-test slider
- Tiny Model Lab
- Published model and dataset/traces
- Field notes
- Custom visual styling

### Could Have

- Live World Cup fixture card
- Forecast Courtroom presentation
- Community leaderboard
- More sophisticated baseline calibration

## Risk Register

| Risk | Trigger | Mitigation |
|---|---|---|
| Space cannot load 3B GGUF | OOM or startup timeout | Quantize more aggressively, reduce context, lazy-load, keep mock/demo fallback |
| llama.cpp lacks model compatibility | Conversion or inference failure | Test base GGUF on June 12; switch to a known-supported <=4B model immediately |
| Fine-tune underperforms | No semantic gain on frozen test | Ship base model; document result |
| Synthetic labels are noisy | Low reviewer agreement | Shrink training set and improve labels rather than train longer |
| Demo feels like hindsight | Showcase relies on known upset | Hide result and use only pre-match or explicitly hypothetical context |
| UI looks like a chat wrapper | Scenario box dominates | Make factors and probability movement the central visual artifact |
| Cloud dependency breaks Off the Grid | Runtime calls external endpoint | Keep all inference in the Space and bundle/cache required artifacts |
| Deadline pressure | Core incomplete by June 13 | Drop secondary tabs and fine-tune before dropping deployable core |

## Release Checklist

- [ ] Registration and organization access confirmed
- [ ] Space created under hackathon organization
- [ ] Model parameter total documented
- [ ] Model license checked
- [ ] Dataset licenses and attribution documented
- [ ] No result leakage in challenge context
- [ ] Base benchmark saved
- [ ] Tuned benchmark saved or negative result documented
- [ ] GGUF and llama.cpp versions pinned
- [ ] Clean Space restart passes
- [ ] Mobile smoke test passes
- [ ] Model card published
- [ ] Dataset or trace card published
- [ ] Field notes published
- [ ] Demo video uploaded
- [ ] Social post published
- [ ] Submission completed before deadline

## Final Pitch

> Underdog Lab fine-tunes a 3B local model to turn messy football narratives into validated forecasting evidence. A transparent statistical engine converts those factors into probabilities, letting users stress-test scenarios, challenge the model, and learn why calibrated forecasts are more useful than confident guesses.
