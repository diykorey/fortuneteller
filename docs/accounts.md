# Accounts and external services

Which outside services this project depends on, who owns the account, and where the credential
lives. **No secrets in this file** — it records *where* a key is kept, never the key itself.

Anything listed here is free unless the cost column says otherwise. Keeping it that way is a design
constraint, not an accident: see [`legend.md`](legend.md).

## In use

| Service | Account | Credential | Used for | Cost |
| --- | --- | --- | --- | --- |
| [FRED](https://fredaccount.stlouisfed.org/) — Federal Reserve Economic Data | Dedicated dev Gmail account | `FT_FRED_API_KEY` in `.env` | CPI release dates and actuals — [step 1](steps/step-1-releases.md); the breakeven's daily values for `load-prices` — [the breakeven](steps/breakeven.md) | Free |
| [GitHub](https://github.com/diykorey/fortuneteller) | `diykorey` | local git + `gh` auth | Code hosting, CI, issue tracker, the scoreboard on GitHub Pages | Free |
| Yahoo Finance chart API | None | No key | Daily closes for every market but the breakeven: `load-prices` | Free, unofficial |
| Nasdaq economic calendar | None | No key | The free consensus: [free consensus](steps/free-consensus.md) | Free, no stated terms |
| TradingView economic calendar | None | No key | Release history for the flows FRED lacks, and the consensus where Nasdaq has none: [consensus fallback](steps/consensus-fallback.md) | Free |
| Federal Reserve website | None | No key | FOMC calendars and statements: [rung 1](steps/rung-1-more-events.md), [the Fed statement's sentiment](steps/fed-statement-sentiment.md) | Free |
| Cleveland Fed inflation nowcast | None | No key | CPI's nowcast baseline: [MVP step 4](steps/step-4-surprise.md) | Free |

## Expected later

Listed so the cost and signup burden are visible in advance, not to imply they are set up.

| Service | Needed for | Key required | Cost |
| --- | --- | --- | --- |
| BLS | Cross-checking release dates against the official schedule | Optional | Free |
| A paid consensus or intraday prices | Sharper measurement; deferred, not dropped ([Decisions](decisions.md), 2026-10-09 and 2026-10-23) | Yes | Paid |

## Rules

- **Credentials live in `.env`**, which is gitignored. Never commit one; if a key is ever pushed,
  rotate it rather than rewriting history and hoping.
- **Every variable is `FT_`-prefixed** and read through `src/fortuneteller/config.py`. A key that
  does not go through `settings` is a key nobody will find later.
- **A service earns a row here when the code actually calls it**, not when it is being considered.
  The "expected later" table is the place for candidates.
- **Describe accounts, do not spell them out.** This repository is public. Name the account by role
  ("dedicated dev Gmail account") rather than by address — an email in a public repo is permanent
  once pushed, and scraped shortly after. The owner knows which account it is; nobody else needs to.
- **Free tiers only** for now. Anything paid is a decision, not a default, and belongs in the
  roadmap before it belongs here.
