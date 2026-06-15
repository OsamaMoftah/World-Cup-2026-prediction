# 90-Second Demo Script — Underdog Lab

_Record with a warm Space. All scenario examples use real challenge or World Cup 2026 data._

## Beat 1 — Hook (0–15s)

“Most AI football predictions are unsupported guesses. Underdog Lab separates
language understanding from probability. A small local model extracts WHAT changed.
Transparent math owns the numbers.”

Show the World Cup 2026 Live tab with the tournament snapshot card:
- 48 teams, 72 group fixtures
- Recorded results (as of June 12 cutoff)

## Beat 2 — World Cup forecast (15–30s)

Select Group A. Show the table with Mexico and South Korea at 3 points.
Scroll through fixture probabilities.

Point to the evidence card: “The fitted model beats the previous baseline
across 8,265 no-lookahead test matches. The 360M language model never writes a
probability.”

## Beat 3 — Scenario extraction (30–50s)

Switch to Challenge tab. Select a hidden historical match.

Enter:

> Canada's striker is confirmed out.

Click **Translate scenario**.

“The local model extracts: key_attacker_unavailable. Team: home. Severity 1.0,
certainty 0.9. It never predicts a score — it only classifies the story.”

Point to the Before/After probability bars.

## Beat 4 — Backend honesty (50–60s)

“When the model produces zero-weight output, the system flags it visibly as
a deterministic fallback. No silent degradation.”

Show the backend label in the factors card.

## Beat 5 — Stress test (60–72s)

Switch to Scenario Stress Test. Move severity from 25% to 100%.

“Every adjustment is bounded and versioned. You can inspect exactly why the
probability changed.”

## Beat 6 — Reveal and scoring (72–85s)

Return to Challenge. Commit a forecast. Reveal the result.

“You, the baseline, and the scenario-adjusted model are all scored with proper
scoring rules. Lower log loss wins. A surprising outcome does not by itself
invalidate a calibrated forecast.”

## Beat 7 — Tiny Model Lab + close (82–90s)

Show Tiny Model Lab tab.

“The QLoRA adapter failed its ship gate, so I rejected it. The safer base model
ships locally with visible fallback. Every probability remains auditable.”

## Recording notes

- Use a warm Space (pre-loaded model, pre-cached first scenario).
- Record at 1080p. Zoom browser to 120% for readability.
- No voiceover over slider movement — let the visual speak.
- Show the backend label clearly when mentioning honesty.
- Keep the Space URL visible in the browser bar for the first and last 5 seconds.
