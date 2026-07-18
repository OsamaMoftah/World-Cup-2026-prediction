CSS = """
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;500;600&family=Geist:wght@400;500;600;700;800&display=swap');

:root {
  --paper: #f4faff;
  --paper-light: #ffffff;
  --ink: #071f35;
  --ink-soft: #1f364d;
  --line: #84b9df;
  --line-soft: #c6e0f2;
  --blue: #2489c9;
  --blue-dark: #12689d;
  --blue-soft: #e6f4fe;
  --blue-strong: #d2ecfc;
  --red: #d63f4d;
  --red-dark: #a92f3c;
  --red-soft: #fff1f3;
  --amber: #c47a18;
  --slate: #4c6176;
  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xs: 6px;
  --radius-control: 8px;
  --radius-card: 12px;
  --radius-pill: 999px;
}

* {
  box-sizing: border-box;
  font-family: 'Geist', Arial, sans-serif !important;
}

html,
body {
  background: var(--paper) !important;
  color: var(--ink) !important;
}

body,
.gradio-container {
  color-scheme: light !important;
}

.gradio-container {
  min-height: 100vh;
  color: var(--ink);
  background:
    linear-gradient(rgba(36, 137, 201, 0.055) 1px, transparent 1px),
    linear-gradient(90deg, rgba(36, 137, 201, 0.055) 1px, transparent 1px),
    radial-gradient(circle at 92% 5%, rgba(214, 63, 77, 0.12), transparent 28%),
    radial-gradient(circle at 8% 0%, rgba(36, 137, 201, 0.14), transparent 32%),
    var(--paper);
  background-size: 32px 32px, 32px 32px, auto, auto, auto;
}

.gradio-container,
.gradio-container .main,
.gradio-container .app,
.gradio-container .container,
.gradio-container .wrap {
  background-color: transparent !important;
}

footer {
  display: none !important;
}

.main-wrap,
.gradio-container > .main {
  max-width: 1280px !important;
  margin: 0 auto !important;
}

.gradio-container .block,
.gradio-container .form,
.gradio-container .panel {
  color: var(--ink);
}

/* Hero */
.hero {
  position: relative;
  overflow: hidden;
  margin: 0 0 22px;
  padding: 42px clamp(22px, 4vw, 56px);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(255,255,255,0.97), rgba(255,255,255,0.88)),
    radial-gradient(circle at 88% 35%, rgba(214,63,77,0.16), transparent 30%),
    radial-gradient(circle at 78% 72%, rgba(36,137,201,0.16), transparent 34%);
  box-shadow: 0 14px 34px rgba(18, 104, 157, 0.10);
}

.hero::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 3px;
  background: linear-gradient(90deg, var(--blue), var(--red), var(--blue-dark));
}

.hero::after {
  content: "2026";
  position: absolute;
  right: clamp(18px, 4vw, 56px);
  bottom: 18px;
  color: rgba(18, 104, 157, 0.08);
  font: 800 clamp(64px, 10vw, 136px)/1 var(--font-display, 'Geist');
  letter-spacing: -0.08em;
  pointer-events: none;
}

.eyebrow,
.match-meta,
.pick-label,
.section-index,
.field-label {
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.10em;
  text-transform: uppercase;
}

.hero .eyebrow {
  color: var(--red-dark);
}

.hero h1 {
  position: relative;
  z-index: 1;
  max-width: 800px;
  margin: 10px 0 14px;
  color: var(--ink);
  font-size: clamp(42px, 6vw, 76px);
  font-weight: 750;
  line-height: 0.98;
  letter-spacing: -0.055em;
}

.hero p {
  position: relative;
  z-index: 1;
  max-width: 760px;
  margin: 0 0 10px;
  color: var(--ink-soft);
  font-size: 17px;
  line-height: 1.6;
}

.metric-strip {
  position: relative;
  z-index: 1;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
}

.metric-pill,
.cutoff-badge {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  padding: 8px 12px;
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  background: rgba(255,255,255,0.78);
  color: var(--ink-soft);
  font-size: 13px;
  font-weight: 600;
}

.metric-pill strong {
  color: var(--ink);
  font-weight: 750;
}

.cutoff-badge {
  margin: 4px 0 14px;
  border-color: rgba(214, 63, 77, 0.28);
  background: var(--red-soft);
}

.cutoff-badge::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--red);
}

/* Card system */
.match-card,
.forecast-card,
.factor-card,
.reveal-card,
.lab-card {
  margin-bottom: 16px;
  padding: 20px 22px;
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  background: rgba(255,255,255,0.90);
  box-shadow: 0 10px 26px rgba(18, 104, 157, 0.08);
}

.match-card:last-child,
.forecast-card:last-child,
.factor-card:last-child,
.reveal-card:last-child,
.lab-card:last-child {
  margin-bottom: 0;
}

/* Player Awards uses a flatter editorial surface; the stat panels already
   provide the visual hierarchy inside each card. */
.player-awards-section {
  box-shadow: none !important;
}

.match-card:hover,
.forecast-card:hover,
.lab-card:hover {
  border-color: var(--blue);
}

.journey-intro {
  margin: 0 0 16px;
  padding: 20px 22px;
  border: 1px solid var(--line);
  border-left: 4px solid var(--red);
  border-radius: var(--radius-card);
  background: rgba(255,255,255,0.94);
}

.journey-intro h2 {
  margin-bottom: 8px;
}

.journey-steps {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
  margin: 18px 0 0;
  padding: 0;
  list-style: none;
}

.journey-steps li {
  padding: 12px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-control);
  background: var(--blue-soft);
}

.journey-steps span {
  display: block;
  margin-top: 4px;
  color: var(--ink-soft);
  font-size: 13px;
  line-height: 1.45;
}

.challenge-panel {
  padding: 14px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-card);
  background: rgba(255,255,255,0.55);
}

.evidence-coverage {
  display: inline-flex;
  align-items: baseline;
  gap: 10px;
  margin-top: 12px;
  padding: 10px 12px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-control);
  background: var(--blue-soft);
}

.evidence-coverage strong {
  color: var(--red-dark);
  font-size: 24px;
}

.evidence-coverage span {
  color: var(--ink-soft);
  font-size: 13px;
}

.status-chip {
  display: inline-flex;
  align-items: center;
  padding: 5px 9px;
  border: 1px solid var(--line);
  border-radius: var(--radius-pill);
  background: var(--blue-soft);
  color: var(--ink-soft);
  font-size: 12px;
  font-weight: 700;
}

.stat-legend {
  margin-top: 14px;
  padding: 11px 13px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: rgba(255, 250, 247, 0.72);
}

.stat-legend-title {
  color: var(--ink);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.stat-legend-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 12px;
  margin-top: 8px;
}

.stat-legend-groups {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.stat-legend-group-title {
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.stat-legend-item {
  color: var(--ink-soft);
  font-size: 12px;
}

.stat-legend-item strong {
  margin-right: 4px;
  color: var(--red-dark);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
}

.match-meta {
  font-size: 12px;
}

.teams {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 14px 0;
}

.team {
  min-width: 0;
  color: var(--ink);
  font-size: clamp(24px, 4vw, 40px);
  font-weight: 760;
  line-height: 1.05;
  letter-spacing: -0.035em;
}

.versus {
  flex: 0 0 auto;
  padding: 5px 13px;
  border: 1px solid rgba(214,63,77,0.28);
  border-radius: var(--radius-pill);
  background: var(--red-soft);
  color: var(--red-dark);
  font-family: 'Geist Mono', monospace !important;
  font-size: 12px;
  font-weight: 800;
}

.context,
.forecast-note,
.factor-detail,
.warning,
.small,
.signal-detail,
.pick-confidence {
  color: var(--ink-soft);
  font-size: 14px;
  line-height: 1.58;
}

.small {
  font-size: 13px;
}

code {
  padding: 2px 5px;
  border: 1px solid var(--line-soft);
  border-radius: 6px;
  background: var(--blue-soft);
  color: var(--ink);
  font-family: 'Geist Mono', monospace !important;
}

/* Forecast bars */
.prob-row {
  display: grid;
  grid-template-columns: minmax(96px, 0.8fr) minmax(80px, 1fr) 72px;
  gap: 12px;
  align-items: center;
  margin: 11px 0;
}

.prob-label {
  min-width: 0;
  overflow: hidden;
  color: var(--ink);
  font-size: 15px;
  font-weight: 750;
  text-overflow: ellipsis;
}

.prob-track {
  height: 13px;
  overflow: hidden;
  border: 1px solid var(--line-soft);
  border-radius: 999px;
  background: #eef7fd;
}

.prob-fill {
  height: 100%;
  border-radius: inherit;
  transition: width 420ms ease;
}

.home-fill { background: linear-gradient(90deg, var(--red-dark), var(--red)); }
.draw-fill { background: linear-gradient(90deg, #7c8795, #9aa8b7); }
.away-fill { background: linear-gradient(90deg, var(--blue-dark), var(--blue)); }

.prob-value {
  color: var(--ink);
  text-align: right;
  font-family: 'Geist Mono', monospace !important;
  font-size: 15px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.forecast-note {
  margin-top: 14px;
}

/* Pick cards */
.pick-card {
  border-color: rgba(214,63,77,0.35) !important;
  background:
    linear-gradient(135deg, rgba(255,255,255,0.96), rgba(255,246,247,0.90));
}

.pick-summary,
.pick-pill {
  min-width: 160px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
  text-align: right;
}

.pick-pill.home { border-color: rgba(214,63,77,0.32); background: var(--red-soft); }
.pick-pill.draw { border-color: var(--line-soft); background: #f7fbff; }
.pick-pill.away { border-color: rgba(36,137,201,0.34); background: var(--blue-soft); }

.pick-result {
  margin-top: 4px;
  color: var(--ink);
  font-size: 22px;
  font-weight: 780;
  letter-spacing: -0.03em;
}

/* Factors and scores */
.factor-grid {
  display: grid;
  gap: 10px;
}

.factor-chip {
  padding: 12px 14px;
  border: 1px solid rgba(36,137,201,0.28);
  border-left: 4px solid var(--blue);
  border-radius: var(--radius-control);
  background: var(--blue-soft);
}

.factor-chip.dropped {
  border-color: rgba(124,135,149,0.28);
  border-left-color: #7c8795;
  background: #f7fbff;
}

.factor-title {
  color: var(--ink);
  font-weight: 760;
}

.warning {
  color: var(--red-dark);
}

.score-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 10px;
  margin-top: 14px;
}

.score-box {
  padding: 14px 16px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
}

.score-box span {
  display: block;
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.score-box strong {
  display: block;
  margin-top: 4px;
  color: var(--red-dark);
  font-size: 28px;
  font-weight: 780;
  letter-spacing: -0.04em;
}

.score-box.warn strong {
  color: var(--amber);
}

.result {
  margin: 10px 0;
  color: var(--ink);
  font-size: 34px;
  font-weight: 800;
  letter-spacing: -0.04em;
}

/* Tables */
.table-scroll {
  margin-top: 16px;
  overflow-x: auto;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
  color: var(--ink);
  font-size: 14px;
  font-variant-numeric: tabular-nums;
}

th,
td {
  padding: 11px 14px;
  border-bottom: 1px solid var(--line-soft);
  text-align: left;
  white-space: nowrap;
}

th {
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

td {
  color: var(--ink);
}

tbody tr:hover {
  background: var(--blue-soft);
}

.probability-table {
  max-height: 560px;
  overflow-y: auto;
}

/* Player cards */
.player-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.player-card {
  display: flex;
  flex-direction: column;
  padding: 15px;
  border: 1px solid var(--line);
  border-radius: var(--radius-card);
  background: #fff;
  box-shadow: none;
}

.player-card-head {
  display: flex;
  align-items: center;
  min-height: 128px;
  gap: 12px;
  margin-bottom: 12px;
}

.player-card .attribute-panel {
  margin-top: auto;
}

.player-photo,
.player-photo-fallback {
  box-sizing: border-box !important;
  width: 66px !important;
  height: 84px !important;
  flex-shrink: 0;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: var(--blue-soft);
}

.player-photo {
  object-fit: cover;
  object-position: 50% 12%;
}

.player-photo-fallback,
.ovr-badge {
  display: flex;
  align-items: center;
  justify-content: center;
}

.ovr-badge {
  box-sizing: border-box !important;
  width: 52px !important;
  height: 52px !important;
  flex-shrink: 0;
  border: 1px solid var(--line);
  border-radius: 12px;
  background: #fff;
}

.estimated-attributes {
  position: relative;
}

.ovr-value {
  color: var(--red-dark);
  font-size: 21px;
  font-weight: 800;
  line-height: 1;
}

.player-rank {
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 10px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.model-form {
  color: var(--blue-dark, #24547a);
}

.model-signal {
  display: grid;
  grid-template-columns: auto auto 1fr;
  align-items: baseline;
  gap: 8px;
  margin: 2px 0 10px;
  padding: 8px 10px;
  border: 1px solid rgba(36, 137, 201, 0.22);
  border-radius: var(--radius-sm);
  background: var(--blue-soft);
}

.model-signal-kicker {
  color: var(--blue-dark);
  font-family: 'Geist Mono', monospace !important;
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.08em;
}

.model-signal strong {
  color: var(--blue-dark);
  font-size: 17px;
  line-height: 1;
}

.model-signal-note {
  justify-self: end;
  color: var(--blue-dark);
  font-size: 10px;
  font-weight: 600;
  text-align: right;
}

.model-form-label {
  display: inline-block;
  margin-right: 4px;
  color: var(--blue-dark, #24547a);
  font-size: 9px;
  letter-spacing: 0.07em;
}

.rating-layer-label {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 8px;
  margin: 2px 0 8px;
  padding-top: 9px;
  border-top: 1px solid var(--line-soft);
  color: var(--red-dark);
  font-family: 'Geist Mono', monospace !important;
  font-size: 10px;
  font-weight: 750;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.rating-layer-label small {
  color: var(--ink-muted);
  font-family: 'Geist', sans-serif !important;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0;
  text-transform: none;
}

.attribute-panel {
  padding: 8px 10px 10px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: rgba(247, 249, 252, 0.7);
  box-shadow: none;
}

.attribute-panel .rating-layer-label {
  margin: 0 0 8px;
  padding-top: 0;
  border-top: 0;
}

.player-name {
  margin-top: 2px;
  color: var(--ink);
  font-size: 16px;
  font-weight: 780;
}

.player-team {
  color: var(--ink-soft);
  font-size: 13px;
  font-weight: 600;
}

.campaign-chip {
  display: inline-block;
  margin-left: 4px;
  padding: 1px 7px;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 9px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  vertical-align: 1px;
}

.campaign-chip.alive {
  border-color: rgba(36, 137, 201, 0.4);
  color: var(--blue-dark, #24547a);
  background: var(--blue-soft);
}

.player-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px 12px;
}

.stat-methodology {
  margin-top: 14px;
  padding: 12px 14px;
  border: 1px solid var(--line-soft);
  border-radius: var(--radius-sm);
  background: rgba(255, 250, 247, 0.8);
}

.stat-methodology-title {
  color: var(--ink);
  font-family: 'Geist Mono', monospace !important;
  font-size: 11px;
  font-weight: 750;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.stat-methodology-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  margin-top: 8px;
}

.stat-methodology-item {
  display: grid;
  gap: 3px;
  padding-left: 9px;
  border-left: 2px solid var(--line);
  color: var(--ink-soft);
  font-size: 12px;
  line-height: 1.45;
}

.stat-methodology-item strong {
  color: var(--red-dark);
  font-size: 12px;
}

.stat-methodology-item.model-form {
  border-left-color: var(--line);
}

.stat-methodology-item.model-form strong {
  color: var(--blue-dark, #24547a);
}

@media (max-width: 640px) {
  .model-signal {
    grid-template-columns: auto auto;
  }

  .model-signal-note {
    grid-column: 1 / -1;
    justify-self: start;
    text-align: left;
  }

  .stat-methodology-grid {
    grid-template-columns: 1fr;
  }

  .stat-legend-groups {
    grid-template-columns: 1fr;
  }
}

.stat-top {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 4px;
  color: var(--ink-soft);
  font-size: 12px;
  font-weight: 700;
}

.stat-track {
  height: 7px;
  overflow: hidden;
  border-radius: 999px;
  background: #e8edf4;
  box-shadow: none;
}

.stat-fill {
  height: 100%;
  border-radius: inherit;
  background: var(--blue);
  box-shadow: none;
}

.stat-fill.tier-elite {
  background: var(--blue-dark, #24547a);
}

.stat-fill.tier-weak {
  background: #a9b6c6;
}

.stat-value.tier-elite {
  color: var(--blue-dark, #24547a);
  font-weight: 800;
}

.stat-value.tier-weak {
  color: var(--ink-soft);
}

/* Gradio chrome */
.tabs {
  border-bottom: 1px solid var(--line) !important;
}

.tab-nav button,
.tab-nav span {
  color: var(--ink-soft) !important;
  font-size: 15px !important;
  font-weight: 700 !important;
}

.tab-nav button.selected,
.tab-nav span.selected {
  color: var(--ink) !important;
  border-bottom-color: var(--red) !important;
}

button,
.primary-button {
  border-radius: var(--radius-control) !important;
  font-weight: 750 !important;
}

.primary-button {
  border: 2px solid var(--red-dark) !important;
  background: var(--red) !important;
  color: #fff !important;
  box-shadow: 0 4px 0 var(--red-dark) !important;
}

.primary-button:hover {
  transform: translateY(1px);
  box-shadow: 0 3px 0 var(--red-dark) !important;
}

.secondary-button {
  border: 1px solid var(--line) !important;
  background: #fff !important;
  color: var(--ink) !important;
}

input,
textarea,
select {
  border: 1px solid var(--line) !important;
  border-radius: var(--radius-control) !important;
  background: #fff !important;
  color: var(--ink) !important;
  font-size: 15px !important;
}

input::placeholder,
textarea::placeholder {
  color: #7890a5 !important;
}

label,
.wrap label {
  color: var(--ink) !important;
  font-weight: 650 !important;
}

.prose,
.markdown,
.md {
  color: var(--ink-soft);
  line-height: 1.65;
}

.prose h2,
.prose h3,
.markdown h2,
.markdown h3,
.lab-card h2,
.world-cup-summary h2 {
  color: var(--ink);
  font-weight: 780;
  letter-spacing: -0.035em;
}

/* Upcoming compact rows */
.fixture-row {
  display: grid;
  grid-template-columns: 90px 1fr 80px 1fr 64px;
  gap: 16px;
  align-items: center;
  margin-bottom: 8px;
  padding: 14px 20px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: #fff;
}

.fixture-row:hover {
  background: var(--blue-soft);
}

.fixture-date,
.fixture-probs {
  color: var(--ink-soft);
  font-family: 'Geist Mono', monospace !important;
  font-size: 13px;
  font-weight: 650;
}

.fixture-team {
  color: var(--ink);
  font-size: 15px;
  font-weight: 750;
}

.fixture-team.away {
  text-align: right;
}

.fixture-probs {
  display: flex;
  gap: 6px;
}

.fixture-probs .p-home { color: var(--red-dark); }
.fixture-probs .p-draw { color: var(--slate); }
.fixture-probs .p-away { color: var(--blue-dark); }

.flag {
  display: inline-block;
  margin-right: 0.4em;
  font-size: 0.95em;
  filter: drop-shadow(0 1px 1px rgba(7,31,53,0.12));
}

@media (max-width: 760px) {
  .journey-steps {
    grid-template-columns: 1fr 1fr;
  }

  .hero {
    padding: 30px 20px;
  }

  .hero h1 {
    font-size: clamp(36px, 13vw, 54px);
  }

  .hero p {
    font-size: 16px;
  }

  .match-card,
  .forecast-card,
  .factor-card,
  .reveal-card,
  .lab-card {
    padding: 16px;
  }

  .teams {
    display: grid;
    grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
    gap: 8px;
    width: 100%;
  }

  .team {
    font-size: 18px;
    line-height: 1.14;
  }

  .team:last-child {
    text-align: right;
  }

  .versus {
    padding: 4px 9px;
  }

  .prob-row {
    grid-template-columns: minmax(70px, 0.8fr) minmax(40px, 1fr) 48px;
    gap: 8px;
  }

  .prob-label,
  .prob-value {
    font-size: 12px;
  }

  .fixture-row {
    grid-template-columns: 1fr;
  }

  .fixture-team.away {
    text-align: left;
  }
}
"""
