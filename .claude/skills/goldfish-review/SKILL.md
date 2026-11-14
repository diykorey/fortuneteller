---
name: goldfish-review
description: Review a FortuneTeller step spec with a fresh-context reviewer (the goldfish) before measuring or after results land, or zoom out over the whole plan once a month. Use when a spec's pull request is opened, when Results are added to a spec, for the monthly zoom-out, or when asked for a goldfish review.
---

# Goldfish review

The Legend's "How a step is reviewed" defines this. You are the elephant: you know too much to
review your own spec. So you do not review it; a fresh subagent does.

## Steps

1. **Pick the stage.** *Before measuring* if the spec has no Results section yet; *results* if it
   has one.
2. **Spawn one fresh subagent** (general-purpose), giving it only the paths below and the prompt
   for the stage. Do not summarise the spec, explain the background, or say what you expect: any
   of that defeats the review.
   - The spec: docs/steps/NAME.md
   - docs/legend.md, docs/glossary.md
   - Every document the spec links to or names (a spec it cites by name, such as "step 4's
     *tracks*", counts), which it may open itself
   - For the results stage, the spec's history: git log -p --follow docs/steps/NAME.md
3. **Act on each finding.** Fix the spec, or write in the pull request why the finding stands.
4. **Record one line in the pull request:** "Goldfish review (STAGE): N findings, M fixed."

## Prompt, before measuring

> You have never seen this project. Read docs/steps/NAME.md, then docs/legend.md and
> docs/glossary.md, and open any document the spec links to or names if you need it. Use nothing
> else, and change nothing.
> Answer, numbered:
> 1. The step's goal in one sentence.
> 2. The bars and the expected outcome, as numbers. If any is missing or vague, say so.
> 3. Each "done when" in The steps that you could not check without judgement, and why.
> 4. One plausible wrong answer the checks in "How you know it is right" would not catch.
> 5. Every term, number or claim you could not understand from these documents alone.
> Then list your findings, most serious first, each in one sentence with the section it is in.
> Say "none" where you found nothing; do not invent findings.

## Prompt, results

> You have never seen this project. Read docs/steps/NAME.md, then docs/legend.md and
> docs/glossary.md. Open any document the spec links to or names when you need a bar it refers to,
> and read the spec's history with git log -p --follow docs/steps/NAME.md to check dates. Use
> nothing else, and change nothing. Answer, numbered:
> 1. Is each verdict in Results judged against the rule fixed before measuring, with every number
>    its bar needs stated? Name any that is not.
> 2. Did any bar, test or expected outcome change without a dated amendment?
> 3. Does each plain-words summary say what its numbers say, no more and no less?
> 4. Does each number name the command that prints it?
> Then list your findings, most serious first, each in one sentence. Say "none" where you found
> nothing; do not invent findings.

## Prompt, the monthly zoom-out

> You have never seen this project. Read docs/legend.md, docs/roadmap.md, docs/status.md and
> docs/decisions.md. Use nothing else, and change nothing. Answer, numbered:
> 1. In two sentences, the target, and whether the work in progress and next serves it.
> 2. Which step's cost is out of line with what it could show, and why.
> 3. Is the latest gate in the roadmap on course, by the numbers the documents give? Name any bar
>    you cannot check from them.
> 4. What would you cut, if you were new and had to choose?
> Then list your findings, most serious first, each in one sentence. Say "none" where you found
> nothing; do not invent findings.

Record the findings in a decisions entry or a roadmap pull request.
