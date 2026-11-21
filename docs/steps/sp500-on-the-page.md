# The S&P 500 on the page

> Step 45 of the [Roadmap](../roadmap.md), the next part of [step 44](readers.md), for
> [step 23](be-seen.md)'s readers. Terms are in the [Glossary](../glossary.md): *cell*, *holds*,
> *the answers that hold*, *kind*. Chosen 2026-11-21 by the owner.

## The goal

**In plain words:** the page answers the three S&P 500 kinds already measured, and its reports
ahead name every S&P 500 company reporting in the next seven weekdays, not only the Dow's.

At the end *Ask* offers three more groups:
- S&P 500 earnings above, in line with or below the consensus ([step 36](earnings-sp500.md));
- a company announced as joining the S&P 500 ([step 35](sp500-additions.md));
- a stock split announced alone or with a report ([step 37](stock-splits.md)).

Each *group* (one kind of event's set of kinds, as *Ask*'s menu groups them) is marked with
the day the script measured it. *The answers that hold* gains those of them that
hold. The reports ahead list the S&P 500's members by day, under the three kinds' lines.

## The way to reach it

- **The obstacle: 38 minutes a run.** The earnings and split kinds need every member's closes,
  which only a copy of the store holds. `follows --event earnings500` took 38 minutes on it
  (step 36). The evening job cannot run that.
  - Additions' closes are loaded each evening, so that group could run live. It is frozen with
    the other two so that the three S&P 500 groups share one measured day; running it live is left
    for later.
- **Measured once, frozen.**
  - `scripts/ask_sp500.py` builds the three groups with the same function as every other group
    (`ask_entry`). It runs on the copy of the store step 40 used: the evening's store plus the
    closes of every company in step 36's earnings seed, to 2026-11-20.
  - It writes `data/seed/ask_sp500.json` with the day it is run, given on its command line.
  - The page reads that file and shows that day. It is measured again only by hand:
    the earnings seed is not refreshed for the S&P 500 (step 33 keeps the Dow's).
- **The reports ahead** take each company that is an S&P 500 member on the report's day, by
  `data/seed/sp500.csv`.
  - The three lines, one per kind, come from the S&P 500 earnings group's day cells against the
    index, from the close before. They are shown once, above the list, since they are the same for
    every company.
  - A Dow company reporting reads them too, as it is in the S&P 500 (`sp500.csv`). The Dow's own
    group stays in *Ask* and in *the answers that hold* as its own kind. Its in-line day holds
    where the S&P 500's does not, and the lines say *past S&P 500 reports*, so the two are told
    apart.
  - Under them, each weekday lists its companies, before the open, after the close or at a time
    not given.
  - This replaces step 44's per-company rows (*amended there, 2026-11-21*).
- **The weekly post** gives the three lines once, and names the five largest companies reporting
  in the week by Nasdaq's market value.

## The rule, fixed before measuring

- **The frozen groups agree with steps 36, 35 and 37.** These five cells, each with its answer,
  verdict and replay (right of graded):
  1. a miss's day: *down*, holds, 2,506 of 3,798;
  2. an in-line day: does not hold (step 36);
  3. a miss's week: does not hold (59.5%, step 36);
  4. a split announced alone, its day: *up*, holds, 33 of 51;
  5. an addition's day: *up*, does not hold, 30 of 53.

  The answers and verdicts must be the same. The counts may differ by the few reports whose
  closes the copy has and the earlier ones did not (step 36 had two 2026-11-18 reports with no
  reaction close). Any other difference is found and explained here before the page is published.
- **Expected outcome:** *the answers that hold* goes from seven to nine:
  - the S&P 500's miss on the day;
  - a split alone on the day.

  The reports ahead list 30 to 60 companies in the week of 2026-11-30, step 44's review week.
  That count is reported, not a bar.

## The steps

| # | Step | Done when |
| --- | --- | --- |
| 1 | The frozen file | `scripts/ask_sp500.py` written and run; the five cells above read from the file and written here beside the earlier steps' |
| 2 | The page reads it | A test with a stubbed file finds a group in *Ask* with its measured day, not left out, and its hold in the list |
| 3 | The reports ahead | Tests with a stubbed Nasdaq page cover a member listed, a non-member left out and a class share (`BRK/B` for `BRK-B`). The three kinds' cells are distinct, and a week cell that holds is not used. A test of the post gives six reports and finds the five with the largest `marketCap`, largest first, and the lines once |
| 4 | Published | The page written on the evening of 2026-11-30 lists that week's reports; their count is written here |

## How you know it is right

- The five cells in the rule agree with steps 36, 35 and 37, as the rule says.
- A test stubs each kind's cell differently, plus a week cell that holds, and finds each line from
  its own kind's day cell.

## What this step does not do

- No evening loading of the members' closes.
- No refresh of the S&P 500 earnings seed.
- No call before a report.
- No new kind.

## Technical details

- `ask_entry(name, noun, con, names)` builds one group from the store `con`, with the market
  names `names`. It is `ask_data`'s loop body, taken out so that the script uses the same code.
- `SP500_FLOWS` (`earnings500`, `additions`, `splits`) are skipped in that loop. The frozen file's
  groups are appended, each with a `measured` key.
- `earnings_ahead` becomes `{"lines": [...], "days": [{"day", "reports": [{symbol, name, time,
  cap}]}]}`, or null when the ask failed. `cap` is Nasdaq's `marketCap` (`$150,864,134,000`) read as dollars, 0 when blank.
- Docs: this spec, step 44's amendment, [scoreboard](scoreboard.md), status, the changelog and
  roadmap row 45.
