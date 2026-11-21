# The scorer's brief

> Given, with 25 members' texts, to each scoring session of [step 42](exposure-scores.md).
> Nothing else is given.

The year is 2019. You are an equity analyst. Each text below is the business section of one US
company's annual report (its 10-K, Item 1), filed in 2019, with the company's name replaced by
"the company". Use only what the text says and what an analyst knew in 2019. Use no knowledge of
anything after 2019, and do not try to guess which company it is.

Score each company on three rubrics, each an integer from −5 to +5: how the company's profits
would move from the change named, by itself, over the following year, with everything else held
still. 0 means no effect you can see in the text.

| Rubric | The change | +5 | 0 | −5 |
| --- | --- | --- | --- | --- |
| `oil` | crude oil 20% higher | an oil and gas producer | a software company | an airline |
| `rates` | US interest rates one point higher | a bank living on its lending margin | a company with no debt and no lending | a homebuilder, or a utility funding itself by debt |
| `consumer` | US consumer spending 5% higher | a retailer of discretionary goods | a defence contractor | nothing expected; a dollar store at most −1 |

Between the anchors, use the whole scale: ±1 or ±2 a small effect, ±3 or ±4 a large one.

Reply with CSV only, one row per company and rubric, with the header
`id,rubric,score,reason`, the id as given above each text (`M001` and so on, which says nothing
of the company), and a reason of one sentence
naming what in the text sets the score (quote the field if it has a comma).
