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

### The state is what leaves the machine

Jev is a cloud API with no on-premise build — **every character you put in the `state` has left this machine**. When scanning candidates, alongside "is the answer in the state?", ask "is this content allowed to leave?". One third-party implementation works this through carefully and its layering is worth copying (📚 [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills), our write-up in [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)):

- **Redact what can be redacted, swap ids for placeholders**: mask emails, phone numbers, tokens and long hex; replace a retrieved passage's source id, path and filename with `P0`, `P1`… so the content goes and the provenance doesn't.
- **Decode before you screen, or the screen misses it**: a newsletter footer carries the recipient's address percent-encoded in the unsubscribe link and base64'd in the tracking link, and a plain-text redactor sees neither. Any "scan for secrets before sending" step must first unwrap quoted-printable, percent-encoding, HTML entities and base64.
- **Dropping the whole item beats redacting it**: a passage that looks like a credential, a turn that looks like it holds a secret — don't send it at all rather than trusting the redactor to be thorough.
- **On sensitive paths, send coarse features instead**: length, whether code is present, whether risk words appear. That is enough for a decision like routing, and the text never leaves the machine.
- **Notice what acts first**: if the decision happens before the agent does (model routing, for instance), then "tell the agent never to send customer data" does nothing — that turn's text was sent before the agent had any say.

### What to grep for, ranked by signal strength

1. **An existing LLM call whose prompt asks for classification/rating/yes-no, and whose response is parsed down to a single label** — look for prompts with "classify," "categorize," "rate 1-10," "which of the following," followed by regex extraction or `if response ==` parsing where the free text itself is never used. Strongest signal: you're paying for a whole model's output and keeping only one narrow value.
2. **Hand-rolled regex/keyword classifiers with home-grown confidence heuristics** — function names like `classify_*`/`score_*`/`detect_*`/`triage_*`, comments or return values with "confidence: high/medium/low" labels assigned by hand. These are already faking calibration; swapping in a genuinely calibrated probability is a direct upgrade.
3. **High-frequency small decisions capped for cost/latency reasons** — comments like "only check the first N," "budget limit," next to a classification/routing decision. The cap usually exists because the current approach is too slow/expensive, not because the task doesn't need doing.
4. **Existing filters that literal/regex matching can't catch semantic-layer errors on** — e.g. lexical-overlap checks that miss "same words, opposite meaning" (see our own citation-check and sarcasm-detection suites).

**After scanning for code patterns, check the techniques in [`jev-patterns.en.md`](jev-patterns.en.md)**: some candidates only show up once the question is rephrased — extraction as "choose among candidates," long-document lookup as "navigate one choice at a time," "do two things agree?," "ask the cheap question before the expensive one."

### Where not to touch

- **Safety-critical, irreversible gates** (deletion, payment, sending, permission decisions) — this logic belongs in deterministic code, and no probabilistic model, however fast, should own the final call. This isn't about Jev specifically — it's the general principle that irreversible actions shouldn't be handed to any probabilistic output.
- **Anywhere that needs the model to explain its reasoning** — structurally impossible per TypeSafe's own docs: no text, no code, no explanation of reasoning.
- **Scoring that needs comparison against an entire field/market** (novelty, significance, "is this good") — unless you retrieve the comparison material first and put it in the state, the text alone has no answer.
- **Anywhere a working, zero-cost deterministic script already does the job well** — don't add a model where there's no failure to fix; this cuts both ways from the usual "fix on the second failure" discipline.
- **Using Jev to decide whether to delete an agent's own past execution history (tool calls/results)** — this isn't "answer a judgment," it's "make a potentially irreversible deletion decision," a different kind of risk; a real case study is in [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/). At minimum, before considering it: ① the state used for scoring must include the actual output content, not just a length placeholder — otherwise it's judging blind (see [issue #26](https://github.com/tamaratran/fast-jev-compaction/issues/26): zero of 256 real tool results scored above 0.3 to keep); ② failed commands, not-yet-superseded computed results, and any output where re-running isn't guaranteed to reproduce the same answer should be protected by a rule, not left to a probability threshold (see [issue #25](https://github.com/tamaratran/fast-jev-compaction/issues/25)'s "relevance ≠ reproducibility"); ③ if cache cost matters, keep the rewritten prefix as close to byte-identical as possible instead of re-scoring on every request (see [issue #1, sticky reduction](https://github.com/jerryfane/omp-jev-compaction/issues/1)). **Stronger evidence, added 2026-09-23**: a third party measured this end to end and removed Jev. Seven real sessions, a 104-question recall exam: the capsule written from Jev's picks scored 37.5% against 48.1% for a plain tail (4 questions won, 15 lost), and what shipped afterwards uses no Jev. Its failure mode differs from all three points above: **the state was complete and Jev's judgement really did beat recency (11 questions to 4); what lost is the shape of the question** — a kept turn still survives only as its first 400 characters. The lesson: after rewriting a task into a shape Jev can answer, ask once more whether that shape can still do the original job. See [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/).
- **Predicting human behavior that hasn't happened yet** (will this message get opened/replied to/converted, will this prospect close) — there is no ground truth to check against at judgment time; it only exists once the real-world outcome plays out later. Bolting on a confidence score doesn't make the forecast trustworthy — TypeSafe's own docs say calibration has to be validated on your own data, and this class of task can't even be validated at judgment time, let alone beforehand. It's a more extreme version of "needs comparison against an entire field": the problem isn't that the data is missing from `state`, it's that **the answer doesn't exist yet**. A real case: a product founder (not an independent third party — the founder of the very service being pitched) claimed "predicted how 700 outreach messages would perform in 40 seconds" ([original tweet](https://x.com/romanbuildsaas)) — the claim's own verifiability is structurally broken. The same company's existing, non-Jev scoring feature has already been called out by an independent review as "scoring is opaque, you can't see the signal weighting" — attaching a Jev confidence score to an already-opaque prediction doesn't make it trustworthy. **An easy variant to fall into — we nearly did ourselves**: decomposing "predict the outcome" into "judge content properties that intuitively seem related to the outcome" (e.g. hook strength, format quality — general copywriting judgment — as a stand-in for "will the target platform's algorithm actually push this"). The properties themselves are self-contained and judgeable, fine — but **whether those properties actually correlate with the outcome you care about is a separate, entirely unvalidated assumption**. A general-purpose good-copy heuristic is not the same thing as a target system's real reward function (X's algorithm, for instance, weights specific actions like reply-from-author at 150x a like and retweet at 20x — not "emotional intensity"); nobody has measured that correlation, so one can't stand in for the other. This is the same underlying mistake as [`capability-map.md`](capability-map.en.md#the-cost-of-decomposing-a-judgment)'s "decomposition doesn't automatically inherit correctness," wearing a different face.

  **The flip side needs saying just as clearly: checking whether a piece of writing meets *defined* criteria is squarely Jev's territory.** Criteria like "does the first sentence give a concrete benefit" or "is the conclusion repeated," once each is defined in a sentence, have their answer in the text; asking dozens of them at once costs almost no time (97 more questions cost 24 ms, see [`translations/ha-jev-home-assistant-zh/`](translations/ha-jev-home-assistant-zh/)), and whether the definitions are written out makes a large difference (see "Writing the question" below). The line is **what you report**: "this post is missing these criteria" is fine; "this post's probability of going viral" is not. 💭 One more thing that's easy to blur: a backtest on content that **already has results** (pick which of two old posts performed better) has an answer to check and can yield a hit rate; but a backtest that works doesn't mean deployment will — the backtest measures how the criteria correlated with outcomes in the past, and once you use them to rewrite content, everything written to the criteria starts to look alike and the criteria stop separating good from bad.

### Writing the question: define it, compute first, separate requirement from preference

Jev scores the options you give it against the `state` you give it. Two third-party integrations measured, against the live API, how much the wording of a question matters (📚 both self-reported, not re-run by us; see [`translations/ha-jev-home-assistant-zh/`](translations/ha-jev-home-assistant-zh/) and [`translations/blakestone-jev-mcp-zh/`](translations/blakestone-jev-mcp-zh/)):

1. **Define the thing being judged.** Bare label names scored 64.5%; one sentence of definition per label, 81.0%; adding "not for" and examples reached only 84.5% at 2.8× the tokens (jev-mcp). Another integration wrote the definitions as structured objects and saw no difference on 15 ambiguous cases (HA-Jev). **Write one sentence of definition; add detail only to the pairs that get confused.**
2. **It judges; it doesn't apply a threshold on its own.** Given a power reading with "under 5 W means idle" buried in prose, separation was only +0.21; putting that rule in the question, or letting code do the comparison and hand over only "it's idle," both reached +0.6 to +0.7, and the two don't stack (HA-Jev). But with **both numbers in the state and the question "which is larger,"** 64 of 64 were right (jev-mcp). It can compare two values in front of it; don't expect it to remember a threshold the question never states. Leave arithmetic and exact numbers to code.
3. **A rule in the question beats the same rule in the state**: placed in the state it was worth about half as much (HA-Jev).
4. **Option order changes answers.** Reversing the option order flipped 32 of 200; flipped items averaged 0.42 confidence, stable ones 0.81 (jev-mcp). For a classification that gates a consequential action, ask again in a different order and send disagreements to a person.
5. **The option list is part of the question.** Offer only options you can actually act on: HA-Jev offered rooms with nothing controllable in them, and "kill the lights in the kitchen" picked one at 0.98 — the right answer to the question, and nothing the system could do with it.
6. **When several questions come back together, let confidence decide which to trust, not code order.** "Turn on the kitchen lights": the scope question said 0.41, the device question 1.00; the code checked scope first and turned on every light in the house (HA-Jev).
7. **Separate the requirement from the preferences.** An unlabelled second attribute reads as required. A vendor reported 16/44 to 33/44 from fixing this, but the primary source is an X post we couldn't reach (see [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)). For Choice, name the deciding attribute, then the tie-breakers; for Score, say which levels the requirement gates; a Noul hiding an "and also" is two questions.

Don't lower a confidence threshold to rescue a badly written question — the threshold was calibrated against one question. Fix the question.

### The minimum verification flow for a candidate (copy our own process, don't skip it)

Once you've found a candidate, don't act on the checklist alone — verify:

1. Pull 10–20 **real** historical inputs/outputs from the existing system (not invented ones).
2. Write a minimal Choice/Score call and actually hit the live API against that real data (needs `TYPESAFE_API_KEY`; see the template in [`scripts/common/`](scripts/common/)). **Print the states you're about to send and proofread them, and store the exact state sent with each result** — Jev won't tell you the input is broken: we misspelled one character in a correct option of our own history question and it picked a wrong answer at 0.90 confidence ([`suites/history-recall-context/`](suites/history-recall-context/)). If the state is assembled from OCR, scraping or user input, upstream cleaning is part of this step too.
3. Compare side by side against the existing approach (regex/old classifier/old LLM call) — look at the disagreement rate and confidence distribution, not one nice-looking example. If you compare latency, exclude the first call: connection setup makes it 2–3× slower ([`suites/jev-latency-distribution/`](suites/jev-latency-distribution/)).
4. Only integrate once real data supports it, and **layer it as a second opinion first, not a replacement** — same as our own pilots: run it for a while before promoting it. On a latency-sensitive path, fire one warm-up call after the service starts.
5. Contribute the result — good or bad — back to [`suites/`](suites/). This is the entire reason this repo exists.

**If the candidate is browser automation** (clicking, filling forms, navigating), don't design the architecture from scratch — read [`browser-automation.en.md`](browser-automation.en.md): the reference architecture three real open-source implementations converged on (one call, three questions), how the typing problem gets solved, and a checklist for before you touch your own system.

**If the candidate is a virtual character's expressions or gestures** (AI VTuber, VRChat, visual-novel performance, a Live2D character), read [`virtual-character-expressions.en.md`](virtual-character-expressions.en.md) and use its decision table to identify your oracle first. Two shapes are measured and dead: **"I speak, my own avatar's face follows"** (the oracle is the speaker's own intent, where the human ceiling is 0.524 and the missing signal is in the audio your STT just discarded) and **the listening expression** (it fails to beat always-neutral, and a perfect character-emotion tracker moves it by +0.000).

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
6. **Before reporting, self-check against the PR checklist in `CONTRIBUTING.md`** — especially "every number traces to a real log" and "every finding is tagged 🔬/📚/📖/💭." Finally, run `python scripts/zh-check/check_zh.py` to make sure no Simplified characters slipped in; with an API key, also run `python scripts/zh-check/proofread_jev.py` and check each sentence it lists.

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
