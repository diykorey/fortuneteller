# Free sources of US economic statistics

> A survey of free sources that could feed the project, made 2026-11-21 at the owner's ask.
> Reference only: nothing here is planned until the [Roadmap](roadmap.md) names it, and each is
> added the way [Extending](extending.md) says, one flow or one expectation source per pull
> request. Terms and limits change; check each source's own page before building on it.

## What the search found

- **The research** measures surprises against survey consensus and finds markets jump with the
  surprise's size ([Andersen, Bollerslev, Diebold and Vega](https://www.nber.org/papers/w11312.pdf));
  a release's weight follows how much it says about GDP ([NBER w25016](https://www.nber.org/papers/w25016.pdf));
  responses to CPI surprises have grown stronger while others have not
  ([FEDS 2025-022](https://www.federalreserve.gov/econres/feds/files/2025022pap.pdf)).
- **No free consensus with history was found.** The calendars that keep it charge for it
  ([Trading Economics](https://tradingeconomics.com/api/calendar.aspx),
  [Benzinga](https://benzinga.com/apis/cloud-product/economic_calendar),
  [EODHD](https://eodhd.com/financial-academy/?p=7100)); a free calendar built on official
  sources [says so outright](https://apify.com/michael_b/economic-calendar-fed-watch). The free
  forecasts of the Federal Reserve banks are the nearest thing.

## 1. Free forecasts: an expected value besides the consensus

| Source | What it gives | Use here |
| --- | --- | --- |
| [Cleveland Fed inflation nowcast](https://www.clevelandfed.org/indicators-and-data/inflation-nowcasting) | A forecast of CPI and PCE each business day, from oil and gasoline prices | A second expected value for CPI and PCE, not from TradingView; its download format is unchecked |
| Atlanta Fed GDPNow ([via FRED](https://fred.stlouisfed.org/search?st=nowcast)) | GDP forecast, updated through the quarter | An expected value for GDP |
| [Philadelphia Fed Survey of Professional Forecasters](https://www.philadelphiafed.org/surveys-and-data/data-files) | Quarterly forecasts since 1968, mean, median and spread, Excel | A long history of expected values for GDP, jobs and inflation |
| [Philadelphia Fed Real-Time Data Set](https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/real-time-data-set-for-macroeconomists) | Each series as first published, before revisions | The actual as known on the day |
| [ALFRED](https://alfred.stlouisfed.org/release/downloaddates?rid=465) | Every past version of each FRED series, with release dates | The same, with the FRED key in use |

Not confirmed by the search: the New York Fed's Staff Nowcast and the Chicago Fed's retail-sales
forecast (CARTS).

## 2. The official releases

| Source | Access | Use here |
| --- | --- | --- |
| FRED | Free key, 800,000+ series | In use; carries BLS, BEA and Census series |
| BLS | Free API; daily limits [differ between guides](https://datasetiq.com/blog/api-access-economic-data-guide) | PPI and JOLTS as new releases |
| BEA | Free API, registration | GDP and PCE at their source |
| Census | Free API, registration | Durable goods, housing starts, trade as new releases |
| [EIA](https://www.eia.gov/opendata/) | Free key | The weekly oil inventories (Wednesday 10:30) as a weekly event for Brent and gasoline |
| [Treasury Fiscal Data](https://apis.io/apis/fiscaldata/fiscaldata-daily-treasury-statement-api/) | No key; JSON or CSV | Auction results and the daily cash statement; a weak auction as an event for yields |

## 3. Weekly and daily readings

| Source | Access | Use here |
| --- | --- | --- |
| [Weekly Economic Index](https://fred.stlouisfed.org/series/WEI/) | On FRED; now published [less often](https://www.dallasfed.org/research/wei) | Ten weekly series in one: sales, claims, fuel, steel, rail |
| [Indeed job postings](https://github.com/hiring-lab/job_postings_tracker) | GitHub, CC BY 4.0, daily, refreshed weekly | A job-market reading before the jobs report; Indeed's series on FRED [need permission](https://fred.stlouisfed.org/news/2023/02/fred-adds-indeed-index-data) |

## 4. Known, not checked in this survey

The University of Michigan's sentiment and its inflation expectations; the New York Fed's
consumer expectations survey and its supply-chain pressure index; the regional Fed factory
surveys (Empire State, Philadelphia, Richmond, Kansas City, Dallas); the Fed's weekly balance
sheet (H.4.1) and loan officer survey; the CFTC's Commitments of Traders; Freddie Mac's mortgage
rate; Zillow and Redfin; Kalshi's and Polymarket's prices (on the roadmap's *Later* list); Google
Trends; ADP payrolls and Challenger job cuts, if their history is free.

## The first two, after the gate

By the owner, 2026-11-21: the Cleveland Fed's nowcast as a second expected value for CPI and
PCE, then the Philadelphia Fed survey's history for GDP, each its own spec after the 2027-01-31
gate ([Roadmap](roadmap.md), *Later*).
