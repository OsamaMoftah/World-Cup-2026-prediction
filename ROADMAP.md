# Post-Hackathon Roadmap

The submission release deliberately stops at a fitted, walk-forward-tested
Dixon-Coles Elo model plus a local small-model scenario interface. The items
below are research and production work, not claims about the submitted system.

## Live Forecast Operations

- [x] Add verified UTC kickoff times for every fixture.
- Generate immutable forecasts at fixed 24-hour, 6-hour, and final pre-match
  horizons.
- [x] Add audited batch result ingestion, forecast scoring, and
  data-freshness/integrity checks.
- [x] Add SHA-256 manifests for exact-kickoff live forecast proofs.

## Statistical Evaluation

- Add bootstrap confidence intervals for log loss, Brier score, and RPS.
- Publish reliability diagrams, expected calibration error, and sharpness.
- Evaluate confederation, Elo-gap, tournament-stage, and favorite/underdog
  slices.
- [ ] Acquire legally reusable timestamp-matched bookmaker probabilities.
- [x] Implement proportional, power, and Shin de-margining plus a separate
  market-blend gate against the calibrated production baseline.
- [x] Test post-hoc temperature calibration with a separate ship gate.

## Model Development

- [x] Evaluate and remove the unconfirmed host-country Elo bonus.
- Fit extra-time and penalty resolution from historical knockout matches.
- Add fair-play event data for complete FIFA tie-break resolution.
- Evaluate statistical ensembles only after defining a frozen benchmark.

## Scenario Extraction

- Complete independent human review of validation and test labels.
- Build a claim-ready benchmark with reviewer agreement statistics.
- Improve attribution and negation handling before attempting another
  fine-tune.
- Keep deterministic fallback visible and measure its production frequency.

## Data Provenance

- Cross-check the encoded Annex C table against FIFA's primary regulations PDF
  and store the source checksum.
- Version team ratings, squads, injuries, suspensions, weather, and venue
  inputs with explicit information cutoffs.

None of these items should be described as implemented until its own
reproducible evaluation and release gate passes.
