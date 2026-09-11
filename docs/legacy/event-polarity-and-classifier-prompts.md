# Spec — Event Polarity & Classifier Prompts

## Part 1 — Polarity of each event (Positive / Negative / Both)

**Reading guide.** "Polarity" = the direction of the market reaction.

- **Positive** = reliably risk-on / bullish for the affected market.
- **Negative** = reliably risk-off / bearish.
- **Both** = direction depends on the *surprise vs. consensus* and/or the *specific outcome*; the
  same event type can push either way, and often pushes different assets in opposite directions at
  once.

Core principle that overrides everything: **markets price the surprise, not the level.** A "good"
number that is worse than expected is negative; a "bad" number that is better than feared is
positive. Also watch the **regime flip** ("good news is bad news") — strong growth/jobs data can
be *negative* when it kills rate-cut hopes.

| # | Event | Polarity | What makes it + vs − |
| --- | --- | --- | --- |
| 1 | Global pandemics & health emergencies | Negative | Demand collapse + risk-off; only narrow exceptions (vaccine names, gold, staples) go up. |
| 2 | Major financial / banking-system crises | Negative | Confidence/funding shock; broad bearish, safe-havens (UST, gold) the only beneficiaries. |
| 3 | Major interstate wars / great-power conflict | Both | − for broad equities/risk; + for oil, gas, gold, defense, ag commodities. |
| 4 | Central-bank decisions & forward guidance | Both | Dovish surprise / cut = +; hawkish surprise / hike = −. Pure surprise play. |
| 5 | Major tariff / trade-war announcements & sanctions | Both | Escalation = − (risk-off); de-escalation/removal = +. Protected domestic sectors can buck the move. |
| 6 | Sovereign-debt crises and defaults | Negative | Risk-free benchmark repricing cascades; bearish for affected sovereign + EM/credit. |
| 7 | CPI / inflation surprises | Both | Cooler-than-expected = +; hotter = −. Classic surprise event. |
| 8 | Non-farm payrolls (NFP) & labor data | Both | Direction depends on surprise AND regime (strong jobs can be − if it removes cuts). |
| 9 | Other macro data (GDP, PMI, retail, PCE, claims) | Both | Beat/miss vs consensus; regime-dependent. |
| 10 | National elections | Both | Depends on which outcome wins vs. what was priced, and the winner's policy mix. |
| 11 | Geopolitical escalations / terrorism | Negative | Reliable risk-off shock; oil/gold/defense rise but broad market falls. |
| 12 | Coups, regime change, sanctions, capital controls | Both | − for the affected sovereign/EM; + for substitute producers / rival exporters. |
| 13 | OPEC+ supply decisions & energy disruptions | Both | Cut/disruption = + for oil & energy equities, − for airlines/consumers; increase = opposite. |
| 14 | Natural disasters | Both | − on impact (insurers, region); + later for reinsurance pricing, cat-bond yields, rebuilding. |
| 15 | Extreme weather & climate-policy announcements | Both | Tightening = + carbon price, − emitters; weather extremes = + energy/ags, − consumers. |
| 16 | Corporate scandals, frauds & mega-bankruptcies | Negative | Bearish for the firm and often peers/CDS; only shorts and competitors gain. |
| 17 | Earnings releases | Both | Beat + raise = +; miss / weak guide = −. Surprise vs. consensus and guidance. |
| 18 | M&A announcements | Both | Target almost always + (premium); acquirer often − (esp. stock-financed). |
| 19 | Regulatory & legal events | Both | Approval / favorable ruling = +; lawsuit / ban / fine / grounding = −. |
| 20 | Leadership changes & C-suite departures | Both | Depends on who, why, and whether seen as upgrade or instability. |
| 21 | Cyber attacks, hacks & IT outages | Negative | Bearish for victim; cybersecurity vendors can rise (narrow exception). |
| 22 | Social-media / viral / meme-driven events | Both | Positive virality = +; controversy / boycott / negative virality = −. |
| 23 | Strikes, labor unrest, civil protests | Negative | Supply disruption + political risk; bearish for affected sectors/region. |
| 24 | Freight & shipping disruptions | Both | + for freight rates & shipping equities; − for importers, retailers, consumers. |
| 25 | Carbon & emissions policy events | Both | Tightening / ambition = + carbon price, − emitters; loosening = opposite. |
| 26 | Routine credit-rating agency actions | Both | Upgrade = +; downgrade = −. Clean binary. |
| 27 | NFT / collectibles / art events | Both | Boom / hype / strong sale = +; bust / fraud / weak sale = −. |
| 28 | Real-estate / housing data | Both | Strong data = + for builders/REITs (unless it lifts rates); weak data = −. |

**Summary**

- **Reliably Negative (7):** pandemics, banking crises, sovereign-debt crises, geopolitical/terror,
  corporate scandals, cyber attacks, strikes.
- **Both / conditional (21):** everything else, including wars (asset-split) and all data, policy,
  and corporate-outcome events.
- **Reliably Positive (0 standalone):** positivity is the favorable *branch* of a Both event — a
  cut, a beat, an approval, a de-escalation, an upgrade.

> Three further event types were added after this table was written — AI / technology
> breakthroughs, Fiscal (debt-ceiling / shutdown), and Stablecoin / DeFi depeg — bringing the
> taxonomy to 31. See [News Source Coverage & Gaps](news-source-coverage-and-gaps.md).

---

## Part 2 — Classifier prompt

> **Start with the single unified prompt below** — one LLM call that outputs
> `positive | negative | both` plus the per-market direction. It is one code path instead of three
> and (per the routing note at the end of this section) usually more robust than three separate
> calls. The single-polarity prompts A/B/C are kept in the **appendix** as a deferred option: adopt
> the split only if a measured precision need demands it.

All prompts share the same inputs and the same overriding rule. Use them as system prompts; pass the
event text plus any market context as the user message. Each emits structured JSON.

### Shared context block (prepend to the prompt)

```
You classify financial-market events by the DIRECTION of their likely market impact.
Universe of markets: equities, forex, bonds/rates, derivatives, commodities, crypto,
prediction markets, sports betting, volatility (VIX), credit/CDS, energy/power, carbon,
freight, weather, real estate, private markets, art, NFT, insurance/reinsurance.

OVERRIDING RULES (apply to every classification):
1. Price the SURPRISE, not the level. Compare the event to the prevailing consensus/expectation.
   If no surprise (fully priced/expected), impact ~ neutral regardless of headline tone.
2. Check the REGIME. In a rate-cut-hungry regime, strong growth/jobs/inflation can be NEGATIVE
   for risk assets ("good news is bad news"), and vice versa.
3. Polarity can be ASSET-SPECIFIC: one event may be bullish for one market and bearish for another.
   When that happens, the correct top-level label is "both".
4. State confidence (0-1) and always name the specific market(s) and the per-market direction.
Inputs you will receive: EVENT_TEXT (required), MARKET (optional focus market),
CONSENSUS/EXPECTATION (optional), AS_OF_DATE (optional).
```

### Unified classifier prompt (default)

```
{{SHARED CONTEXT BLOCK}}

TASK: Classify the event's market impact in ONE pass — decide the top-level polarity AND name the
per-market direction.

1. Apply the overriding rules: price the SURPRISE vs consensus, check the REGIME ("good news is bad
   news"), and remember polarity can be asset-specific.
2. Choose the top-level polarity:
   - "positive": risk-on / bullish for the target market(s) relative to expectations.
   - "negative": risk-off / bearish relative to expectations.
   - "both": direction depends on the surprise/outcome, OR the event pushes different in-scope assets
     in opposite directions (war: oil/defense up, equities down; OPEC cut: oil up, airlines down;
     M&A: target up, acquirer down; tariffs: protected sector up, exporters down).
   - "neutral": fully priced in / no surprise.
3. For each affected in-scope market, give the resolved direction (up/down/mixed) and a magnitude
   bucket. If a direction can't be resolved without a missing input, mark it "mixed" and name the
   required input in "why".
4. Always state confidence and the surprise-vs-consensus read.

OUTPUT JSON:
{
  "polarity": "positive" | "negative" | "both" | "neutral",
  "confidence": 0.0-1.0,
  "surprise_vs_consensus": "above" | "in_line" | "below" | "unknown",
  "drivers": ["surprise_vs_consensus" | "outcome_branch" | "asset_split"],
  "affected_markets": [
    { "market": "...", "direction": "up" | "down" | "mixed", "magnitude": "low" | "med" | "high", "why": "..." }
  ],
  "regime_caveat": "string",
  "rationale": "1-3 sentences"
}
```

## Appendix — optional high-precision split (deferred)

> Use these only if the unified prompt's precision on a specific single-polarity decision proves
> insufficient. They are 3× the LLM calls and 3× the code — do not adopt by default.

### Prompt A — POSITIVE-event identifier

```
{{SHARED CONTEXT BLOCK}}

TASK: Determine whether the event is a POSITIVE (risk-on / bullish) catalyst for the target market.

An event is POSITIVE when, relative to expectations, it RAISES expected cash flows, LOWERS
discount rates/risk premia, or REDUCES uncertainty. Identification signals:
- Dovish monetary surprise: rate cut, slower hikes, dovish guidance, QE/liquidity injection.
- Inflation/data printing in the favorable direction vs consensus (e.g., cooler CPI; jobs that
  support a soft landing without forcing hikes).
- Earnings BEAT + raised guidance; positive pre-announcement.
- M&A: being the TARGET (premium); accretive cash deal for an acquirer.
- Favorable regulatory/legal outcome: approval (FDA, ETF), dismissed suit, lighter rules.
- De-escalation: ceasefire, tariff rollback, sanctions lifted, trade deal.
- Credit-rating UPGRADE; supply increase that lowers input costs for the target sector.
- Strong positive virality / coordinated demand for the specific asset.

DISQUALIFIERS (do NOT label positive):
- The good news is fully priced in (no surprise) -> "neutral".
- Strong data that, in the current regime, removes expected easing -> likely "negative".
- It helps one asset but clearly hurts another in scope -> label "both".

OUTPUT JSON:
{
  "polarity": "positive" | "neutral" | "not_positive",
  "is_positive": true|false,
  "confidence": 0.0-1.0,
  "affected_markets": [{ "market": "...", "direction": "up|down|mixed", "magnitude": "low|med|high" }],
  "surprise_vs_consensus": "above|in_line|below|unknown",
  "regime_caveat": "string",
  "rationale": "1-3 sentences"
}
```

### Prompt B — NEGATIVE-event identifier

```
{{SHARED CONTEXT BLOCK}}

TASK: Determine whether the event is a NEGATIVE (risk-off / bearish) catalyst for the target market.

An event is NEGATIVE when, relative to expectations, it LOWERS expected cash flows, RAISES
discount rates/risk premia, or INCREASES uncertainty. Identification signals:
- Systemic shocks: pandemic, banking/financial crisis, sovereign-debt crisis, major war outbreak.
- Hawkish monetary surprise: surprise hike, hawkish guidance, QT acceleration.
- Inflation/data printing unfavorably vs consensus (hotter CPI; or strong data that forces hikes).
- Earnings MISS / cut guidance; profit warning.
- Adverse regulatory/legal outcome: lawsuit, fine, ban, product grounding, license loss.
- Escalation: new tariffs, sanctions, conflict escalation, terror attack, coup.
- Credit-rating DOWNGRADE; default; major corporate fraud or bankruptcy.
- Cyber attack/hack/outage hitting the issuer; strikes/supply disruption; negative virality.

ALWAYS-NEGATIVE event types (label negative unless clearly priced in): pandemics, banking crises,
sovereign-debt crises, geopolitical/terror shocks, corporate scandals/fraud/bankruptcy, cyber attacks,
strikes/civil unrest.

DISQUALIFIERS (do NOT label negative):
- Fully anticipated / priced in -> "neutral".
- A risk-off event that is simultaneously BULLISH for safe-havens/commodities in scope -> note those
  legs, and if the net scope is genuinely two-sided, label "both".

OUTPUT JSON:
{
  "polarity": "negative" | "neutral" | "not_negative",
  "is_negative": true|false,
  "confidence": 0.0-1.0,
  "affected_markets": [{ "market": "...", "direction": "up|down|mixed", "magnitude": "low|med|high" }],
  "safe_haven_legs": [{ "market": "...", "direction": "up" }],
  "surprise_vs_consensus": "above|in_line|below|unknown",
  "rationale": "1-3 sentences"
}
```

### Prompt C — BOTH / CONDITIONAL-event identifier (and direction resolver)

```
{{SHARED CONTEXT BLOCK}}

TASK: Decide whether the event is CONDITIONAL ("both") -- i.e., its market direction depends on the
surprise or specific outcome, or it pushes different in-scope assets in opposite directions -- and if
so, RESOLVE the actual direction for this specific instance.

Label "both" when ANY of these hold:
- Scheduled data release or decision read against a consensus (CPI, NFP, GDP, PMI, PCE,
  central-bank decision): direction = sign of (actual - expected), adjusted for regime.
- The event has opposing winners/losers in scope (war: oil/defense up, equities down;
  OPEC cut: oil up, airlines down; freight disruption: shipping up, importers down; M&A: target up,
  acquirer down; tariffs: protected sector up, exporters/importers down).
- The outcome is binary/multi-way with different implications (election, court ruling,
  rating action, regulatory approval-vs-denial, earnings beat-vs-miss).

RESOLUTION PROCEDURE for this instance:
1. Identify the consensus/expectation; compute the surprise sign & size.
2. Apply the regime check (is "good = bad" in force right now?).
3. Map each affected in-scope market to up/down/mixed.
4. If one direction dominates the target market, report that net direction while listing opposing legs.

OUTPUT JSON:
{
  "polarity": "both",
  "is_conditional": true,
  "resolved_direction_for_target": "up|down|mixed|undetermined",
  "drivers": ["surprise_vs_consensus" | "outcome_branch" | "asset_split"],
  "affected_markets": [{ "market": "...", "direction": "up|down", "why": "..." }],
  "surprise_vs_consensus": "above|in_line|below|unknown",
  "regime_caveat": "string",
  "confidence": 0.0-1.0,
  "rationale": "2-4 sentences"
}
If you cannot resolve direction without the missing input, set
resolved_direction_for_target="undetermined" and list exactly what input is required.
```

### Routing note (unified vs. the split)

The **default is the unified prompt** (one call → positive | negative | both + per-market direction),
usually more robust than three separate calls. The split is **deferred** — adopt it only for a proven
high-precision single-polarity need. If you do: in production, run a cheap first pass that assigns the
event type, then dispatch: always-negative
types → Prompt B; scheduled data / decisions / binary-outcome / opposing-winners types → Prompt C
(resolver); everything that survives as a clean upside surprise → Prompt A. A single unified prompt
that outputs positive | negative | both plus the per-market direction is usually more robust than
three separate calls; the split exists for high-precision single-polarity detection.
