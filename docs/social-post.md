# Social Post Draft

I built **Underdog Lab** for the @huggingface Build Small Hackathon.

Most AI football predictions are confident prose wrapped around an unverifiable
number. Underdog Lab does the opposite:

A local 360M model reads your scenario text and extracts typed semantic factors
— injuries, fatigue, venue changes — into grammar-constrained JSON. A
deterministic ruleset maps those to bounded adjustments. An Elo + Poisson engine
owns every probability.

The model NEVER emits a score or a probability. It classifies the story.
Transparent math handles the rest.

Try it:
- Pick a hidden historical match (or a live 2026 World Cup fixture)
- Write a scenario: “The favourite's striker is out”
- Watch the model extract factors, team, severity, and certainty
- See the before/after probability shift
- Commit your own forecast
- Reveal the result and get scored with log loss

World Cup 2026 mode covers all 48 teams, 72 group fixtures, and runs Monte Carlo
tournament simulations from current Elo ratings.

No cloud inference. No API keys. The model runs locally in the Space through
llama.cpp.

- Space: https://huggingface.co/spaces/build-small-hackathon/World-Cup-2026-predicition
- Code: https://github.com/OsamaMoftah/World-Cup-2026-predicition
- Model (base): https://huggingface.co/bartowski/SmolLM2-360M-Instruct-GGUF
- Model (tuned, negative result): https://huggingface.co/sammoftah/underdog-lab-smollm2-360m-lora
- Dataset: https://huggingface.co/datasets/sammoftah/underdog-lab-scenarios
- Field notes: https://github.com/OsamaMoftah/World-Cup-2026-predicition/blob/main/docs/field-notes.md

#BuildSmall #Gradio #HuggingFace #SmallModels #FootballAnalytics
