---
title: World Cup 2026 Forecaster
emoji: ⚽
colorFrom: blue
colorTo: red
sdk: gradio
sdk_version: 6.18.0
python_version: 3.12
app_file: app.py
pinned: false
license: mit
tags:
  - track:backyard
  - sponsor:openai
  - achievement:offbrand
models:
  - HuggingFaceTB/SmolLM2-360M-Instruct
---

# World Cup 2026 Forecaster

A rigorous football forecasting project and small-model experimentation platform.

The project has two related goals:

1. Build calibrated probabilistic forecasts for football matches and tournaments.
2. Evaluate how language models and coding agents contribute to forecasting systems.

The project avoids treating a single tournament-winner guess as evidence. Its primary unit of evaluation is the match-level probability distribution over home win, draw, and away win.

## Recommended Hackathon Entry

**World Cup 2026 Forecaster: Can You Beat the Tiny Pundit?**

The primary experience is now a prospective 2026 tournament forecaster:

- all 48 teams and 72 known group fixtures,
- current group tables from a timestamped result snapshot,
- 1X2 probabilities for every group match,
- Monte Carlo advancement and championship probabilities,
- FIFA's published Round-of-32 slots, all 495 Annex C third-place mappings,
  and the fixed knockout path through match 104,
- bounded scenario adjustments extracted by a local 360M model,
- the original hidden historical challenge as a calibration game.

An interactive, local-first Gradio application where users:

- select a real or historical match;
- inspect a transparent statistical forecast;
- describe a counterfactual scenario in natural language;
- watch a small local model convert that scenario into validated semantic football factors;
- compare the updated probability distribution with the baseline;
- make their own forecast and receive a proper-scoring-rule score.

The language model never invents probabilities or numerical model deltas. It extracts typed semantic factors such as `key_attacker_unavailable`, with team attribution, severity, and certainty. A deterministic ruleset maps those factors into bounded adjustments, and the statistical engine owns the numerical forecast.

## Team

- [@sammoftah](https://huggingface.co/sammoftah) — Hugging Face username, Build Small Hackathon org member.

## Submission Links

- **Submission Space:** https://huggingface.co/spaces/build-small-hackathon/World-Cup-2026-predicition
- **Source:** https://github.com/OsamaMoftah/World-Cup-2026-predicition
- **Demo video:** `PENDING: add a public demo-video URL before final validation`
- **Social post:** `PENDING: add the public social-media post URL before final validation`
- **Team usernames:** `sammoftah`

## Documentation

- [Implementation plan](docs/implementation-plan.md)
- [Hackathon entry plan](docs/hackathon-entry.md)
- [Research synthesis](docs/research.md)
- [Field notes](docs/field-notes.md)
- [Demo script](docs/demo-script.md)
- [Social post draft](docs/social-post.md)
- [Post-hackathon roadmap](ROADMAP.md)
- [Market-data source review](docs/market-data-source-review.md)

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

The default runtime starts downloading and warming a Q8 quantization of
SmolLM2-360M-Instruct when the app boots, then runs it through
`llama-cpp-python`. To
exercise the app without downloading a model:

```bash
UNDERDOG_EXTRACTOR=mock python app.py
```

## Reproduce the Core

```bash
PYTHONPATH=src python scripts/prepare_matches.py
PYTHONPATH=src pytest
UNDERDOG_EXTRACTOR=mock PYTHONPATH=src python scripts/evaluate_extractor.py
make sunday
```

The extraction fixtures are synthetic and remain marked as pending manual
review. Their metrics are pipeline diagnostics, not an accuracy claim. A QLoRA
adapter was trained and published, but the reproducible gate in
`results/qlora_gate_report.json` selected **NO-SHIP** because semantic F1 did
not improve materially, team attribution regressed, and fallback use rose.
The production path therefore remains the base 360M model plus validated
deterministic fallback.

## Fine-Tune on Modal

1. Publish the reviewed JSONL dataset to the Hub.
2. Create a Modal secret named `huggingface-secret` containing `HF_TOKEN`.
3. Run one QLoRA job:

```bash
modal run training/modal_train.py \
  --dataset-repo YOUR_DATASET_REPO \
  --output-repo YOUR_ADAPTER_REPO
```

4. Compare base and tuned models on the frozen test set.
5. Merge and export only if the tuned model passes the decision gate described
   in the implementation plan.

## Evaluation Principles

- Primary metric: multiclass log loss.
- Secondary metrics: Brier score, calibration, sharpness, and optional ranked probability score.
- Historical validation: strictly walk-forward.
- Live predictions: immutable timestamped records created before kickoff.
- Live reporting: prospective artifacts are never mixed with retrospective
  current-model replays.
- Market comparisons: use prices captured at the same forecast horizon and remove the bookmaker margin.
- Tournament forecasts: Monte Carlo simulations derived from match-level probabilities.

## Proposed Repository Layout

```text
app.py
src/underdog_lab/
  data/
  forecasting/
  scenarios/
  telemetry/
  ui/
scripts/
training/
data/
models/
tests/
docs/
```

## Status

The end-to-end application, challenge data, forecasting core, scenario
contracts, llama.cpp adapter, Gradio experience, tests, synthetic-data
pipeline, Modal training job, evaluation script, and submission drafts are
implemented.

All 72 group fixtures have exact UTC kickoff metadata. Forecast artifacts
record model version, calibration temperature, team-rating hash, snapshot
hash, commit, generation time, and information cutoff. `make health` verifies
schedule completeness, snapshot integrity, result freshness, and live-proof
manifests. `make track-record` prints prospective scores by forecast horizon
and keeps current-model retrospective replay clearly separate.

## Result And Deployment Automation

The result path is intentionally semi-automatic:

1. `.github/workflows/result-check.yml` polls football-data.org every three
   hours using `FOOTBALL_DATA_API_KEY`.
2. Provider names, IDs, kickoff times, fixture orientation, competition, and
   season are normalized and validated before a candidate update is written.
3. New results or provider corrections are applied on an automation branch,
   checked by the health report and full test suite, and opened as a PR.
4. A human reviews and merges the PR. Automation never writes results directly
   to `main`.
5. `.github/workflows/deploy-space.yml` pushes the exact merged Git revision
   to `build-small-hackathon/World-Cup-2026-predicition` using `HF_TOKEN`, then waits for the Hub
   repository and running Space revision to match.

Repository secrets required for these workflows:

- `FOOTBALL_DATA_API_KEY`: football-data.org v4 API token.
- `HF_TOKEN`: Hugging Face token with write access to the Space.

Missing secrets are reported as `not configured` in the workflow summary;
they are not treated as a successful update or deployment.

The Space, base model, evaluated adapter, dataset, field notes, and source are
published. `make sunday` closes the QLoRA gate, verifies all 495 official
bracket combinations, runs tests and the data audit, and emits
`results/submission_preflight.json`.

Cold-start and mobile-width checks are complete. Remaining account-dependent
release work is intentionally narrow: publish the demo video and social post,
then record the final hackathon submission URL in `release/submission.json`.

## Important Claim Boundary

The initial release should claim to be an experimental forecasting lab, not the most accurate model in football. Accuracy claims require a frozen benchmark, held-out evaluation, uncertainty intervals, and comparison against de-margined market probabilities at matched timestamps.

## Build Small submission

Submitted to the **Backyard AI** track and positioned for **Tiny Titan**,
**Best Agent**, and **Off Brand**. The app runs as a Gradio Space inside the
`build-small-hackathon` organization with a custom CSS interface that pushes
past the default Gradio look while keeping the forecast workflow intact.

Submission readiness:

- YAML tags are present: `track:backyard`, `sponsor:openai`, `achievement:offbrand`.
- The local scenario reader is `HuggingFaceTB/SmolLM2-360M-Instruct` at 360M parameters, well below the 32B cap and the 4B Tiny Titan threshold.
- The project includes a short product story, architecture notes, methodology, evaluation principles, and local setup instructions.
- Team username is listed above.
- Demo video and social-post URLs are the remaining fields to replace before the final validator run.

Built, redesigned, tested, deployed, and prepared for submission with OpenAI
Codex. Codex-attributed commits are available in the linked public GitHub
repository.
