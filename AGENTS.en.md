🇹🇼 [中文](AGENTS.md)｜🇬🇧 English (this page)

# AGENTS.md — for an agent brought into a project to find where Jev could fit

You're here because someone wants to know if any part of an existing codebase is a good candidate for swapping a slow/expensive LLM call for TypeSafe's Jev (fast, cheap, but limited to narrow typed judgments). This is a checklist, not background reading — read the full [`capability-map.md`](capability-map.md) first, then scan.

## The one test

> **Is the correct answer for this judgment fully recoverable from the content you're already about to hand it, with no outside knowledge or field comparison needed?**

Yes → a candidate. No (needs an external knowledge base, needs comparison against an entire field, or is pure fact recall with no supporting passage given) → not a candidate, don't force it — see [`suites/history-recall-context/`](suites/history-recall-context/) for a real counter-example.

## What to grep for, ranked by signal strength

1. **An existing LLM call whose prompt asks for classification/rating/yes-no, and whose response is parsed down to a single label** — look for prompts with "classify," "categorize," "rate 1-10," "which of the following," followed by regex extraction or `if response ==` parsing where the free text itself is never used. Strongest signal: you're paying for a whole model's output and keeping only one narrow value.
2. **Hand-rolled regex/keyword classifiers with home-grown confidence heuristics** — function names like `classify_*`/`score_*`/`detect_*`/`triage_*`, comments or return values with "confidence: high/medium/low" labels assigned by hand. These are already faking calibration; swapping in a genuinely calibrated probability is a direct upgrade.
3. **High-frequency small decisions capped for cost/latency reasons** — comments like "only check the first N," "budget limit," next to a classification/routing decision. The cap usually exists because the current approach is too slow/expensive, not because the task doesn't need doing.
4. **Existing filters that literal/regex matching can't catch semantic-layer errors on** — e.g. lexical-overlap checks that miss "same words, opposite meaning" (see our own citation-check and sarcasm-detection suites).

## Where not to touch

- **Safety-critical, irreversible gates** (deletion, payment, sending, permission decisions) — this logic belongs in deterministic code, and no probabilistic model, however fast, should own the final call. This isn't about Jev specifically — it's the general principle that irreversible actions shouldn't be handed to any probabilistic output.
- **Anywhere that needs the model to explain its reasoning** — structurally impossible per TypeSafe's own docs: no text, no code, no explanation of reasoning.
- **Scoring that needs comparison against an entire field/market** (novelty, significance, "is this good") — unless you retrieve the comparison material first and put it in the state, the text alone has no answer.
- **Anywhere a working, zero-cost deterministic script already does the job well** — don't add a model where there's no failure to fix; this cuts both ways from the usual "fix on the second failure" discipline.

## The minimum verification flow for a candidate (copy our own process, don't skip it)

Once you've found a candidate, don't act on the checklist alone — verify:

1. Pull 10–20 **real** historical inputs/outputs from the existing system (not invented ones).
2. Write a minimal Choice/Score call and actually hit the live API against that real data (needs `TYPESAFE_API_KEY`; see the template in [`scripts/common/`](scripts/common/)).
3. Compare side by side against the existing approach (regex/old classifier/old LLM call) — look at the disagreement rate and confidence distribution, not one nice-looking example.
4. Only integrate once real data supports it, and **layer it as a second opinion first, not a replacement** — same as our own pilots: run it for a while before promoting it.
5. Contribute the result — good or bad — back to [`suites/`](suites/). This is the entire reason this repo exists.

## Where to find API mechanics

For how to call the API and design Choice/Score/Noul questions, read TypeSafe's own [skill](https://github.com/typesafe-ai/skills) — it's covered thoroughly there, we don't repeat it here.
