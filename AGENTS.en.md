🇹🇼 [中文](AGENTS.md)｜🇬🇧 English (this page)

# AGENTS.md — for agents

**Read the "Not a state machine, not blind guessing" section of [`README.md`](README.md) before anything else.** Whichever mode you're in, you'll likely need to describe what Jev is to someone else (a user, a team) afterward — **don't compress it down to "state machine" or "guessing,"** and don't overcorrect into "it thinks" either; both are wrong, and that section explains why. This isn't optional background — it shapes the conclusions you draw and the words you use to report them.

Figure out which situation you're in first:
- Brought in to look at **another project**, assessing where Jev could fit → read "Mode A"
- Brought into **this repo itself**, to run existing suites, add a new one, or report results → read "Mode B"

---

## Mode A: assessing another codebase for Jev-fit

You're here because someone wants to know if any part of an existing codebase is a good candidate for swapping a slow/expensive LLM call for TypeSafe's Jev (fast, cheap, but limited to narrow typed judgments). This is a checklist, not background reading — read the full [`capability-map.en.md`](capability-map.en.md) (or the [Chinese original](capability-map.md)) first, then scan.

### The one test

> **Is the correct answer for this judgment fully recoverable from the content you're already about to hand it, with no outside knowledge or field comparison needed?**

Yes → a candidate. No (needs an external knowledge base, needs comparison against an entire field, or is pure fact recall with no supporting passage given) → not a candidate, don't force it — see [`suites/history-recall-context/`](suites/history-recall-context/) for a real counter-example.

### What to grep for, ranked by signal strength

1. **An existing LLM call whose prompt asks for classification/rating/yes-no, and whose response is parsed down to a single label** — look for prompts with "classify," "categorize," "rate 1-10," "which of the following," followed by regex extraction or `if response ==` parsing where the free text itself is never used. Strongest signal: you're paying for a whole model's output and keeping only one narrow value.
2. **Hand-rolled regex/keyword classifiers with home-grown confidence heuristics** — function names like `classify_*`/`score_*`/`detect_*`/`triage_*`, comments or return values with "confidence: high/medium/low" labels assigned by hand. These are already faking calibration; swapping in a genuinely calibrated probability is a direct upgrade.
3. **High-frequency small decisions capped for cost/latency reasons** — comments like "only check the first N," "budget limit," next to a classification/routing decision. The cap usually exists because the current approach is too slow/expensive, not because the task doesn't need doing.
4. **Existing filters that literal/regex matching can't catch semantic-layer errors on** — e.g. lexical-overlap checks that miss "same words, opposite meaning" (see our own citation-check and sarcasm-detection suites).

### Where not to touch

- **Safety-critical, irreversible gates** (deletion, payment, sending, permission decisions) — this logic belongs in deterministic code, and no probabilistic model, however fast, should own the final call. This isn't about Jev specifically — it's the general principle that irreversible actions shouldn't be handed to any probabilistic output.
- **Anywhere that needs the model to explain its reasoning** — structurally impossible per TypeSafe's own docs: no text, no code, no explanation of reasoning.
- **Scoring that needs comparison against an entire field/market** (novelty, significance, "is this good") — unless you retrieve the comparison material first and put it in the state, the text alone has no answer.
- **Anywhere a working, zero-cost deterministic script already does the job well** — don't add a model where there's no failure to fix; this cuts both ways from the usual "fix on the second failure" discipline.

### The minimum verification flow for a candidate (copy our own process, don't skip it)

Once you've found a candidate, don't act on the checklist alone — verify:

1. Pull 10–20 **real** historical inputs/outputs from the existing system (not invented ones).
2. Write a minimal Choice/Score call and actually hit the live API against that real data (needs `TYPESAFE_API_KEY`; see the template in [`scripts/common/`](scripts/common/)).
3. Compare side by side against the existing approach (regex/old classifier/old LLM call) — look at the disagreement rate and confidence distribution, not one nice-looking example.
4. Only integrate once real data supports it, and **layer it as a second opinion first, not a replacement** — same as our own pilots: run it for a while before promoting it.
5. Contribute the result — good or bad — back to [`suites/`](suites/). This is the entire reason this repo exists.

### Where to find API mechanics

For how to call the API and design Choice/Score/Noul questions, read TypeSafe's own [skill](https://github.com/typesafe-ai/skills) — it's covered thoroughly there, we don't repeat it here.

---

## Mode B: working inside this repo — running suites, adding suites, reporting results

### Setup

```bash
pip install "typesafe-sdk>=0.5.7" --extra-index-url https://pypi.typesafe.ai/
export TYPESAFE_API_KEY=<your key>          # early-access waitlist, see typesafe.ai
python scripts/common/jev_client.py         # self-check: zero cost, confirms the service is live (deliberately triggers a 401 with a bad key)
```

### Running an existing suite

```bash
python suites/<slug>/run.py
```

Every `run.py` makes real API calls and saves the responses to `suites/<slug>/runs/<date>.json`, printing results to the terminal too. **Never hand-edit files in `runs/`** — they're receipts; editing them defeats the point.

### Adding a new suite

1. `cp -r suites/TEMPLATE suites/<your-slug>`
2. Write `data/cases.json` + `run.py` following an existing suite (e.g. `suites/history-recall-context/`) as a template — import `scripts/common/jev_client.py` rather than reimplementing access logic.
3. Actually run it, producing `runs/<date>.json`.
4. Fill in `README.md` (mirroring `suites/TEMPLATE/README.md`'s sections) and `protocol.yaml`.
5. **Before reporting, self-check against the PR checklist in `CONTRIBUTING.md`** — especially "every number traces to a real log" and "every finding is tagged 🔬/📚/📖/💭."

### Reporting results — a concrete protocol (the important part; don't just say "I ran it, looks good")

Two paths depending on what access you have:

**Agent with push/PR access:**
```bash
git checkout -b suite/<slug>
git add suites/<slug>/
git commit -m "suite: <slug> — <one-line finding, e.g. "cross-turn sarcasm 10/10">"
git push -u origin suite/<slug>
gh pr create --title "suite: <slug>" --body "<paste report.md's summary + tag (🔬/📚/📖/💭) + runs/ filenames>"
```

**Agent with no push access, asked by a user to just run something:** don't summarize with a conclusion alone — give the user, itemized:
1. Which files were created (full paths)
2. The full contents of `report.md`, not a summary of it
3. Each case's `choice`/`confidence`/`probabilities` — not just right/wrong
4. Whether this is a 🔬 brand-new suite, a re-run of an existing one, or pure analysis
5. One line on what the user can do next (open a PR themselves, or ask you to)

**The floor that applies either way**: a result report **must** include the real `runs/*.json` content or its path — never a remembered "roughly 80% accurate." Same rule for agents as for human contributors — see `CONTRIBUTING.md`.
