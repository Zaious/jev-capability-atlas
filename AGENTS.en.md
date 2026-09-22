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

Yes → a candidate. No (needs an external knowledge base, needs comparison against an entire field, or is pure fact recall with no supporting passage given) → not a candidate, don't force it — see the real third-party case [Hubei news classification](translations/libukai-hubei-news-classification-zh/) (it's weaker than a large model on background connections the article never states). It doesn't necessarily not know — it answered the obscure history question in [`suites/history-recall-context/`](suites/history-recall-context/) with no passage — but you can't tell in advance, so it still isn't a candidate unless you put the facts in `state` first.

### When the candidate signal isn't text to begin with (image/audio/sensor), ask this first

**Has the system already computed this signal internally, just without exposing it?** Usually the answer is yes — some internal algorithm or data structure already derived that signal, it just was never surfaced as text. Checking for and exposing that existing computation is close to free, and its fidelity is structurally higher than re-deriving it by bolting on a new "perception" model:

- Both real integrations in [`browser-automation.md`](browser-automation.md) read the browser's own existing DOM instead of taking a screenshot — not because a vision model can't read the screen, but because the browser system had already turned screen state into structured data.
- [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/) failed at default settings because the state only showed Jev a length placeholder — the content was right there, just never exposed, not genuinely unreachable.
- The two failing categories in [`suites/icu-alarm-classification/`](suites/icu-alarm-classification/) come down to us crudely re-deriving waveform features from scratch, worse than the algorithms the monitor's own internals already run.

**Only when no existing system has ever computed that signal at all** (a camera judging whether real-world fruit is ripe, whether a wall has a structural crack) does a separate perception/conversion model become genuinely necessary — there, it's a required step, not a shortcut for insufficient logging. Work out which case your candidate is before deciding whether to wire one in.

Real examples almost all convert to text first and then hand it to Jev: [jev-drone](https://github.com/RomanSlack/jev-drone) turns the onboard camera feed into a symbolic depth-plus-segmentation scene before Jev judges it; [GUI JEV](https://github.com/ZihuaEvan/GUI_JEV) has a separate vision model describe each tile of a screenshot, and Jev only chooses among the descriptions; [jev-canvas](https://github.com/gaborishka/jev-canvas) tracks a finger with MediaPipe and transcribes speech before asking Jev anything. Jev itself currently accepts text only 📖. There are Jev-shaped open variants that read pixels directly, but so far they're specialists or unverified — see [`jev-variants.en.md`](jev-variants.en.md#variants-that-read-images-directly).

### Official hard limits: know these before you scan

From [TypeSafe's Models page](https://docs.typesafe.ai/models) 📖 — check each candidate against these first; some drop out right here:

- **Text only**: the state must be a string, a JSON object, or an array of text values. No images, audio or video.
- **Length**: 64k tokens per request; the state plus the single longest question can be at most 32k tokens. Beyond that, chunk or summarize first — it isn't a candidate as-is.
- **No fine-tuning**: every account shares the same weights; you steer it only through state, instructions and criteria. "Just train it on our data" isn't an option; if you need fine-tuning, see the open variants in [`jev-variants.en.md`](jev-variants.en.md).
- **Languages**: English is best; other languages (including CJK) are officially less accurate, so validate on your own data. We measured 0.93 on Traditional-Chinese intent classification 🔬 ([`suites/laya-head-to-head/`](suites/laya-head-to-head/)), but that's one task, not yours.
- **Price and rate limits**: $0.042 per million input tokens, output free; rate limits are officially described as adjusting dynamically.

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
- **Using Jev to decide whether to delete an agent's own past execution history (tool calls/results)** — this isn't "answer a judgment," it's "make a potentially irreversible deletion decision," a different kind of risk; a real case study is in [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/). At minimum, before considering it: ① the state used for scoring must include the actual output content, not just a length placeholder — otherwise it's judging blind (see [issue #26](https://github.com/tamaratran/fast-jev-compaction/issues/26): zero of 256 real tool results scored above 0.3 to keep); ② failed commands, not-yet-superseded computed results, and any output where re-running isn't guaranteed to reproduce the same answer should be protected by a rule, not left to a probability threshold (see [issue #25](https://github.com/tamaratran/fast-jev-compaction/issues/25)'s "relevance ≠ reproducibility"); ③ if cache cost matters, keep the rewritten prefix as close to byte-identical as possible instead of re-scoring on every request (see [issue #1, sticky reduction](https://github.com/jerryfane/omp-jev-compaction/issues/1)).
- **Predicting human behavior that hasn't happened yet** (will this message get opened/replied to/converted, will this prospect close) — there is no ground truth to check against at judgment time; it only exists once the real-world outcome plays out later. Bolting on a confidence score doesn't make the forecast trustworthy — TypeSafe's own docs say calibration has to be validated on your own data, and this class of task can't even be validated at judgment time, let alone beforehand. It's a more extreme version of "needs comparison against an entire field": the problem isn't that the data is missing from `state`, it's that **the answer doesn't exist yet**. A real case: a product founder (not an independent third party — the founder of the very service being pitched) claimed "predicted how 700 outreach messages would perform in 40 seconds" ([original tweet](https://x.com/romanbuildsaas)) — the claim's own verifiability is structurally broken. The same company's existing, non-Jev scoring feature has already been called out by an independent review as "scoring is opaque, you can't see the signal weighting" — attaching a Jev confidence score to an already-opaque prediction doesn't make it trustworthy. **An easy variant to fall into — we nearly did ourselves**: decomposing "predict the outcome" into "judge content properties that intuitively seem related to the outcome" (e.g. hook strength, format quality — general copywriting judgment — as a stand-in for "will the target platform's algorithm actually push this"). The properties themselves are self-contained and judgeable, fine — but **whether those properties actually correlate with the outcome you care about is a separate, entirely unvalidated assumption**. A general-purpose good-copy heuristic is not the same thing as a target system's real reward function (X's algorithm, for instance, weights specific actions like reply-from-author at 150x a like and retweet at 20x — not "emotional intensity"); nobody has measured that correlation, so one can't stand in for the other. This is the same underlying mistake as [`capability-map.md`](capability-map.en.md#the-cost-of-decomposing-a-judgment)'s "decomposition doesn't automatically inherit correctness," wearing a different face.

### The minimum verification flow for a candidate (copy our own process, don't skip it)

Once you've found a candidate, don't act on the checklist alone — verify:

1. Pull 10–20 **real** historical inputs/outputs from the existing system (not invented ones).
2. Write a minimal Choice/Score call and actually hit the live API against that real data (needs `TYPESAFE_API_KEY`; see the template in [`scripts/common/`](scripts/common/)). **Print the states you're about to send and proofread them, and store the exact state sent with each result** — Jev won't tell you the input is broken: we misspelled one character in a correct option of our own history question and it picked a wrong answer at 0.90 confidence ([`suites/history-recall-context/`](suites/history-recall-context/)). If the state is assembled from OCR, scraping or user input, upstream cleaning is part of this step too.
3. Compare side by side against the existing approach (regex/old classifier/old LLM call) — look at the disagreement rate and confidence distribution, not one nice-looking example. If you compare latency, exclude the first call: connection setup makes it 2–3× slower ([`suites/jev-latency-distribution/`](suites/jev-latency-distribution/)).
4. Only integrate once real data supports it, and **layer it as a second opinion first, not a replacement** — same as our own pilots: run it for a while before promoting it. On a latency-sensitive path, fire one warm-up call after the service starts.
5. Contribute the result — good or bad — back to [`suites/`](suites/). This is the entire reason this repo exists.

**If the candidate is browser automation** (clicking, filling forms, navigating), don't design the architecture from scratch — read [`browser-automation.en.md`](browser-automation.en.md): the reference architecture three real open-source implementations converged on (one call, three questions), how the typing problem gets solved, and a checklist for before you touch your own system.

**If you're about to suggest replacing Jev with a self-hosted open alternative** (Laya or another variant), read [`jev-variants.en.md`](jev-variants.en.md) and [`suites/laya-head-to-head/`](suites/laya-head-to-head/) first: today's open variants mostly trail Jev on new tasks asked directly, and nearly every win is on a distribution the variant was trained on. Before suggesting it, check whether the user has labelled data and whether the workflow is fixed.

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
2. Write `data/cases.json` + `run.py` following an existing suite (e.g. `suites/history-recall-context/`) as a template — import `scripts/common/jev_client.py` rather than reimplementing access logic; `run.py` should support `--dry-run` to print the states it would send, and the receipt should store each sent state — the history suite's typos slipped through because neither was done.
3. Actually run it, producing `runs/<date>.json`.
4. Fill in `README.md` (mirroring `suites/TEMPLATE/README.md`'s sections) and `protocol.yaml`.
5. If the README reports aggregate numbers (accuracy, sensitivity and the like), add a script that recomputes them from the receipts, with `--check` exiting 1 on a mismatch (as in [`suites/icu-alarm-classification/metrics.py`](suites/icu-alarm-classification/metrics.py)) — so the prose and the receipts can't quietly drift apart.
6. **Before reporting, self-check against the PR checklist in `CONTRIBUTING.md`** — especially "every number traces to a real log" and "every finding is tagged 🔬/📚/📖/💭." Finally, run `python scripts/zh-check/check_zh.py` to make sure no Simplified characters slipped in.

### Reporting results — a concrete protocol (the important part; don't just say "I ran it, looks good")

Two paths depending on what access you have:

**Agent with push/PR access:**
```bash
git checkout -b suite/<slug>
git add suites/<slug>/
git commit -m "suite: <slug> — <one-line finding, e.g. "cross-turn sarcasm 10/10">"
git push -u origin suite/<slug>
gh pr create --title "suite: <slug>" --body "<paste the README.md results summary + tag (🔬/📚/📖/💭) + runs/ filenames>"
```

**Agent with no push access, asked by a user to just run something:** don't summarize with a conclusion alone — give the user, itemized:
1. Which files were created (full paths)
2. The full contents of the suite's `README.md` (or `report.md` for an external-source entry), not a summary of it
3. Each case's `choice`/`confidence`/`probabilities` — not just right/wrong
4. Whether this is a 🔬 brand-new suite, a re-run of an existing one, or pure analysis
5. One line on what the user can do next (open a PR themselves, or ask you to)

**The floor that applies either way**: a result report **must** include the real `runs/*.json` content or its path — never a remembered "roughly 80% accurate." Same rule for agents as for human contributors — see `CONTRIBUTING.md`.
