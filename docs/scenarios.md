# Scenarios

Ten patterns of *"if this happens, expect that — and then, later, this"*, each anchored in a real
episode. They describe what FortuneTeller is ultimately meant to warn about, and they are the test
cases its measurements will eventually have to reproduce. Unfamiliar term? See the
[Glossary](glossary.md).

> **These are hypotheses, not predictions.** Each scenario is one historical episode, and one
> episode is `n = 1`. The directions below are what happened, not what will happen next time; the
> product may only say "expect" once a measured history stands behind it (see the
> [Legend](legend.md), principle 1). Today only scenario 1 is inside the MVP.

Every number below was checked on 2026-09-25 against daily closes from Yahoo Finance (FRED for the
2-year yield) unless marked *reported*: those come from contemporary reporting and are not in the
free daily data.

## How to read a scenario

Each one runs through three phases:

| Phase | When | What it is |
| --- | --- | --- |
| **Shock** | Minutes to the first close | The market's first reaction to the news |
| **Aftershock** | Days to a few weeks | Second-order effects: contagion, a policy response, a reversal, the next shoe dropping |
| **Resolution** | Weeks to months | What finally ended it, and where prices settled |

Instruments are named by their canonical symbol from `instruments.csv` (`SPY / ES`, `UST10Y / ZN`,
`DXY`, `GC / XAU`, `VIX`, `BRN`, `BTC`, `NVDA`) where one exists. Several scenarios need
instruments outside today's universe (the Nikkei, the yen, sterling, regional banks); they are named
plainly and flagged.

## The ten at a glance

| # | Scenario | Event type | Episode | Shock → aftershock in one line | Reachable at |
| --- | --- | --- | --- | --- | --- |
| 1 | Inflation surprise | `CPI / inflation surprise` | 2022-09-13 / 2022-11-10 | Direction set by the surprise's sign; the Fed decision follows within weeks | **MVP** |
| 2 | Central-bank surprise meets a crowded trade | `Central-bank decision` | 2024-07-31 BoJ | Carry trade unwinds in days, then snaps back | Rung 1 + breadth |
| 3 | War breaks out | `Major interstate war` | 2022-02-24 Ukraine | Stocks shrug by the close; commodities spike for two weeks | Rung 7 |
| 4 | A bank fails | `Banking / financial crisis` | 2023-03-10 SVB | Yields collapse; contagion arrives in waves for seven weeks | Rung 7 |
| 5 | A pandemic spreads | `Global pandemic / health emergency` | 2020-02 COVID | A month-long crash that ends on the policy response | Rung 7 |
| 6 | Tariff shock | `Tariff / trade-war / sanctions` | 2025-04-02 | Stocks, bonds and the dollar fall together; a policy pause reverses it | Rung 7 |
| 7 | Fiscal credibility shock | `Sovereign-debt crisis` | 2022-09-23 UK mini-budget | Currency and bonds break; a political reversal ends it | Rung 7 + breadth |
| 8 | Natural disaster | `Natural disaster` | 2011-03-11 Japan | The second-order event is worse than the first; the currency rises | Rung 7 + breadth |
| 9 | Stablecoin collapse | `Stablecoin / DeFi depeg` | 2022-05 Terra | Counterparty failures months apart | Rung 7 |
| 10 | Technology shock to a leader | `AI / technology breakthrough` | 2025-01-27 DeepSeek | Single-name crash, partial rebound next day | Rung 7 |

"Reachable at" is the [roadmap](roadmap.md) stage at which FortuneTeller could first measure the
scenario; "breadth" means it also needs instruments beyond today's five.

---

## 1. Inflation surprise

**If** CPI comes in **above** expectations, **expect** yields and the dollar up, stocks and gold
down, VIX up — on the day. **Then** expect the move to be carried forward by the next central-bank
decision. **If below**, expect the mirror image. The direction is decided by the *sign* of the
surprise, which is why `effect_size_seed` records CPI as `conditional`.

| Phase | Hot print — August CPI, released 2022-09-13 | Cool print — October CPI, released 2022-11-10 |
| --- | --- | --- |
| Shock | `SPY / ES` −4.32%, `UST10Y / ZN` +6 bps (3.36% → 3.42%), `DXY` +1.4%, `GC / XAU` −1.3%, `VIX` 23.9 → 27.3 | `SPY / ES` +5.54%, `UST10Y / ZN` −32 bps (4.15% → 3.83%), `DXY` −2.1%, `GC / XAU` +2.3%, `VIX` 26.1 → 23.5 |
| Aftershock | The Fed raised rates by 0.75 pp on 2022-09-21. The S&P 500 kept falling to a closing low of 3,577 on 2022-10-12, another 9% down | The S&P 500 rose another 3% to a close of 4,080 on 2022-11-30. The Fed slowed to a 0.5 pp hike on 2022-12-14 |
| Resolution | Ends at the next data point that changes the rate path | Same |

**For FortuneTeller:** the MVP's own question. Step 3 asks whether CPI days move more than ordinary
days; step 4 asks whether the size of the move tracks the size of the surprise.

## 2. Central-bank surprise meets a crowded trade

**If** a central bank moves against a heavily used trade — here, the Bank of Japan raising rates
while investors borrowed cheap yen to buy other assets (the *carry trade*) — **expect** the trade to
unwind violently over a few days, especially if a second shock lands at the same time. **Then**
expect a fast snap-back once the central bank signals it will hold.

| Phase | Episode: BoJ hike 2024-07-31, weak US payrolls 2024-08-02 |
| --- | --- |
| Shock | Nikkei −2.5% (08-01), −5.8% (08-02), **−12.4% (08-05)**, its largest points drop on record. `VIX` 23.4 → 38.6 at the close, 65.7 intraday. `SPY / ES` −3.0% on 08-05. The yen strengthened from 161.6 per dollar (07-04) to 144.7 (08-07), about 10% |
| Aftershock | Nikkei **+10.2%** the next day. On 08-07 the BoJ's deputy governor said it would not raise rates while markets were unstable (*reported*) |
| Resolution | Nikkei back to 38,700 by 2024-09-02, up 23% from the 08-05 low. Half-life measured in days |

**For FortuneTeller:** the move came from *positioning*, not from the size of the rate change (a
quarter point). Two events compounding within days is the attribution problem at its sharpest. Needs
the Nikkei and the yen in the universe.

## 3. War breaks out

**If** a long-feared invasion finally happens, **expect** commodities to spike and a sharp intraday
fall in stocks that may not survive to the close — the event was partly priced in beforehand.
**Then** expect the commodity move to keep building for one to two weeks as sanctions and supply
effects become clear.

| Phase | Episode: Russia invades Ukraine, 2022-02-24 |
| --- | --- |
| Shock | `BRN` above $100 for the first time since 2014 (*reported*; intraday high $105.75), closing +2.3% at $99.08. `GC / XAU` +0.8%. `SPY / ES` fell to 4,115 intraday (−2.6%) and then **closed +1.5%** |
| Aftershock | `BRN` closed at $128 on 2022-03-08 (intraday high $137); `GC / XAU` closed at $2,043 the same day. The Fed began raising rates on 2022-03-16, into an oil-driven inflation spike |
| Resolution | By the end of April, `BRN` at $109 and `GC / XAU` at $1,912, near pre-invasion levels. The inflation effect outlasted the price spike |

**For FortuneTeller:** a shock that was expected; `priced_in_prior` exists for exactly this. The
equity close alone would say "no effect". Commodities carried the aftershock, not stocks.

## 4. A bank fails

**If** a bank fails suddenly, **expect** its peers to crash and short-term yields to collapse as the
market prices out rate hikes. **Then** expect contagion in waves, each a week or more apart, while
the broad index recovers.

| Phase | Episode: Silicon Valley Bank, seized 2023-03-10 |
| --- | --- |
| Shock | US regional banks (`KRE`) −8.1% (03-09), −4.4% (03-10), −12.3% (03-13). The **2-year yield fell from 5.05% to 4.03% in three trading days**, about −100 bps. `SPY / ES` −1.9%, −1.5%, −0.2% |
| Aftershock | 03-12: deposits of SVB and Signature Bank guaranteed and a new Fed lending facility opened. 03-19: UBS takes over Credit Suisse. 05-01: First Republic seized and sold. Regional banks bottomed on 05-04, down 37% from 03-08. `GC / XAU` rose 11% to $2,016 by 04-14 |
| Resolution | `SPY / ES` was 3.6% *higher* on 05-05 than on 03-08. The damage stayed in the sector |

**For FortuneTeller:** the aftershock is sector-specific, and waves arrive weeks apart. An
index-level measurement would miss most of it. Regional banks are outside the universe.

## 5. A pandemic spreads

**If** a pandemic reaches the major economies, **expect** a crash that unfolds over weeks, not a
single day, with volatility at records. **Then** expect the turning point to be the policy
response, and a full recovery within months.

| Phase | Episode: COVID-19, February–March 2020 |
| --- | --- |
| Shock | `SPY / ES` from a record 3,386 (2020-02-19) to 2,237 (2020-03-23): **−33.9% in 23 trading days**. On 03-16, the day after an emergency Sunday rate cut to zero, `SPY / ES` −12.0% and `VIX` closed at a record 82.69 |
| Aftershock | 03-23: the Fed announced unlimited asset purchases; that day was the low. Fiscal relief followed within the week |
| Resolution | `SPY / ES` set a new record close of 3,390 on 2020-08-18, five months after the low |

**For FortuneTeller:** the "shock" phase lasted a month, so a one-day window measures a fraction of
it. A policy response can mark the bottom better than the news itself.

## 6. Tariff shock

**If** large, unexpected tariffs are announced, **expect** a two-day equity crash and a volatility
spike. **Then** watch for a regime flip: Treasuries and the dollar may *fall* with stocks rather
than act as havens. Expect a policy pause to trigger a violent reversal.

| Phase | Episode: US tariffs announced after the close on 2025-04-02 |
| --- | --- |
| Shock | `SPY / ES` −4.84% (04-03) and −5.97% (04-04), about −10.5% in two days. `VIX` closed at 45.3 on 04-04 and reached 60.1 intraday on 04-07 |
| Aftershock | **`UST10Y / ZN` rose 51 bps in a week** (3.99% on 04-04 → 4.49% on 04-11), and `DXY` fell 5.3% (103.8 → 98.3 by 04-21). `GC / XAU` closed at a record $3,425 on 04-21 |
| Resolution | 04-09: a 90-day pause on most tariffs, and `SPY / ES` **+9.52%** in one day |

**For FortuneTeller:** in an ordinary risk-off move, Treasury yields and the dollar go the other way.
A model trained on the usual sign would have been confidently wrong here. This is why confidence
must be calibrated per regime (roadmap rung 3).

## 7. Fiscal credibility shock

**If** a government announces large unfunded tax cuts into high inflation, **expect** its currency
and its bonds to fall together, fast. **Then** expect central-bank intervention, and a resolution
only when the policy is reversed.

| Phase | Episode: UK "mini-budget", Friday 2022-09-23 |
| --- | --- |
| Shock | Sterling fell more than 3% on the day (*reported*) and hit an all-time low below $1.04 intraday on Monday 09-26. FTSE 100 −2.0%. 30-year gilt yields rose by more than a percentage point within days (*reported*). Spillover: `UST10Y / ZN` from 3.69% (09-23) to 3.97% (09-27) |
| Aftershock | 09-28: the Bank of England began emergency purchases of long-dated gilts; `UST10Y / ZN` fell back to 3.72% the same day. 10-14: the chancellor was dismissed; 10-17: most of the measures reversed |
| Resolution | 10-20: the prime minister resigned. Sterling was back at $1.16 by 10-31 |

**For FortuneTeller:** the resolution was political, not economic. **Measurement warning:** Yahoo's
daily currency bars place the Friday move on Monday — the same wrong-day trap as
[step 1](steps/step-1-releases.md), and a reason FX needs its day boundary checked before use.
Needs sterling and gilts in the universe.

## 8. Natural disaster

**If** a major disaster hits a large economy, **expect** a local equity fall, and watch for a
second-order event that is worse than the first. **Then** expect a counterintuitive currency
move — money coming home — and possibly coordinated intervention.

| Phase | Episode: Tōhoku earthquake and tsunami, 2011-03-11, 14 minutes before the Tokyo close |
| --- | --- |
| Shock | Nikkei −1.7% (03-11). Then −6.2% (03-14) and **−10.6% (03-15)** as the Fukushima nuclear crisis escalated — the second event did more damage than the first |
| Aftershock | The yen *strengthened*, to 79.1 per dollar at the close on 03-17 (a post-war record; stronger still intraday, *reported*), on expectations that Japanese firms would bring money home. 03-18: the G7 intervened jointly to weaken it |
| Resolution | Nikkei +5.7% on 03-16, and 11.5% above its 03-15 close by 04-15 |

**For FortuneTeller:** the disaster country's currency rose. Free daily data also understates the
intraday extreme of the currency move. Needs the Nikkei and the yen.

## 9. Stablecoin collapse

**If** a major stablecoin loses its peg, **expect** a sharp crypto sell-off. **Then** expect
aftershocks months apart, as the firms that held it fail one after another.

| Phase | Episode: TerraUSD, May 2022 |
| --- | --- |
| Shock | TerraUSD lost its dollar peg around 2022-05-09 (*reported*). `BTC` fell from $35,500 (05-07) to $28,940 (05-11), −18% |
| Aftershock | 06-12: the crypto lender Celsius froze withdrawals (*reported*), and other firms exposed to Terra followed. `BTC` closed at $19,020 on 06-18, down 46% from 05-07 |
| Resolution | A third wave came six months later: the exchange FTX collapsed and filed for bankruptcy on 2022-11-11 (*reported*). `BTC` fell 25% between 11-06 and 11-21 |

**For FortuneTeller:** each aftershock is itself a new event — a chain of counterparty failures,
not one reaction decaying. A reaction window of days would catch only the first link.

## 10. Technology shock to a leader

**If** news suggests a dominant company's advantage is weaker than priced, **expect** a single-stock
crash large enough to move the index, and a flight to safety. **Then** expect a partial rebound the
next day, with later moves hard to attribute.

| Phase | Episode: DeepSeek's low-cost AI model hits markets, 2025-01-27 |
| --- | --- |
| Shock | `NVDA` **−16.97%** ($142.6 → $118.4), the largest one-day loss of market value for any US company (*reported*). Nasdaq −3.1%, `SPY / ES` −1.5%, `UST10Y / ZN` −10 bps (4.63% → 4.53%) |
| Aftershock | `NVDA` **+8.9%** the next day |
| Resolution | `NVDA` closed at $94.31 on 2025-04-04, but by then the tariff shock (scenario 6) was under way, so how much of that fall belongs to this event is unknowable from prices alone |

**For FortuneTeller:** attribution fails as soon as a second event arrives. Separating the two
needs an abnormal return — the move beyond what the market as a whole did.

---

## What the ten have in common

These are the lessons that shape what FortuneTeller must measure:

1. **The aftershock is often bigger than the shock.** Scenarios 1 (hot), 3, 4, 5, 8 and 9 all moved
   further after the first day than on it. A one-day window measures only the start.
2. **Policy responses mark the turn.** A central bank's reassurance, a deposit guarantee, unlimited
   asset purchases, a tariff pause, a reversed budget, a joint intervention: in six of the ten
   (scenarios 2, 4, 5, 6, 7, 8) the turning point was a policy decision, not the passage of time.
3. **Reversals can be as violent as the shock** (+10.2% for the Nikkei, +9.5% for the S&P 500, +8.9%
   for NVDA the next day). Direction over a day and over a week can disagree.
4. **The usual correlations can flip** (scenario 6). A warning built on the usual sign needs to know
   when it no longer holds.
5. **Contagion comes in waves weeks or months apart** (scenarios 4 and 9). Each wave is best treated
   as its own event.
6. **Expected events move less than their size suggests** (scenario 3). Without `priced_in_prior`,
   a well-anticipated shock looks like no effect.
7. **Free daily data has blind spots**: intraday extremes (scenarios 2, 8) and, for currencies, the
   day boundary (scenario 7).
