# Field Notes: Building Underdog Lab

_Draft for publication after the final runtime and reviewed evaluation are complete._

## The Problem

Most AI football predictions are confident prose wrapped around an
unverifiable number. Underdog Lab separates the jobs:

- a small language model understands narrative evidence;
- a deterministic ruleset maps evidence to bounded assumptions;
- an Elo-Poisson engine owns the numerical probability.

This makes the system inspectable. A user can see which factor was detected,
which rule changed the model, and why a restated venue fact was rejected.

## Why a Small Model

The language task is narrow. The model does not need encyclopedic football
knowledge or open-ended reasoning. It needs to classify a short scenario,
resolve which team it concerns, and express severity and certainty in a
constrained schema.

The target runtime is SmolLM3-3B in GGUF format through llama.cpp. The app has
no cloud inference dependency.

## Numerical Baseline

The challenge data does not claim historical expected-goals coverage.
`lambda_home` and `lambda_away` are derived from pre-match Elo ratings:

```text
lambda_home = exp(intercept + scale * effective_elo_difference)
lambda_away = exp(intercept - scale * effective_elo_difference)
```

The checked-in coefficients are bootstrap assumptions. Outcomes from the
challenge matches are not used to derive their own rates.

The app uses independent Poisson scoring distributions. This is intentionally
simple and can understate low-score dependence and draw probability.

## Preventing Double Counting

Venue is already represented in each baseline. If a user restates a known
venue fact, the system drops it and explains why. Venue factors apply only to
counterfactual changes, such as moving a home match to neutral ground.

## Fine-Tuning

The planned QLoRA run uses:

- rank 16;
- alpha 32;
- dropout 0.05;
- learning rate around 2e-4;
- two to three epochs;
- one run, not a sweep.

The fine-tuned model is selected only if it beats the base model on a frozen,
manually reviewed test set without material regressions.

## Evaluation

Formatting validity is enforced by grammar and therefore is not the headline
metric. The meaningful measurements are:

- factor micro-F1;
- team attribution accuracy;
- unsupported-claim F1;
- severity error;
- paraphrase consistency;
- inference latency.

The checked-in synthetic test fixtures are marked `review_status=pending`.
Their results are pipeline checks, not publishable model claims.

The first dataset implementation used a small bank of repeated templates and
was rejected during review because it could not measure generalization. The
replacement corpus uses split-specific language banks, multi-factor cases,
negation, ambiguity, irrelevant commentary, unsupported claims, and prompt
injection. Even this replacement remains a pipeline fixture: the competition
fine-tune must use the Modal-generated candidate corpus, and the held-out sets
must be manually approved.

## Behavioral Tests

The repository tests properties that are easy to understand:

- an unavailable attacker never improves that team's attack;
- higher severity creates a monotonic effect;
- unsupported text changes nothing;
- duplicate factors do not stack without bounds;
- known venue facts cannot be double-counted;
- must-win behavior raises both the attacking team's rate and the opponent's
  transition opportunity;
- probabilities remain finite and sum to one.

## What We Learned

1. A grammar solves syntax, not semantic correctness.
2. A transparent fallback keeps the product usable but must be visible in
   traces and evaluation.
3. Famous upsets are memorable demos but dangerous training examples because
   they invite hindsight contamination.
4. A narrow, measurable language task is a better fit for a 3B model than
   asking it to invent calibrated probabilities.

## Final Results

_Measured June 13, 2026 on Apple M5 (cpu-basic benchmarks pending)._

### Base Model Evaluation

| Metric | Base Q8 | Tuned Q8 | Target |
|---|---:|---:|---:|
| Factor micro-F1 | 0.026 | 0.027 | ≥0.20 |
| Team attribution | 0.043 | 0.032 | ≥0.85 |
| Severity MAE | 0.400 | 0.267 | — |
| Median latency | 3.7s | 3.0s | ≤25s |
| Fallback rate | 9.2% | 17.4% | <10% |
| Schema validity | 100% | 100% | 100% |

### Ship Decision: NO-SHIP for tuned adapter

The QLoRA fine-tune (rank=16, 861 examples, 3 epochs, 5m54s on A10G) correctly
learned factor type classification — the tuned Q8 model outputs
`key_attacker_unavailable` where the base model incorrectly outputs
`home_advantage`. However, severity and certainty values are near-zero, triggering
the zero-weight hallucination detector. The deterministic fallback handles both
models identically, producing near-identical scores (F1 delta +0.09 points,
target ≥15).

**Shipping configuration:** Base SmolLM2-360M-Instruct Q8 + deterministic
keyword fallback. Backend honesty labels are visible in the UI. The tuned
adapter (3.3 MB, `sammoftah/underdog-lab-smollm2-360m-lora`) is published
alongside a negative result.

**Dataset:** 861 training examples (compositional synthetic + gap-fill), 56
validation, 98 frozen test. All synthetic. Human review pending.

**Tests:** 43 automated tests passing.

**Key limitation:** The checked-in frozen test labels are synthetic and
unreviewed. Zero-weight hallucination detection rejects the tuned model's
correct factor classifications because severity/certainty are not learned.
This makes the fine-tune look worse than it is on classification accuracy
alone. A future iteration should: manually review test labels, use a
severity-aware loss, or separate factor classification from weight regression.
