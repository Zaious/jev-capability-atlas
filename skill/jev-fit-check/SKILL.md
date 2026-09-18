---
name: jev-fit-check
license: MIT
description: >
  Scan a codebase for places where TypeSafe's Jev (a fast, cheap, calibrated
  typed-decision model) could replace or augment a slower/costlier LLM call
  or a hand-rolled heuristic classifier. Independent, evidence-based guidance
  from the Jev Capability Atlas project — not TypeSafe's own SDK skill (use
  that separately for API mechanics). Use when asked to find where an AI
  agent's codebase could adopt Jev, to evaluate whether a specific
  classification/routing/scoring task is a good fit for it, or to design a
  verification pilot before integrating it.
---

# Jev fit-check

**Before using this checklist, read `MECHANISM.md` in the
[Jev Capability Atlas](https://github.com/Zaious/jev-capability-atlas) repo.**
It explains why Jev is neither a state machine nor a blind guesser, and
neither a chain-of-thought reasoning model — a distinction you will likely
need to get right when reporting your conclusions to whoever asked you to
evaluate this. Don't simplify it yourself; point to that page or restate its
three negations.

This skill answers one question: **where in this codebase could Jev fit, and where shouldn't it?**
It does not cover how to call the API — read TypeSafe's own skill
(`typesafe-ai/skills`) for that. This skill is the independent, evidence-based
layer on top: the [Jev Capability Atlas](https://github.com/REPLACE_WITH_REPO_URL)
project's findings, condensed into a checklist.

## The one test

Is the correct answer for this judgment fully recoverable from the content
you're about to hand the model, with no outside knowledge or comparison
against a broader field needed? If yes, it's a candidate. If the task needs
an external knowledge base, comparison against an entire domain, or is pure
fact recall with no supporting passage supplied, it is not a candidate —
don't force it.

## What to grep for, ranked by signal strength

1. **An existing LLM call whose prompt asks for classification/rating/yes-no,
   whose response is parsed down to one label.** Look for prompts containing
   "classify," "categorize," "rate 1-10," "which of the following," followed
   by regex extraction or `if response == ...` parsing where the free text
   itself is never consumed downstream. This is the strongest signal: a whole
   model's output is being paid for and only one narrow value is kept.
2. **Hand-rolled regex/keyword classifiers with home-grown confidence
   heuristics.** Function names like `classify_*`/`score_*`/`detect_*`/
   `triage_*`, comments or return values with hand-assigned "confidence:
   high/medium/low" labels. These are already faking calibration; a real
   calibrated probability is a direct upgrade.
3. **High-frequency small decisions capped for cost/latency reasons.**
   Comments like "only check the first N," "budget limit," next to a
   classification/routing decision. The cap usually exists because the
   current approach is too slow or expensive, not because the task itself
   doesn't need doing at scale.
4. **Existing filters that literal/keyword matching can't catch
   semantic-layer errors on** — e.g. overlap checks that miss "same words,
   opposite meaning."

## Where not to touch

- **Safety-critical, irreversible gates** (deletion, payment, sending,
  permission checks) — keep these in deterministic code; no probabilistic
  model output, however fast, should own a final irreversible decision.
- **Anywhere the model needs to explain its reasoning** — structurally
  impossible for Jev: it returns typed answers and probabilities, never
  text, code, or an explanation.
- **Scoring that requires comparison against an entire field or market**
  (novelty, significance, "how good is this") — unless the comparison
  material is retrieved and included in the state first, the text alone
  has no answer to give.
- **Anywhere a working, zero-cost deterministic script already does the job
  well** — don't add a model where there is no demonstrated failure to fix.

## Minimum verification flow before integrating a candidate

1. Pull 10–20 real historical inputs/outputs from the existing system —
   not invented examples.
2. Write a minimal Choice/Score/Noul call and run it against that real data
   with a live `TYPESAFE_API_KEY`.
3. Compare side by side against the existing approach: disagreement rate and
   confidence distribution, not one favorable-looking example.
4. Only integrate once real data supports it, and add it as a second
   opinion first — not an outright replacement — until it has run for a
   while.
5. Consider contributing the result, positive or negative, back to the Jev
   Capability Atlas project's `suites/` directory.

## Contributing a result back

If you're working directly inside the Jev Capability Atlas repo (not just
using this skill from another project), the fuller workflow — running an
existing suite, adding a new one, and the exact protocol for reporting
results depending on whether you have push access — lives in that repo's
`AGENTS.md`, under "Mode B." This skill only covers Mode A (finding a fit in
someone else's codebase); read `AGENTS.md` directly for Mode B rather than
relying on this file, since it may drift out of sync.

## Known evidence (as of this skill's last update)

Self-contained classification and relation-judgment tasks (topic
classification, citation-support checking, sarcasm/irony detection even
across conversational turns) have performed strongly and at expected cost in
every test we've run or read about. Tasks needing outside knowledge (pure
trivia recall with no supporting passage, comparison against an entire
field, genuinely overlapping/ambiguous categories) have shown real, and in
one case dangerous, degradation — including a case where confidence stayed
high while accuracy collapsed. Treat any single number, including these, as
a starting point to verify on your own data, not a guarantee.
