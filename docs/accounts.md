# Accounts and external services

Which outside services this project depends on, who owns the account, and where the credential
lives. **No secrets in this file** — it records *where* a key is kept, never the key itself.

Anything listed here is free unless the cost column says otherwise. Keeping it that way is a design
constraint, not an accident: see [`legend.md`](legend.md).

## In use

| Service | Account | Credential | Used for | Cost |
| --- | --- | --- | --- | --- |
| [FRED](https://fredaccount.stlouisfed.org/) — Federal Reserve Economic Data | Dedicated dev Gmail account | `FT_FRED_API_KEY` in `.env` | CPI release dates and actuals — [step 1](step-1-releases.md) | Free |
| [GitHub](https://github.com/diykorey/fortuneteller) | `diykorey` | local git + `gh` auth | Code hosting, CI, issue tracker | Free |

## Expected later

Listed so the cost and signup burden are visible in advance, not to imply they are set up.

| Service | Needed for | Key required | Cost |
| --- | --- | --- | --- |
| Stooq or yfinance | Daily price history — [step 2](roadmap.md) | No | Free |
| BLS | Cross-checking release dates against the official schedule | Optional | Free |
| An economic calendar | Historical **consensus**, if step 4 uses market expectations | Yes | Usually paid — the open question in the roadmap |

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
