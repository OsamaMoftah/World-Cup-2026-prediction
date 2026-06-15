# Build Small Hackathon Entry Plan

_Date assessed: June 12, 2026_

## Eligibility and Constraints

The Build Small Hackathon page states:

- registrations closed June 3, 2026;
- the build window runs June 5–15, 2026;
- entrants must deploy a Gradio app as a Hugging Face Space;
- total model parameters must be at most 32B;
- submission requires the Space, a short demo video, and a social-media post.

This plan assumes the entrant registered and joined the hackathon organization before registration closed.

## Concept Evaluation

| Concept | Originality | Small-model fit | AI is essential | Demo appeal | Three-day feasibility | Verdict |
|---|---:|---:|---:|---:|---:|---|
| Direct World Cup winner chatbot | 2/5 | 3/5 | 2/5 | 2/5 | 5/5 | Too generic and scientifically weak |
| Live multi-model benchmark | 4/5 | 1/5 | 4/5 | 3/5 | 2/5 | Needs many external APIs and does not fit the small-model theme |
| Automated betting assistant | 3/5 | 3/5 | 3/5 | 3/5 | 2/5 | Data, safety, execution, and accuracy claims create avoidable risk |
| Static statistical dashboard | 2/5 | 5/5 | 1/5 | 3/5 | 5/5 | Useful, but AI is not load-bearing |
| **Underdog Lab** | **5/5** | **5/5** | **5/5** | **5/5** | **4/5** | **Recommended** |

## Recommended Product

### Underdog Lab: Can You Beat the Tiny Pundit?

Underdog Lab is an interactive football forecasting game and counterfactual simulator.

A user chooses a match, sees a transparent baseline forecast, and writes a scenario such as:

> The favorite's striker is unavailable, the match is at altitude, and the underdog only needs a draw.

A local model converts the statement into semantic factors:

```json
{
  "factors": [
    {
      "factor_type": "key_attacker_unavailable",
      "team": "home",
      "severity": 0.8,
      "certainty": 0.9,
      "evidence": "the favorite's striker is unavailable"
    },
    {
      "factor_type": "altitude_disadvantage",
      "team": "away",
      "severity": 0.5,
      "certainty": 0.7,
      "evidence": "the match is at altitude"
    }
  ],
  "unsupported_claims": [],
  "ambiguities": []
}
```

A deterministic, versioned rule table maps validated factors to bounded numerical adjustments. The language model never emits probabilities or expected-goal deltas. The statistical engine recomputes the scoreline distribution and displays how and why the forecast changed.

The user then makes a forecast. In historical challenge mode, the app reveals the actual result and scores the user, baseline, and adjusted model with log loss and Brier score.

## Why This Is a Strong Entry

### Honest Small-Model Fit

A 3B–4B local instruction model is sufficient for constrained extraction and concise explanation. The application does not pretend that a small language model is a superior numerical forecaster.

The current recommendation is `HuggingFaceTB/SmolLM3-3B`, subject to immediate llama.cpp and Space compatibility testing. Use one model for the submitted runtime.

### AI Is Load-Bearing

The model translates unconstrained human football scenarios into a validated semantic representation. Grammar-constrained decoding guarantees the output shape; fine-tuning and evaluation target semantic understanding rather than formatting.

### Delight and Replayability

The historical challenge mode creates immediate feedback:

1. inspect the baseline;
2. add a scenario;
3. predict;
4. reveal the real match;
5. compare scores;
6. challenge another match.

The scenario stress test provides the strongest visual moment: changing severity moves the forecast in real time.

## Track Recommendation

Enter **An Adventure in Thousand Token Wood** unless there is a specific real person who will use the tool and can appear in the demo. The interactive forecasting challenge has a clearer path to delight, originality, and community sharing.

## Awards and Merit Badges

The hackathon lists six merit badges:

1. **Off the Grid:** no cloud APIs at runtime.
2. **Well-Tuned:** use a fine-tuned model published on Hugging Face.
3. **Off-Brand:** custom UI beyond the default Gradio presentation.
4. **Llama Champion:** run the model through llama.cpp.
5. **Sharing is Caring:** publish an agent trace on the Hub.
6. **Field Notes:** publish a report about the build and lessons.

**Tiny Titan** is a separate special award for strong applications using models around 4B parameters or smaller.

The recommended strategy is local llama.cpp inference in the Space, with Modal used for dataset generation, QLoRA training, and evaluation. A runtime Modal endpoint would conflict with the Off the Grid strategy.

## Minimum Viable Architecture

```text
Gradio UI
  -> match selector / historical challenge
  -> user scenario
  -> local SLM semantic extraction
  -> grammar and Pydantic validation
  -> deterministic factor-to-adjustment rules
  -> Poisson forecast engine
  -> probability and scoreline visualization
  -> user forecast scoring
  -> append-only trace log
```

## Guardrails

- Require probabilities to sum to one.
- Clamp all deterministic adjustments to documented ranges.
- Reject unresolved team references and malformed semantics.
- Distinguish dataset facts from user-supplied hypotheticals.
- Do not market the app as betting advice.
- Keep historical results hidden until forecast commitment.
- Show uncertainty, assumptions, and limitations.

## Delivery Strategy

Build the entire application against the base model first. Fine-tuning is a drop-in upgrade, not a dependency for submission.

### June 12

- Build and deploy the first end-to-end vertical slice.
- Freeze the factor taxonomy.
- Test base-model GGUF inference through llama.cpp.
- Start synthetic-data generation after the schema is frozen.

### June 13

- Freeze and review the evaluation set.
- Benchmark the base model.
- Run one QLoRA fine-tune on Modal.
- Complete challenge scoring and stress testing.
- Decide whether the tuned model is measurably better.

### June 14

- Quantize and publish the selected model.
- Finish custom UI and Tiny Model Lab.
- Cold-start test the Space.
- Record the demo and draft submission materials.

### June 15

- Fix critical defects only.
- Publish field notes and social post.
- Submit before the deadline.

See [implementation-plan.md](implementation-plan.md) for contracts, modules, tests, acceptance criteria, and the full release checklist.

## Demo Storyboard

1. “Most AI football predictions are unsupported guesses.”
2. Select a hidden historical match.
3. Show the baseline probability without revealing the result.
4. Enter a realistic scenario.
5. Show extracted semantic factors.
6. Move severity and show the probability shift.
7. Commit the user's forecast.
8. Reveal the historical result and compare scores.
9. End on: “A 3B local model understands the story; transparent math owns the probability.”

## Judging Risks

### It Looks Like a Statistics App With a Chat Box

Make extracted factors, severity controls, and probability movement the central interaction.

### Accuracy Claims Are Unconvincing

Avoid “best predictor” claims. Show frozen extraction metrics, behavioral tests, and documented statistical assumptions.

### Fine-Tuning Consumes the Schedule

Use one QLoRA run and a June 13 decision gate. Ship the base model if the tuned model does not improve semantic extraction.

### Model Runtime Is Slow

Use a quantized 3B model, short constrained outputs, model warming, and cached examples. Test deployment on June 12.

### Historical Demo Creates Hindsight Bias

Hide outcomes, exclude showcase matches from training, and distinguish pre-match evidence from hypothetical scenarios.

## Post-Hackathon Roadmap

After submission, extend the repository into the full forecasting research platform:

- walk-forward international match benchmark;
- Elo and Dixon-Coles baselines;
- live timestamped forecasts;
- tournament simulation;
- market comparison at fixed horizons;
- agent-built pipeline competition;
- small-model extraction ablations;
- public leaderboard and calibration report.

## Decision

Build **Underdog Lab** for the hackathon and preserve **Football Prediction Lab** as the broader research project. The hackathon product must remain narrow, playable, local, measurable, and polished.
