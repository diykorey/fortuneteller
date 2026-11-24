# Sources by country, and each country's financial news

> Surveyed 2026-11-24, after the countries of steps 50 to 54 were added, at the owner's request:
> other useful free sources for each country's releases, and each country's top financial news,
> with the feeds that answer. Every endpoint was fetched that day; *not checked* marks one that was
> not. It adds to [Data sources](data-sources.md) and [Free sources](free-sources.md) and repeats
> neither. Nothing here is built; each source is a candidate, to be taken up by a roadmap step.
> Terms are in the [Glossary](glossary.md).

## What it means for the project

- **Release times to the minute, from official sources, for the past:** the UK's ONS release
  calendar (2016 on, open licence), Statistics Canada's data service (a `releaseTime` on every
  value, the first for series never revised, such as CPI), China's NBS yearly calendars (2015 on),
  the Fed Board's calendar file (2017 on) and BEA's file. For the ECB, the SNB, the Bank of Japan
  and ZEW only the coming year is published, so it must be saved each year.
- **A trap:** the ECB's and the SNB's rate series are dated when a rate takes effect, not the
  decision day; decision days come from the meeting calendars.
- **Actual figures:** free from every statistics office and central bank surveyed. Eurostat keeps
  only the latest revision, so a first print must come from elsewhere (not checked where). The Bank of Japan asks to be told before a public service uses its API.
- **Expected values (consensus):** no free source that may be republished, in any country. The
  only new free expected value is the Atlanta Fed's GDPNow, kept with every update's date.
- **News:** working feeds for the top outlets of every country but China (Caixin and Xinhua have
  none; SCMP covers China in English), and for most central banks and statistics offices. Every
  outlet's feed is for personal use: headlines may be read to find events (step 20), not
  republished. **GDELT** is the one source for many countries at once whose terms allow reuse with
  a citation.
- **Polymarket** (asked about the same day): already graded in [Data sources](data-sources.md) as
  the one free expected value for a Fed decision, with a short history; its API did not answer from
  here on 2026-11-24.

## Part A. The United States, and sources for many countries

Checked 2026-11-24 with `curl` from one machine in Europe (Linux, browser user agent) and, where
curl was blocked, a second fetcher. "200" means it answered with the data shown, today.
"Not checked" means no request got through; the claim comes from the source's own docs or a
search result. What `docs/free-sources.md` and `docs/data-sources.md` already cover (FRED,
ALFRED, the Cleveland nowcast, Philadelphia Fed SPF and real-time data, the WEI, Indeed, ECB,
CBOE, Stooq, the paid calendars, Kalshi, Polymarket) is not repeated. Where those surveys only
name a source (BLS, BEA, Census, EIA, Treasury, CFTC), this note adds the endpoint, the release
times, history and terms.

Terms in short: **US federal agencies** (BLS, BEA, Census, EIA, Treasury, CFTC, the Fed Board)
publish in the public domain; republishing numbers is allowed, citing the source is asked.
**News outlets** allow their RSS for personal, non-commercial reading only; storing headlines as
timestamps for our own measuring is a grey zone, and republishing headline text is not allowed.

### Part 1. US data the surveys miss

| Source | What it gives | Endpoint | Key | History | Release time | Terms | Status | Grade |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **Fed Board calendar JSON** | Every Board event with date and ET time: FOMC statements, minutes, pressers; Stat releases (H.4.1, G.17, Z.1...); speeches; testimony; Beige Book | `https://www.federalreserve.gov/json/calendar.json` | none | 2017-01 to 2026-12, 2,618 rows | each row has `time` ("2:00 p.m.") | public domain, cite the Board ([disclaimer](https://www.federalreserve.gov/disclaimer.htm)); endpoint undocumented | 200 | **useful**: FOMC and speech times with no scraping; undocumented, so cache it |
| **Fed Board RSS** | One feed per kind: `press_monetary.xml` (FOMC statements), `speeches.xml`, `testimony.xml`, `s_t_powell.xml` and one per governor, `h41.xml`, `h10.xml`, `g17.xml`... ([list](https://www.federalreserve.gov/feeds/feeds.htm)) | `https://www.federalreserve.gov/feeds/press_monetary.xml` | none | last 15 items | as published | public domain | 200 | **useful**: a live trigger for unscheduled Fed statements and speeches |
| **BLS release calendar (ICS)** | Every BLS news release with ET time (CPI, jobs, PPI, JOLTS, ECI...) | `https://www.bls.gov/schedule/news_release/bls.ics` | none | 2025-01-03 to 2026-12-30 (read via WebFetch) | 8:30 or 10:00 ET in the file | public domain | 403 to curl here (bls.gov blocks this IP/agent); 200 via WebFetch | **useful**: release times as data; fetch needs a user agent bls.gov accepts |
| **BLS API v2** | Any BLS series, latest values (not vintages) | `https://api.bls.gov/publicAPI/v2/timeseries/data/<id>` | none (answered without one); a free key raises limits | per BLS docs, 10 years (no key) / 20 years (key) per call, not checked | n/a | public domain | 200 (CPI-U Oct 2026 = 337.511) | **could be useful** if a series is missing from FRED; FRED already carries it, and BLS gives no first prints |
| **BEA release calendar (ICS)** | GDP, PCE / personal income, trade, with UTC times | `https://www.bea.gov/news/schedule/ics/online-calendar-subscription.ics` | none | 338 events, 2025-01-07 to 2027-12-22 | e.g. `DTSTART 20250130T133000Z` (8:30 ET) | public domain | 200 | **useful**: two years ahead, machine-readable times |
| **BEA API** | NIPA tables, regional, international | `https://apps.bea.gov/api/data?UserID=<key>&method=GETDATASETLIST` | free UserID ([signup](https://apps.bea.gov/API/signup/)) | full NIPA history (latest vintage) | n/a | public domain | 200 (JSON) | **could be useful** for PCE detail FRED lacks; no first prints |
| **Census indicator calendar** | Retail sales, durable goods, housing starts, trade, construction | `https://www.census.gov/economic-indicators/calendar-listview.html` (also `calendar-listview-2026.html`) | none | per year | 8:30 for advance indicators, 10:00 for others (per search) | public domain | 403 to curl and WebFetch: **not checked** | **could be useful** if census.gov lets us in; no ICS found |
| **Census EITS API** | The same indicators as time series | `https://api.census.gov/data/timeseries/eits` | free key for volume | not checked | n/a | public domain | 403: **not checked** | **could be useful**; FRED carries the headline series |
| **OMB PFEI schedule** | One PDF: release dates of all principal federal indicators for the year (BLS, BEA, Census, Fed, USDA, EIA) | `https://www.whitehouse.gov/wp-content/uploads/2026/10/FY2027-PFEI.pdf` | none | one year a file | dates (times not checked) | public domain | 200 | **could be useful**: the official cross-check of 2027 dates; a PDF, so parse once a year |
| **TreasuryDirect auctions API** | Every auction: high yield, bid-to-cover, dealer and indirect take, announcement and close dates | `https://www.treasurydirect.gov/TA_WS/securities/auctioned?format=json`; upcoming: `.../securities/upcoming?format=json` | none | not checked how far | results ~1:00 pm ET close + minutes (close time in data) | public domain | 200 (today's rows, 2026-11-23 auction) | **could be useful**: auctions as events for the 10-year; a surprise needs the when-issued yield, which is not free |
| **FiscalData auctions_query** | Same auctions, cleaner fields incl. `closing_time_comp` | `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query` | none | from 1979-10-31, 11,154 rows | close time "01:00 PM" ET | public domain | 200; lags TreasuryDirect (latest 10-year with results 2026-08-12) | **could be useful**: the history; TreasuryDirect for the latest |
| **EIA weekly petroleum (API v2)** | Weekly crude, gasoline, distillate stocks | `https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key=<key>&frequency=weekly` | free key (`DEMO_KEY` answered) | from 1983 | Wed 10:30 ET | public domain, cite "Source: EIA" ([terms](https://www.eia.gov/about/copyrights_reuse.php)) | 200 | **could be useful** if oil or gasoline markets join; no free consensus |
| **EIA WPSR schedule** | The Wednesday 10:30 rule and each holiday shift (2026 pairs listed include Jan 16/22, Feb 13/19, May 22/28, Sep 4/10) | `https://www.eia.gov/petroleum/supply/weekly/schedule.php` | none | current year | 10:30 ET Wed, exceptions listed | public domain | 200 (HTML) | **useful with the above**: the only source of exception dates; `ir.eia.gov/wpsr/wpsrsummary.pdf` gave 403 |
| **EIA natural gas storage** | Weekly storage report | `https://ir.eia.gov/ngs/ngs.html` | none | via API from 1994 (not checked) | Thu 10:30 ET | public domain | 200 | **could be useful** if natural gas is added |
| **CFTC Commitments of Traders (Socrata)** | Weekly positions by trader type, every futures market | `https://publicreporting.cftc.gov/resource/6dca-aqww.json` (legacy, futures only) | none (app token raises limits) | from 1986-01-15 | Fri 3:30 pm ET, Tuesday data ([schedule](https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm)) | public domain | 200 (2026-11-17 rows) | **could be useful** as a condition (positioning) in a later rung; not an event |
| **Atlanta Fed GDPNow** | Every GDPNow estimate through each quarter, and a file of the data-release dates it uses | `https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/data/gdpnow/GDPTrackingModelDataAndForecasts.xlsx` (11 MB); `.../GDPNowcastDataReleaseDates.xlsx` | none | not checked | updated after major releases | terms page not found: **not checked**; reserve-bank content, cite it | 200 | **useful**: the expected value for GDP (the survey lists GDPNow via FRED; this file keeps each update's date) |
| **NY Fed Staff Nowcast** | Weekly GDP nowcast | page `https://www.newyorkfed.org/research/policy/nowcast` | none | real-time from 2016, back-cast from 2002 (per a NY Fed blog) | Fridays (not checked) | not checked | page 200; the download link is rendered by script, **not found** | **could be useful** as a second GDP expectation once the file URL is found; code on [GitHub](https://github.com/FRBNY-RG/New-York-Nowcast) |

### Part 2a. US financial and economic news feeds

All five are headline-only RSS (title, link, time, short summary). None is a licence to republish;
all are for personal, non-commercial use. Use them, if at all, as timestamps of when a story broke.

| Outlet | Feed URL | Today | Paywall | Terms on automated use | Grade |
| --- | --- | --- | --- | --- | --- |
| CNBC | `https://www.cnbc.com/id/100003114/device/rss/rss.html` (top news); economy: `https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258` | 200, 30 items, minutes old | free site | no CNBC RSS terms found; NBC sister feeds say personal, non-commercial, with attribution | **useful** for timestamps |
| MarketWatch / WSJ (Dow Jones) | `https://feeds.content.dowjones.io/public/rss/mw_topstories`; WSJ markets: `https://feeds.content.dowjones.io/public/rss/RSSMarketsMain` | 200, current. Old `feeds.a.dj.com` and `mw_realtimeheadlines` are stale (2025) | WSJ paywalled, MarketWatch partly | Dow Jones terms: personal, non-commercial; MarketWatch terms bar scraping headlines for another site and algorithmic use | **could be useful**, internal timestamps only |
| Bloomberg | `https://feeds.bloomberg.com/markets/news.rss`, `https://feeds.bloomberg.com/economics/news.rss` | 200, 20 items, current | hard paywall on articles | [ToS](https://www.bloomberg.com/notices/tos/) has no RSS clause found; assume personal use | **could be useful**, headlines only |
| New York Times | `https://rss.nytimes.com/services/xml/rss/nyt/Economy.xml`, `.../Business.xml` | 200, current | metered paywall | ToS (Jan 2026): personal, non-commercial; RSS is a "Service"; bars use for software/AI without consent | **could be useful**; slower, not market-wire |
| Financial Times | `https://www.ft.com/rss/home`, `https://www.ft.com/global-economy?format=rss` | 200, 10 items | hard paywall | not checked; assume personal use | **could be useful**, UK/global angle |

Also responding: Investing.com `https://www.investing.com/rss/news_14.rss` (200, economy news),
Seeking Alpha `https://seekingalpha.com/market_currents.xml` (200), Economist
`https://www.economist.com/finance-and-economics/rss.xml` (200, weekly), NPR economy
`https://feeds.npr.org/1017/rss.xml` (200). Yahoo Finance headline RSS: 404 / 429 today.
**Reuters** has had no public RSS since June 2020 (`feeds.reuters.com` does not resolve;
`reuters.com` returns 401 to scripts). **AP** (`apnews.com/hub/business.rss`) returns 403; no
official free feed found. Both are reachable only through Google News or GDELT (below).

### Part 2b. Multi-country sources

| Source | What it gives | URL | Key / limits | Terms | Status | Grade |
| --- | --- | --- | --- | --- | --- | --- |
| **GDELT DOC 2.0 API** | Article lists (URL, title, time seen, domain, language, source country) and volume/tone timelines for any query, 65 languages; filters `sourcecountry:`, `sourcelang:`, `domain:`, `theme:` | `https://api.gdeltproject.org/api/v2/doc/doc?query=...&mode=artlist&format=json` (modes `timelinevolraw`, `timelinetone`, `tonechart`...) | no key; **one request per 5 s**, enforced (we hit it); max 250 articles a call; default window 3 months, back to 2017 per GDELT's blog (2019 test was rate-limited: not checked) | "unlimited and unrestricted use ... commercial" and republishing allowed, **must cite GDELT and link gdeltproject.org** ([about](https://www.gdeltproject.org/about.html)) | 200 (US Fed articles from today) | **useful**: the one free, reusable, many-country news index; links point to paywalled outlets, titles only |
| **GDELT 2.0 event / GKG files** | Every 15 minutes: coded events (who did what to whom, where), mentions, and the GKG (themes, tone, places per article) | `http://data.gdeltproject.org/gdeltv2/lastupdate.txt` lists the newest zips; masterfile lists all since 2015 | no key | same as above | 200 (14:00 UTC file today) | **could be useful** for unscheduled-event detection (rung 7); heavy and noisy |
| **GDELT Context 2.0** | Sentence-level matches with snippet | `https://api.gdeltproject.org/api/v2/context/context?query=...&format=json` | same limits | same | 200 (but returned an off-topic hit) | **could be useful** |
| **BIS central bankers' speeches** | Speeches of ~all central banks, one feed, with date, bank, speaker, summary | `https://www.bis.org/doclist/cbspeeches.rss` | none | BIS terms: free non-commercial redistribution; limited extracts with citation ([terms](https://www.bis.org/terms_conditions.htm)) | 200, 51 items, newest 2026-11-19 | **useful** as a list of speech dates; posted days late, so not a live trigger |
| BIS press releases | BIS's own press | `https://www.bis.org/doclist/all_pressrels.rss` | none | same | 200 | **useless** here (BIS itself does not move markets) |
| Central-bank RSS, direct | ECB `https://www.ecb.europa.eu/rss/press.html` (200); Bank of England `https://www.bankofengland.co.uk/rss/news` (200); IMF `https://www.imf.org/en/News/RSS` (403) | none | per bank; ECB and BoE reuse with source | 200 / 403 | **useful** as live triggers for ECB/BoE (the BIS feed is too late) |
| **Google News RSS** | Search or topic feeds per language/country: `https://news.google.com/rss/search?q=<query>[+when:1d][+site:reuters.com]&hl=<lang>&gl=<CC>&ceid=<CC>:<lang>`; topic: `.../rss/headlines/section/topic/BUSINESS?hl=..&gl=..&ceid=..` | none; returned **429** after a few calls | Google News terms: personal, non-commercial; no automated copying (legacy terms page) | 200 for search (US, GB), 200 for DE business topic, 429 for US topic | **could be useful** as a way to see Reuters/AP headlines and other countries' news; terms forbid robots, so internal and light only |
| NewsAPI.org | Headlines by country/category from many outlets | `https://newsapi.org/v2/top-headlines` | free Developer key: development only, not production; 100 requests/day and 24 h delay (per secondary sources) | [pricing](https://newsapi.org/pricing) | 401 without key | **useless**: dev-only and delayed |
| Marketaux | Financial news with tickers and entity sentiment, many countries | `https://api.marketaux.com/v1/news/all` | free key: 100 requests/day, 3 articles a request ([pricing](https://marketaux.com/pricing)) | not checked | 401 without key | **could be useful** for tagging stories to markets; tiny free tier |
| Finnhub market news | General, forex, crypto, merger news | `https://finnhub.io/api/v1/news?category=general` | free key | not checked | 401 without key | **could be useful**, not checked |
| Alpha Vantage NEWS_SENTIMENT | News with ticker and sentiment scores | `https://www.alphavantage.co/query?function=NEWS_SENTIMENT` | free key (`demo` key refused); 25 calls/day per the survey | not checked | 200 (asks for a key) | **could be useful**, tiny tier |

### The short of it

- Release **times** as data, free and official: the Fed's `calendar.json`, BLS's ICS and BEA's
  ICS; EIA's schedule page for its holiday shifts; CFTC's schedule page. Census has no file found
  and blocked us.
- New expected values: GDPNow's own file with every update; the NY Fed nowcast if its file is found.
- For news, GDELT is the only free source whose terms let us store and republish; outlet RSS
  feeds are usable for internal timestamps at most; the BIS speeches feed lists every central
  bank's speeches but late.

## Part B. The euro area, Germany, France, the UK and Switzerland

Checked 2026-11-24 with plain HTTP (curl). "Verified" = the URL answered 200 with the stated content type,
and where noted the body was read. "Not checked" = not fetched, or fetched without confirming the claim.
Times written as "(not checked)" come from memory, not from a page read today.

### Main findings first

1. **Past release minutes, machine readable, verified:**
   - **ONS release-calendar API** (UK): every release with a UTC timestamp, from about Feb 2016 (a 2009 query returned nothing).
     June-2025 CPI shows `2025-07-16T06:00:00.000Z`, which is 07:00 BST, so the Z timestamps are real UTC.
   - **BFS DAM API `embargo` field** (Switzerland): UTC embargo per published asset, e.g. CPI `2026-11-03T07:30:00Z`
     (08:30 CET); `2020-04-02T06:30:00Z` (08:30 CEST). Only 4 CPI assets came back (2020, 2021, 2026), so it is thin.
   - **SNB iCal 2026 and 2027** (Switzerland): `TZID=Europe/Zurich` minutes, e.g. policy assessment press release
     `20260319T093000`. Future and current year only, no archive.
   - **ZEW** page: "released ... at 11:05 a.m. Frankfurt Time" for the 2026 dates. That page covers 2026 only.
2. **RSS `pubDate` is when the item was posted, not the release minute.** Example: ifo's November 2026 business
   climate item has `pubDate 10:30 +0100`. Destatis items show 08:00 +0100. Usable only as a rough check.
3. **Policy-rate series give the date the rate takes effect, not the decision day:**
   - ECB `FM/B.U2.EUR.4F.KR.MRR_FR.LEV` ("date of changes") shows 2025-06-11, a Wednesday. The decision was the Thursday before.
   - SNB cube `snbgwdzid`, series `LZ`, shows 2025-06-20, a Friday. The decision was Thursday 19 June 2025.
   - BoE `IUDBEDR` shows 08 May 2025 and 07 Aug 2025, both Thursdays, so it does match the decision day.
     It was checked on these two rows only.
   - So ECB and SNB decision dates must come from their calendars and press-release archives, not from the rate series.
4. **Consensus forecasts: no free source found that may be republished.** Official sources publish actuals only.
   ForexFactory's weekly JSON has forecasts, but its terms forbid redistribution (see below).
   The ECB Survey of Professional Forecasters is quarterly: it is not a forecast for each release.

### Part 1: data sources

Grades: **U** = useful, **C** = could be useful (on the stated condition), **X** = useless for this project.

#### Euro area (ECB, HICP)

| Source | What it gives | Endpoint | Key | History | Times? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| ECB Data Portal API | All ECB series (SDMX), CSV/JSON | `https://data-api.ecb.europa.eu/service/data/FM/B.U2.EUR.4F.KR.MRR_FR.LEV?format=csvdata` (verified, CSV, from 1999-01-01); HICP `.../ICP/M.U2.N.000000.4.ANR?format=csvdata` (verified) | No | 1999 on | No; the rate series is dated by when the rate takes effect | ECB disclaimer (verified): free use, must appear accurately, ECB cited as source; if resold, buyers must be told it is free from ECB | **U** for actuals and rate levels. Not for decision dates. |
| ECB Governing Council meeting calendar | Meeting dates, "Day 2, followed by press conference" | `https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html` (verified, HTML) | No | Upcoming only | No time on the page | as above | **U** for dates; HTML scrape |
| ECB monetary policy decisions archive | Decision press releases | `https://www.ecb.europa.eu/press/govcdec/mopo/html/index.en.html` (verified 200) | No | 1999 on (not checked) | Not seen on page; time of the decision release (not checked) | as above | **C**: decision dates, if the times come from elsewhere |
| ECB press RSS | Press releases and speeches with minute `pubDate` (+0100) | `https://www.ecb.europa.eu/rss/press.html` (verified, 15 items); statistical press releases `https://www.ecb.europa.eu/rss/statpress.html` (verified) | No | About 15 latest items only | Posting time only | as above | **C**: live trigger, not history |
| ECB Survey of Professional Forecasters | Quarterly panel forecasts (HICP, GDP, unemployment) | Page `https://www.ecb.europa.eu/stats/ecb_surveys/survey_of_professional_forecasters/html/index.en.html` (verified); dataflow `https://data-api.ecb.europa.eu/service/dataflow/ECB/SPF` (verified 200); my guessed series key returned 404, so the key is not checked | No | 1999 on (not checked) | n/a | ECB terms | **C**: an expectation, but quarterly and not per release |
| Eurostat dissemination API | HICP flash and final, GDP, unemployment, trade; JSON-stat and SDMX-CSV | `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/prc_hicp_manr?geo=EA&coicop=CP00&lastTimePeriod=2` (verified JSON); `https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/prc_hicp_manr/M.RCH_A.CP00.EA?startPeriod=2015-01&format=SDMX-CSV` (verified) | No | 1990s on | No; latest values only, so the first print is lost after revisions | CC BY 4.0, cite the source and mark changes (copyright page verified) | **U** for actuals |
| Eurostat release calendar | Euro-indicator release dates | `https://ec.europa.eu/eurostat/news/release-calendar` (verified 200, filled in by script; iCal export not checked) | No | Not checked | Release time (not checked) | CC BY 4.0 | **C**: if the script's data call or an iCal export is found |
| Eurostat dataset-update RSS | Dataset update notices | `https://ec.europa.eu/eurostat/api/dissemination/catalogue/rss/en/statistics-update.rss` (verified XML) | No | Recent only | Posting time | CC BY 4.0 | **C**: as a "data changed" signal only |

#### Germany (CPI, ZEW, ifo, elections)

| Source | What it gives | Endpoint | Key | History | Times? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| Destatis GENESIS-Online API | CPI (table 61111-0002) and all federal statistics | `https://genesis.destatis.de/genesisWS/rest/2020/data/tablefile` (POST). The old `www-genesis` host redirects here; guest login GAST was refused with "Code 15: not allowed" | **Yes**: free registration (token not tried) | 1991 on (not checked) | No | Data licence Germany, attribution, version 2.0 (legal notice verified) | **C**: with a free account |
| Bundesbank time-series API | German CPI (`BBDP1/M.DE.N.VPI.C.A00000.I20.A`, verified, 2026-10 = 126.5), FX, yields; SDMX/CSV | `https://api.statistiken.bundesbank.de/rest/data/...` (verified). `api.bundesbank.de` did not answer. | No | Long (not checked per series) | No | Not checked | **U** for CPI actuals without registration |
| Destatis press-release dates | Upcoming release dates | `https://www.destatis.de/EN/Press/Dates/_node.html` (verified 200, content not parsed) | No | Upcoming | Not parsed | dl-de/by-2-0 | **C**: if the page lists times |
| Destatis press RSS (German only) | Press releases | `https://www.destatis.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/Aktuell.xml` (verified; items `pubDate 08:00 +0100`). The English counterpart returned 404. | No | Recent | Posting time | dl-de/by-2-0 | **C**: live trigger |
| ZEW Indicator of Economic Sentiment | 2026 release dates, time 11:05 Frankfurt | `https://www.zew.de/en/zew/news/2026-release-dates-for-zew-indicator-of-economic-sentiment-fixed` (verified, text read); survey page `https://www.zew.de/en/research-at-zew/zew-financial-market-survey` (verified; no data download found) | No | Dates: 2026 only. Values: no free history found | **Yes** for 2026 (11:05) | Not checked | **C**: dates and time yes; history of the figures not found free |
| ifo Business Climate | Time-series xlsx files | `https://www.ifo.de/en/ifo-time-series` (verified) links `/sites/default/files/2020-01/ifo_Business_Survey_Historical_TimeSeries.xlsx` (path is from 2020, may be stale, not opened) and `https://www.ifo.de/sites/default/files/facts/vintage/Germany-ifo-vintage.xlsx` (verified, xlsx, 273 KB) | No | Long (not checked) | No | Not checked | **U** if the vintage file holds first releases (not checked) |
| ifo press RSS | Press releases, **German titles even on the /en/ path** | `https://www.ifo.de/en/rss.xml` redirects to `https://www.ifo.de/en/pressemitteilungen/rss.xml` (verified) | No | Recent | `pubDate` 10:30 +0100 for the climate release, which is the posting time, not the release minute | Not checked | **C**: live trigger only |
| Federal Returning Officer (Bundeswahlleiterin) | Bundestag results, open-data CSV | `https://www.bundeswahlleiterin.de/bundestagswahlen/2025/ergebnisse/opendata.html` (verified 200) | No | Older elections on the site (not checked) | Poll-closing time (not checked) | Not checked | **U** for election results |

#### France (CPI, business climate, elections)

| Source | What it gives | Endpoint | Key | History | Times? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| INSEE BDM SDMX | Any INSEE series; CPI series `001759970` returns observations from 1990-01, each with a `DATE_JO` attribute (an official-journal publication date, not the release minute) | `https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001759970` (verified XML) | No | 1990 on | Date only (DATE_JO, meaning not confirmed) | Not checked (INSEE terms page returned 404) | **U** for actuals |
| INSEE Melodi API | New-style datasets, e.g. `DS_IPC_PRINC` (CPI) as JSON | `https://api.insee.fr/melodi/data/DS_IPC_PRINC?maxResult=2` (verified JSON) | No | Back to 2012 seen in the sample | No | Not checked | **U** for actuals |
| INSEE release agenda | "Agenda de diffusion des indicateurs économiques" | `https://www.insee.fr/fr/information/1405540` (verified title; content filled in by script, not parsed); English list of calendars `https://www.insee.fr/en/information/2107811` (verified) | No | Upcoming | Release time (not checked) | Not checked | **C**: if the script's data source is found |
| Banque de France Webstat API | Opendatasoft catalogue, 42,804 datasets | `https://webstat.banque-france.fr/api/explore/v2.1/catalog/datasets?limit=1` (verified JSON; key need for data not checked) | Not checked | Long (not checked) | No | Not checked | **C**: for French business surveys, if keyless |
| Interior Ministry results | Election results site | `https://www.resultats-elections.interieur.gouv.fr/` (verified 200) | No | Not checked | No | Not checked | **C**: HTML |
| data.gouv.fr API | Open datasets incl. election results | `https://www.data.gouv.fr/api/1/datasets/?q=elections%20legislatives` (verified JSON) | No | Many past elections (not checked) | No | Usually Licence Ouverte (Etalab page verified); per-dataset licence not checked | **U** for election results |
| INSEE RSS | `https://www.insee.fr/fr/flux-rss` and `/en/rss` returned **500** | | | | | | **X** today |

#### United Kingdom (Bank of England, CPI, elections)

| Source | What it gives | Endpoint | Key | History | Times? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| ONS release-calendar API | Every ONS release with UTC timestamp, status (published/confirmed/cancelled), `date_changes` | `https://api.beta.ons.gov.uk/v1/search/releases?limit=100&fromDate=2025-07-15&toDate=2025-07-17` (verified; query text seems ignored; use date filters) | No | From about Feb 2016; nothing for 2009 | **Yes**, minute, UTC | OGL v3 (ONS licences page verified: free reuse incl. commercial, attribution) | **U**: the best release-time source found |
| ONS release-calendar RSS | Same, live | `https://www.ons.gov.uk/releasecalendar?rss` (verified; `pubDate 09:30:00 +0000`) | No | Recent | Yes (scheduled time) | OGL v3 | **U**: live trigger |
| ONS time series | CPI D7G7 etc. as JSON or CSV | `https://www.ons.gov.uk/economy/inflationandpriceindices/timeseries/d7g7/mm23/data` (verified JSON); CSV `https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/d7g7/mm23` (verified) | No | Decades | No | OGL v3 | **U** for actuals (latest vintage) |
| ONS dataset API | Versioned datasets (CPIH), so earlier vintages can be read | `https://api.beta.ons.gov.uk/v1/datasets/cpih01/editions/time-series/versions` (verified JSON) | No | Per version | Release date per version (not checked) | OGL v3 | **C**: for first-print values |
| BoE Interactive Database | Bank Rate `IUDBEDR` and others as CSV | `https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&Datefrom=01/Jan/2015&Dateto=now&SeriesCodes=IUDBEDR&CSVF=TN&UsingCodes=Y` (verified CSV) | No | Decades | No; dates match decision Thursdays in 2 rows checked | **Database: Open Government Licence** (legal page verified), except some third-party exchange-rate series. **Rest of the website: personal or internal non-commercial use only** | **U** |
| BoE MPC dates | 2026 and 2027 announcement dates | `https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates` (verified, text read; no time on page) | No | Upcoming | Time not on page | Website terms (non-commercial) | **U** for dates |
| BoE RSS | News; publications | `https://www.bankofengland.co.uk/rss/news`, `https://www.bankofengland.co.uk/rss/publications` (verified; `pubDate ... Z`) | No | Recent | Posting time | Website terms | **C**: live trigger |
| UK Parliament election results | General election results | `https://electionresults.parliament.uk/` (verified 200) | No | Not checked | No | Open Parliament Licence (not checked) | **C** |
| Commons Library / Electoral Commission | Election data | Both returned 403 to the script | | | | | **X** for automated use |

#### Switzerland (SNB, CPI)

| Source | What it gives | Endpoint | Key | History | Times? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| SNB data portal API | Cubes as CSV; `snbgwdzid` (SNB policy rate `LZ`, SARON etc., from 2004), `snboffzisa` | `https://data.snb.ch/api/cube/snbgwdzid/data/csv/en` (verified CSV; header `PublishingDate 2026-11-23 10:00`) | No | 2004 on for this cube | No; `LZ` change dates are effective dates (Fri 2025-06-20, not the Thu decision) | Not checked (terms page did not render text) | **U** for levels, not for decision dates |
| SNB iCal calendars | All SNB events with Zurich-time minutes | `https://www.snb.ch/public/ical/calendar/en/872f3023-70ea-42a9-8c27-524da3533fb7.ics` (2026, verified), `.../ac3d067c-1b93-475e-9d22-56045798603d.ics` (2027, verified); listed at `https://www.snb.ch/en/services-events/digital-services/rss-calendar-feeds` | No | Current and next year | **Yes**, e.g. 2026-03-19 09:30 press release | Not checked | **U** for scheduling; past years: archive the file yearly |
| SNB RSS | Press releases (`dc:date` UTC); monetary policy | `https://www.snb.ch/public/rss/en/pressrel` (verified; the old `/public/en/rss/pressrel` redirects there), `https://www.snb.ch/public/rss/en/mopo` (verified); others listed on the page above | No | Recent | Posting time | Not checked | **C**: live trigger |
| BFS (FSO) DAM API | Published files with an **`embargo` timestamp (UTC)** | `https://dam-api.bfs.admin.ch/hub/api/dam/assets?orderNr=cc-e-05.02.08` (verified; CPI table) | No | 4 CPI assets: 2020, 2021, 2026 | **Yes**, minute | opendata.swiss shows BFS CPI data under "terms_by" (open use, source must be given) | **C**: release minutes, but sparse; other order numbers not checked |
| BFS PXWeb API | Statistical tables (CPI among them) | `https://www.pxweb.bfs.admin.ch/api/v1/en/` (verified JSON list; CPI table id not checked) | No | Not checked | No | as above | **C** |
| BFS agenda and CPI page | Release dates | `https://www.bfs.admin.ch/bfs/en/home/news/agenda.html`, `https://www.bfs.admin.ch/bfs/en/home/statistics/prices/consumer-price-index.html` (verified 200; times not parsed) | No | Upcoming | Not parsed | as above | **C** |
| opendata.swiss CKAN | Catalogue with licence per dataset | `https://ckan.opendata.swiss/api/3/action/package_search?q=konsumentenpreise` (verified) | No | n/a | No | per dataset | **U** for licence lookup |
| BFS elections | National Council results | `https://www.bfs.admin.ch/bfs/en/home/statistics/politics/elections.html` (verified 200) | No | Not checked | No | as above | **C** |
| KOF Economic Barometer | Page verified 200: `https://www.kof.ethz.ch/en/forecasts-and-indicators/indicators/kof-economic-barometer.html`. Guessed data API `datenservice.kof.ethz.ch` did not answer | | | | | Not checked | **C**: download route not found |

#### Consensus forecasts (all countries)

| Source | Result | Grade |
|---|---|---|
| ForexFactory / faireconomy weekly JSON `https://nfs.faireconomy.media/ff_calendar_thisweek.json` | Verified: title, country, date with offset, forecast, previous; **this week only**. Terms (`https://www.forexfactory.com/notices`, read): "copying, republication or redistribution of FEED, in part or in whole, is explicitly prohibited". | **X** for the public repo; at most a private check |
| ECB SPF | Quarterly, euro area only (see above) | **C**: as a separate "experts expected" line, not per release |
| Official sources (all above) | None publishes a consensus | none |
| Apify "official release calendar" actors (search result only) | Third-party scrapers of the Eurostat/ECB/ONS calendars; not fetched | not checked |

### Part 2: financial news feeds

"Feed" = verified 200 with current items on 2026-11-24 (count and latest date seen). Terms on automated use:
**not checked for any outlet** unless stated. Paywall marks are from general knowledge (not checked) unless stated.
Headlines in the feeds are free in every case listed.

#### Euro area / pan-European

| Outlet | Feed URL | Lang | Paywall | Status |
|---|---|---|---|---|
| Euronews Business | `https://www.euronews.com/rss?level=vertical&name=business` | EN | No (not checked) | verified, 50 items |
| Financial Times, global economy | `https://www.ft.com/global-economy?format=rss` (also `https://www.ft.com/rss/home`) | EN | Yes, articles (not checked) | verified, 25 items |
| Politico Europe | `https://www.politico.eu/feed/` | EN | Partly | **403** |
| Reuters | no public RSS; `https://www.reuters.com/business/` returned **401** | EN | | failed |
| CNBC (feed id 19794221, section not checked) | `https://www.cnbc.com/id/19794221/device/rss/rss.html` | EN | No | verified 200 |

#### Germany

| Outlet | Feed URL | Lang | Paywall | Status |
|---|---|---|---|---|
| Handelsblatt, Finanzen | `https://www.handelsblatt.com/contentexport/feed/finanzen` (also `.../feed/schlagzeilen`) | DE | Yes (not checked) | verified, 20 items |
| FAZ Wirtschaft / Finanzen | `https://www.faz.net/rss/aktuell/wirtschaft/`, `https://www.faz.net/rss/aktuell/finanzen/` | DE | Partly, F+ (not checked) | verified, 50 items |
| tagesschau Wirtschaft (ARD) | `https://www.tagesschau.de/wirtschaft/index~rss2.xml` | DE | No | verified, 39 items |
| WirtschaftsWoche | `https://www.wiwo.de/contentexport/feed/rss/schlagzeilen` | DE | Yes (not checked) | verified, 20 items |
| Süddeutsche Wirtschaft / Spiegel Wirtschaft / manager magazin | `https://rss.sueddeutsche.de/rss/Wirtschaft`, `https://www.spiegel.de/wirtschaft/index.rss`, `https://www.manager-magazin.de/finanzen/index.rss` | DE | Partly | verified 200 |
| Deutsche Welle Business | `https://rss.dw.com/xml/rss-en-bus` | EN | No | verified, 20 items |
| Bundesbank | `https://www.bundesbank.de/service/rss/en/633306/feed.rss` ("Latest") | EN | No | verified |
| Destatis | `https://www.destatis.de/SiteGlobals/Functions/RSSFeed/DE/RSSNewsfeed/Aktuell.xml` | DE only | No | verified |
| ifo | `https://www.ifo.de/en/pressemitteilungen/rss.xml` | DE titles | No | verified |
| ZEW | `https://www.zew.de/en/rss` returned 404; no feed found | | | failed |

#### France

| Outlet | Feed URL | Lang | Paywall | Status |
|---|---|---|---|---|
| Les Echos | `https://www.lesechos.fr/rss/rss_une.xml`, `https://services.lesechos.fr/rss/les-echos-finance-marches.xml` | FR | Yes | **403** (both user agents) |
| Le Figaro Économie | `https://www.lefigaro.fr/rss/figaro_economie.xml` | FR | Partly | verified, 20 items |
| Le Monde Économie | `https://www.lemonde.fr/economie/rss_full.xml` | FR | Partly | verified, 20 items |
| La Tribune | `https://www.latribune.fr/feed.xml` | FR | Partly | verified, 20 items |
| BFM Économie | `https://www.bfmtv.com/rss/economie/` | FR | No | verified, 30 items |
| France 24 Business | `https://www.france24.com/en/business/rss` | EN | No | verified, 30 items |
| L'Express Économie | `https://www.lexpress.fr/arc/outboundfeeds/rss/economie.xml` | FR | Partly | verified 200 |
| Boursorama | `https://www.boursorama.com/rss/actualites/economie` | FR | | **404** |
| INSEE | RSS returned 500 | | | failed |
| Banque de France | `https://www.banque-france.fr/fr/rss` returned 404; no feed found | | | failed |

#### United Kingdom

| Outlet | Feed URL | Lang | Paywall | Status |
|---|---|---|---|---|
| BBC Business | `https://feeds.bbci.co.uk/news/business/rss.xml` | EN | No | verified, 58 items |
| The Guardian Economics / Business | `https://www.theguardian.com/business/economics/rss`, `https://www.theguardian.com/business/rss` | EN | No | **403 with a browser user agent, 200 with a feed-reader user agent**. The Guardian content API needs a free key (`api-key=test` gave 401) |
| Financial Times | see euro area | EN | Yes | verified |
| City AM | `https://www.cityam.com/feed/` | EN | No | verified, 30 items |
| The Telegraph Business | `https://www.telegraph.co.uk/business/rss.xml` | EN | Yes, many articles (not checked) | verified, 120 items |
| This is Money / Independent Business | `https://www.thisismoney.co.uk/money/index.rss`, `https://www.independent.co.uk/news/business/rss` | EN | No | verified 200 |
| Bank of England | `https://www.bankofengland.co.uk/rss/news`, `.../rss/publications` | EN | No | verified |
| ONS | `https://www.ons.gov.uk/releasecalendar?rss` (releases) | EN | No | verified |

#### Switzerland

| Outlet | Feed URL | Lang | Paywall | Status |
|---|---|---|---|---|
| NZZ Wirtschaft / Finanzen | `https://www.nzz.ch/wirtschaft.rss`, `https://www.nzz.ch/finanzen.rss` | DE | Yes, metered (not checked) | verified, 32 items |
| SRF Wirtschaft | `https://www.srf.ch/news/bnf/rss/1926` | DE | No | verified, 60 items |
| finews.ch / finews.com | `https://www.finews.ch/news?format=feed&type=rss`, `https://www.finews.com/news/english-news?format=feed&type=rss` | DE / EN | No | verified, 19 items (EN) |
| Le Temps Économie | `https://www.letemps.ch/economie.rss` | FR | Yes, partly (not checked) | verified, 21 items |
| Swissinfo | `https://www.swissinfo.ch/eng/business/rss` and `/eng/rss` | EN | | **410 Gone** |
| Handelszeitung | `/rss.xml`, `/rss` | DE | | **404** |
| cash.ch | `https://www.cash.ch/rss` returns an HTML page, not RSS | DE | | failed |
| Finanz und Wirtschaft | `https://www.fuw.ch/feed` redirects (302), not followed to a feed | DE | Yes | not checked |
| SNB | `https://www.snb.ch/public/rss/en/pressrel`, `/public/rss/en/mopo` (+ others on the rss-calendar-feeds page) | EN/DE/FR | No | verified |
| BFS | `https://www.bfs.admin.ch/bfs/en/home/news/whats-new.rss` 404; no RSS link on the press page | | | failed |

### Release times known only from memory (not checked today; verify before use)

ECB decision press release 14:15 CET (13:45 before a change in about 2022; date of the change not checked);
Eurostat euro indicators 11:00 CET; Destatis CPI flash usually 14:00 CET; ifo 10:00 CET; INSEE CPI 08:45 CET;
BoE MPC 12:00 UK time; SNB assessment 09:30 Zurich (confirmed for 2026 by the iCal); BFS CPI 08:30 Zurich
(confirmed by the DAM embargo stamps).

## Part C. Japan, China and Canada

"Verified" means the URL was fetched on 2026-11-24 from a European IP and answered as described.
"Not checked" means nobody fetched it or read it. Grades: **useful**, **could be useful (on what
condition)**, **useless**.

### Headline findings

1. **No free source gives consensus forecasts with republishing rights** for any of the three
   countries. The only free machine-readable forecast found is the Forex Factory weekly JSON
   (current week only; its terms page returned 403). JCER's ESP survey covers longer-range
   forecasts, not a consensus figure per release. This fits the project's decision to drop
   third-party consensus figures.
2. **Statistics Canada's WDS gives a release time for each data point** (`releaseTime`), which is
   the best result in this survey. One caveat: for revised series it holds the time of the *last
   revision*, not of the first release (details below).
3. **Some events have no scheduled minute**: BoJ policy decisions (published when the meeting
   ends), PBoC rate and reserve-ratio moves, and China customs trade data (times vary). None of
   them has an official archive of past release times.
4. **China access**: `data.stats.gov.cn` returns `403 Forbidden ... reason:UrlACL` from this IP,
   which looks like an IP or region block. `www.customs.gov.cn` timed out. `www.stats.gov.cn`,
   `www.pbc.gov.cn` and `www.chinamoney.com.cn` answered.

---

### Part 1. Data sources

#### Canada

| Source | What it gives | Endpoint | Key | History | Release time? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| Bank of Canada Valet API | Policy rate target (series `V39079`), Bank Rate (`V122530`), FX, CORRA, ~all BoC series as JSON/CSV | `https://www.bankofcanada.ca/valet/observations/V39079/json?recent=3` (verified) | No | V39079 starts 2009-04-21 (verified) | No, daily values only | bankofcanada.ca/terms (verified): reproduce with attribution; paid redistribution needs a notice; third-party content excluded | **useful**: actual decision outcome, 17 years |
| BoC "upcoming events" page | Announcement dates with time "09:45 (ET)"; 2026 and 2027 schedule | `https://www.bankofcanada.ca/press/upcoming-events/` (verified); 2026/2027 dates also on `https://www.bankofcanada.ca/core-functions/monetary-policy/key-interest-rate/` (verified) | No | Upcoming only | Yes, 09:45 ET | As above | **useful**: the time comes from the source itself. Whether the time was always 09:45 ET is not checked; read older press releases for that |
| BoC press-release RSS | Rate announcements and other releases, with timestamps | `https://www.bankofcanada.ca/content_type/press-releases/feed/` (verified, 11 items) | No | ~10 latest | Yes, pubDate | As above | **useful** for live triggers. `.../content_type/interest-rate-announcement/feed/` answers but held no items |
| StatCan Web Data Service (WDS) | Every table. CPI vector `41690973` (all-items NSA), LFS unemployment rate `2062815` (table 14-10-0287) | `POST https://www150.statcan.gc.ca/t1/wds/rest/getDataFromVectorsAndLatestNPeriods` body `[{"vectorId":41690973,"latestN":200}]` (verified); `getAllCubesListLite` (verified) | No | latestN=200 returned 200 points back to 2010-03; full depth not checked (fetch by reference period to get more) | **Yes, per data point**: `releaseTime` e.g. `2026-11-16T08:30`. For CPI it gives original times (2010 points show `07:00`, which looks like the old 07:00 release slot). For LFS, 2010 points show `2025-01-24T08:30`, the date of a revision. Reliable only for series that are never revised | Statistics Canada Open Licence (verified): worldwide, royalty-free; use, reproduce, publish, sell; attribution required | **useful**: actual figure and minute in one call. For revised series, take original times from The Daily archive or the calendar |
| StatCan release calendar | Upcoming releases with times | `https://www150.statcan.gc.ca/n1/dai-quo/cal2-eng.htm` (verified, HTML) | No | Upcoming | Yes | Open Licence | **useful** for scheduling |
| The Daily Atom feed | Every release, timestamped | `https://www150.statcan.gc.ca/n1/rss/dai-quo/0-eng.atom` (verified, 305 entries, newest `2026-11-23T08:30:00-05:00`) | No | ~300 latest | Yes | Open Licence | **useful** for live triggers |

#### Japan

| Source | What it gives | Endpoint | Key | History | Release time? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| BoJ Time-Series Data Search API | All BoJ statistics, including the Tankan. Example: large-manufacturer business conditions DI `TK99F1000601GCQ01000` | `https://www.stat-search.boj.or.jp/api/v1/getDataCode?format=json&lang=en&db=CO&code=TK99F1000601GCQ01000` (verified) | No | Tankan DI from 1974Q2 (verified) | No (only `LAST_UPDATE` date) | API notice (`https://www.stat-search.boj.or.jp/info/api_notice_en.pdf`, verified): **you must email BoJ (post.rsd17@boj.or.jp) before releasing a service that uses the API and show a set credit line**; no heavy load | **useful** for Tankan actuals and the policy rate. The email-notice duty matters for a public repo |
| BoJ release schedule | Each release with date **and time**, e.g. "Dec. 14, 8:50 Tankan (Dec.): Summary"; MPM dates | `https://www.boj.or.jp/en/about/calendar/index.htm` (verified, updated Fridays) | No | Upcoming weeks | Yes (Tankan 08:50 JST). The MPM decision has no time | BoJ site terms not found (guessed URL 404); not checked | **useful** for Tankan; **useless** for the decision minute |
| BoJ MPM schedule | Meeting dates for 2026 and 2027; statements, minutes, Outlook Report | `https://www.boj.or.jp/en/mopo/mpmsche_minu/index.htm` (verified) | No | Past years linked | Only for minutes and Summary of Opinions (08:50) and the full Outlook Report (14:00). The statement comes out "immediately after" the meeting, with no set minute | Not checked | **could be useful**: gives dates. Past decision minutes need another source (e.g. the RSS pubDate, kept from now on) |
| BoJ "what's new" RSS (EN / JA) | Every BoJ release, with time | `https://www.boj.or.jp/en/rss/whatsnew.xml`, `https://www.boj.or.jp/rss/whatsnew.xml` (both verified; 41 EN items) | No | ~40 latest | Yes, e.g. `Tue, 24 Nov 2026 08:50:00 +0900` | Not checked | **useful** for live triggers and for logging the decision minute from now on |
| e-Stat API (Statistics Bureau and other ministries) | CPI (national and Tokyo), labour, all official statistics | `https://api.e-stat.go.jp/rest/3.0/app/json/getStatsList?appId=...` (verified: answers, says the appId is invalid) | **Yes**, free appId after registration | Long (CPI tables go back decades; exact depth not checked) | No | e-Stat terms (verified): Government of Japan Standard Terms of Use, compatible with CC BY 4.0, commercial use allowed, numbers not copyrighted | **useful** once the appId is registered |
| Statistics Bureau CPI release schedule | CPI release dates (national and Tokyo) | `https://www.stat.go.jp/english/data/cpi/1582.html` (verified) | No | Current year | **No time on the page.** 08:30 JST appears only on third-party calendars; the Japanese-language page was not checked | As e-Stat | **useful** for dates; the time needs a second source |
| e-Stat release calendar | Release calendar for all ministries | `https://www.e-stat.go.jp/en/release-calendar` (verified, HTML) | No | Not checked | Not checked | As e-Stat | **could be useful** if it lists times (not checked) |
| ESRI (Cabinet Office) GDP | Quarterly GDP releases | `https://www.esri.cao.go.jp/en/sna/sokuhou/sokuhou_top.html` (verified, HTML) | No | Not checked | Not checked | Not checked | **could be useful** if GDP is added |
| JCER ESP Forecast | Monthly survey of ~35 forecasters (GDP, CPI, ...) | `https://www.jcer.or.jp/en/esp-forecast-top` (verified) | No | Not checked | n/a | Not checked | **could be useful** as context only. It is not a consensus figure per release |

#### China

| Source | What it gives | Endpoint | Key | History | Release time? | Reuse terms | Grade |
|---|---|---|---|---|---|---|---|
| NBS regular release calendars, 2015-2026 | For each year, the release date **and time** of CPI/PPI (09:30), PMI (09:30), industrial output/retail/FAI (10:00), GDP | Index `https://www.stats.gov.cn/english/PressRelease/ReleaseCalendar/` (verified); 2026 `.../ReleaseCalendar/202512/t20251226_1962154.html` (verified) | No | 12 yearly calendars (2015-2026) | Yes (scheduled, not actual) | NBS terms at `https://www.stats.gov.cn/english/nbs/200701/t20070104_59236.html`: page answered but the text was not read; not checked | **useful**: scheduled minutes for 10+ years, as an HTML table to parse once |
| NBS English "Latest Releases" RSS | Every NBS release with time | `https://www.stats.gov.cn/english/PressRelease/rss.xml` (verified, ~470 items, newest `2026-11-24 09:30:00`) | No | Several months | Yes, Beijing time | Not checked | **useful** for live triggers and as a check of the actual minute |
| NBS data portal (data.stats.gov.cn) | Monthly and quarterly series: CPI, PMI, industrial output | `https://data.stats.gov.cn/english/easyquery.htm?cn=A01` | No | Long | No | Not checked | **could be useful only from an allowed IP**: answered **403 (WAF `UrlACL`)** from here |
| DBnomics (mirror) | Mirrors NBS, BOJ, BOC, STATCAN, STATJP, ESRI | `https://api.db.nomics.world/v22/providers` (verified on the second try; the first timed out) | No | Varies | No | Each original source's terms apply | **could be useful** as a way around the NBS block, if the NBS series are kept current. Freshness and series paths not checked (a guessed NBS series path returned 404) |
| China Foreign Exchange Trade System (chinamoney) LPR | Latest 1Y/5Y Loan Prime Rate, time-stamped | `https://www.chinamoney.com.cn/r/cms/www/chinamoney/data/currency/bk-lpr.json` (verified: `"showDateEN":"20/11/2026 9:00"`, 1Y 3.00, 5Y 3.50); page `https://www.chinamoney.com.cn/english/bmklpr/` (verified) | No | Latest only; history endpoint not checked | Yes, 09:00 on the 20th | Not checked | **useful** for live LPR. History needs another source |
| PBoC English site | Press releases, MPC, statistical releases | `https://www.pbc.gov.cn/en/3688110/3688172/index.html` (verified, list built by JavaScript) | No | Years linked | No set minute for rate or reserve-ratio moves | Not checked | **could be useful** for dates of unscheduled moves; parsing is fragile. No RSS found (`/rss/index.xml` 404) |
| China customs (GACC) | Monthly trade | `http://english.customs.gov.cn/` (verified); `https://www.customs.gov.cn/` timed out | No | Not checked | No fixed published minute; press reports cite ~10:00 or later and say the time varies | Not checked | **could be useful** for actuals; the time must be logged live |

#### Consensus forecasts (all three countries)

| Source | What it gives | Endpoint | Terms | Grade |
|---|---|---|---|---|
| Forex Factory calendar export (faireconomy mirror) | Current week only: title, country, time with zone, impact, **forecast**, previous (e.g. "Tokyo Core CPI y/y 2026-11-26T18:30-05:00 forecast 3.0%") | `https://nfs.faireconomy.media/ff_calendar_thisweek.json`, `.xml` (both verified) | forexfactory.com returned 403; terms not checked. Third-party consensus, same republishing problem as TradingView | **could be useful** only for private, unpublished use and kept week by week; no history |
| Official consensus | None exists at the statistics offices or central banks | - | - | - |

---

### Part 2. News feeds

Each outlet's terms on automated use: **not checked for any outlet**. Most publishers allow RSS
for personal reading and limit republishing; read each one's terms before use.

#### Japan

| Outlet | Language | Feed | Status | Paywall |
|---|---|---|---|---|
| Nikkei Asia | EN | `https://asia.nikkei.com/rss/feed/nar` | verified, 51 items, current | Metered paywall on articles |
| Nikkei (nikkei.com) | JA | no official feed found (`https://www.nikkei.com/rss/` 404). `https://assets.wor.jp/rss/rdf/nikkei/news.rdf` works (31 items, current) but is an **unofficial third-party re-feed**, not Nikkei's | - | Paywall |
| Japan Times | EN | `https://www.japantimes.co.jp/feed/` | verified, 30 items (business sub-feed 403) | Metered |
| NHK News, economy | JA | `https://www3.nhk.or.jp/rss/news/cat5.xml` | answers but **stale**: newest item 5 Aug 2026, lastBuildDate 9 Aug 2026 | Free |
| Asahi Shimbun, economy | JA | `https://www.asahi.com/rss/asahi/business.rdf` | verified, 22 items, current (served as text/html but is RDF) | Partly paywalled |
| Toyo Keizai | JA | `https://toyokeizai.net/list/feed/rss` | verified, 20 items | Mostly free |
| Jiji Press | JA | `https://www.jiji.com/rss/ranking.rdf` | verified, 11 items (most-read ranking, not all news) | Free headlines |
| Reuters Japan | JA | none (site 401 to scripts) | - | - |
| **BoJ** | EN/JA | `https://www.boj.or.jp/en/rss/whatsnew.xml`, `https://www.boj.or.jp/rss/whatsnew.xml` | verified | Free |
| **Statistics Bureau / e-Stat** | - | no feed found (guess `e-stat.go.jp/rss/new_release_ja.xml` 404) | - | - |

#### China

| Outlet | Language | Feed | Status | Paywall |
|---|---|---|---|---|
| Caixin / Caixin Global | ZH / EN | none found (`caixinglobal.com/rss/` 403, `/feed/` 404; `caixin.com/rss/` is an HTML page with no feed links) | - | Paywall |
| South China Morning Post | EN | Business `https://www.scmp.com/rss/92/feed`; China `https://www.scmp.com/rss/4/feed` | verified, 50 items each, current | Metered |
| Xinhua English | EN | `http://www.xinhuanet.com/english/rss/businessrss.xml`, `chinarss.xml` (listed on `https://english.news.cn/rss/`) | answer but **dead**: newest items from 2017 | Free |
| Global Times | EN | `https://www.globaltimes.cn/rss/outbrain.xml` | answers; ad-partner feed, newest item 9 Oct 2026 | Free |
| China Daily | EN | guessed feeds 404 | none found | Free |
| Yicai, China Securities Journal, Securities Times | ZH | no feed found (Yicai `/rss/` 404, cs.com.cn 403, stcn.com timed out) | - | Mostly free |
| **NBS** | EN | `https://www.stats.gov.cn/english/PressRelease/rss.xml` (official, listed on the NBS RSS page) | verified | Free |
| **PBoC** | - | none found | - | - |

#### Canada

| Outlet | Language | Feed | Status | Paywall |
|---|---|---|---|---|
| Globe and Mail | EN | Business `https://www.theglobeandmail.com/arc/outboundfeeds/rss/category/business/`; Economy `.../category/business/economy/` | verified (12 and 3 items), current | Paywall |
| Financial Post | EN | `https://financialpost.com/feed/` returns HTML, so no feed | none | Metered |
| CBC News, business | EN | `https://www.cbc.ca/webfeed/rss/rss-business` | verified, 20 items | Free |
| BNN Bloomberg | EN | `https://www.bnnbloomberg.ca/arc/outboundfeeds/rss/category/business/?outputType=xml` | verified, 3 items, current | Free |
| Radio-Canada, economy | FR | `https://ici.radio-canada.ca/rss/5717` | verified, 50 items | Free |
| La Presse, Affaires | FR | `https://www.lapresse.ca/affaires/rss` | verified, 10 items | Free |
| Le Devoir, Économie | FR | `https://www.ledevoir.com/rss/section/economie.xml` | verified, 10 items | Partly paywalled |
| **Bank of Canada** | EN | `https://www.bankofcanada.ca/content_type/press-releases/feed/` | verified | Free |
| **Statistics Canada** | EN | `https://www150.statcan.gc.ca/n1/rss/dai-quo/0-eng.atom` | verified | Free |

---

### What fits the project's needs best

- **Canada** is fully covered by official sources: the Valet API (decision outcome), BoC events
  page and RSS (09:45 ET), WDS (actual figure plus release minute; original minute only for
  series that are never revised, such as NSA CPI) and the Open Licence.
- **Japan**: BoJ API for the Tankan (email-notice duty), BoJ schedule for the 08:50 time, e-Stat
  (free appId) for CPI. The CPI 08:30 time is not on the official English page. There is no
  archive of BoJ decision minutes; start logging the RSS pubDate.
- **China**: NBS yearly calendars give the scheduled minutes from 2015, and the NBS RSS gives the
  actual minute live. Actual figures come from the NBS portal (blocked from here), so try DBnomics
  or the release text. LPR is at 09:00 on the 20th (latest value only). The PBoC and customs have
  no fixed minute.
