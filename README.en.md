🇹🇼 [中文](README.md)｜🇬🇧 English (this page)

# Jev Capability Atlas

**An independent, unofficial, community project — not sponsored by TypeSafe.** We map where TypeSafe's Jev (a "System One" calibrated-decision model) actually holds up versus where it breaks down, using receipts from real API calls — for people deciding how to use it, for agents deciding where in a codebase to try it, and as a place for anyone who's actually run real experiments to contribute their results.

This is not a leaderboard (that's already well covered by [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) — we cite them, we don't redo them). This answers a more basic question: **when is it strong, when is it weak, and why.**

## The 30-second version

Jev is fast and cheap, limited to narrow judgments — pick one option, rate on a scale, answer yes/no — and it never writes prose explaining itself. Because the answer space is one you declare up front, it's **structurally incapable of emitting anything outside that list** — a different class of guarantee than a free-text model occasionally breaking format or inventing a category you never listed; it's not low-probability, it's type-impossible (this only guarantees the answer lands in your list, not that it's the right one — details in "not blind guessing" below).

**It's accurate on tasks where the answer is written directly in the text you hand it** (classification, judging whether two passages relate, catching semantic-level contradictions), and also fits high-volume operations where "the candidates are numerous but all present in the given content" — like browser automation's "which of these on-screen elements should I click," see the worked example below. **It breaks — often confidently — on tasks needing knowledge you didn't supply.** The clearest example: the same history multiple-choice question answered wrong at 0.90 confidence with no supporting passage, then correctly at 0.97 confidence once that passage was included (see [`suites/history-recall-context/`](suites/history-recall-context/), real API receipts). This repo exists to help you tell which kind of task you have, and to keep accumulating real cases.

---

## Not a state machine, not blind guessing — but also not a "thinking" reasoning model

"Narrow judgments, no explanation" is easy to round down to "it's a state machine / lookup table" or "it's just guessing" — neither is accurate, and they're wrong in different directions.

The comparison isn't out of nowhere: "narrow, semantic-layer judgment" is an architectural slot that, for the past year or so, has typically been filled by rule-based state machines plus fast, small models — at the cost of being rigid, with a low ceiling on capability. Jev is aiming at that same slot, but with genuine language understanding underneath — which is exactly why "state machine" comes to mind naturally, and exactly why applying it literally is inaccurate.

**Why it's not a state machine**: a state machine's core is finite discrete states plus hand-written transition rules. Under the hood, Jev is a trained language model doing distributed language understanding, not rule matching — evidence in [`suites/citation-support-check/`](suites/citation-support-check/)'s two contrast cases: `paraphrase_support` (claim and quote share almost no literal words, but genuinely support each other — correctly judged) and `reversed_meaning_high_overlap` (near-word-for-word overlap except one word that flips the meaning — also correctly judged). 🔬 A pure rule/keyword system can't do either.

But the "state machine" metaphor gets one thing right — not the internals, the intended *position* in a system. TypeSafe's own framing: "code needs a narrow decision it can inspect and act on," "99% machine-to-machine interactions." 📖 It should be used as a component embedded in your own program logic, not an autonomous conversational partner. "A node in your state machine" is the right architectural instinct; "its internals are a state machine" is not.

**Why it's not blind guessing**: `confidence` isn't a separate "how sure am I" faculty — it's a statistic **computed from** the probability distribution it already produced. 📖 That number is trustworthy because the training objective targets it directly: TypeSafe splits post-training into three paths — RLHF (chatbots, trained for what people like), RLVR (reasoning models, trained to derive correctly), and **RLCD** (what Jev uses, explicitly trained so "higher probability should correspond to a greater chance the answer is correct"). 📖 We've repeatedly seen this number track real difficulty: the cross-turn sarcasm suite's two deliberately ambiguous controls split — one dropped to 0.19 confidence (near a coin flip), the other stayed at 1.00; 🔬 the pure-recall history suite is even more direct — the same question came back near-flat across three options (0.25/0.37/0.38) with no context, concentrated to 0.98 once context was supplied. 🔬

The honest caveat: calibration is a **population-level** property, not a guarantee about any single answer — TypeSafe says so themselves. 📖 A third-party benchmark we found shows exactly where it breaks: on the DAIR Emotion task, Jev's mean confidence was 0.819 while actual accuracy was 48%, and on 16% of items it assigned the correct answer a probability of exactly zero. 📚 **This is where the "blind guessing" concern actually lands** — not that it guesses everywhere, but that its confidence mechanism can fail on certain tasks (genuinely overlapping, blurred categories), in the most dangerous direction: appearing more certain than it has any right to be.

**One more guarantee worth separating from "not blind guessing"**: because the Choice/Score/Noul answer space is one you declare up front, it's structurally incapable of selecting anything outside that list — TypeSafe's own wording is that "producing an invalid value or a hallucinated answer is mathematically impossible." 📖 That's different from a free-text model, which can break format, answer off-topic, or invent a category you never listed — leaving you to write a parser to catch the drift. Jev structurally can't do that; whatever it returns is guaranteed to be one of the values you defined. **But this is a type guarantee, not a correctness guarantee** — the DAIR Emotion case above is a live counter-example: the answer always lands on one of the six emotion options (the type guarantee holds), but which one it picks is often wrong (the correctness guarantee doesn't). Keep the two apart, or "can't go off-menu" quietly turns into "can't be wrong."

**So what is it**: a model trained for genuine language understanding, deliberately constrained to typed answers only, with a training objective aimed at making its probability numbers trustworthy. It differs from a state machine in having real language understanding; from blind guessing in that its confidence carries empirical signal (with the caveat above); from current "reasoning models" (o1/DeepSeek-R1-class) in not doing extended, multi-step, self-conditioning derivation — TypeSafe places it in a genuinely third category. All three negations together are more honest than reaching for any single label.

### A worked example: why browser automation benchmarks so well

A third-party case (`jev-ultrafast`, integrating Jev into the open-source Browser Use agent framework): a Google Flights search dropped from 9.5s to 7.1s (25% faster); a 12-task benchmark against Playwright MCP showed 1.5× faster, 1.6× cheaper, comparable accuracy; the standalone Jev loop ran ~1.8s and $0.0005 per task at 97% success. 📚

This isn't "Jev is good at browsing" — it currently accepts text only, no screenshots, per its own docs. What's actually happening is this integration hits both principles above precisely:

1. **Trading "look at the screen" for "read given text"**: instead of a screenshot, it uses a structured DOM-snapshot as `state` — a task that used to need visual understanding gets translated into a purely textual, self-contained judgment, landing squarely in its strong zone.
2. **Trading "one step at a time" for "one batch"**: instead of asking a slow model "what do I click next" at every step, it asks about every candidate element in parallel in one call (TypeSafe's own term: "speculative fan-out") — exactly its strength: high-volume, narrow, parallel judgments.

In other words, what's strong here isn't the model's own browsing savvy — it's that someone placed it correctly. This is a worked example of the "component, not agent" framing above, not an exception to it.

---

## The core finding: one axis

Across our own tests (real API calls, not estimates) and every third-party benchmark we've read, one axis keeps explaining the results:

> **Is the correct answer fully recoverable from the `state` you hand the model, or does it require outside knowledge/comparison that isn't in `state`?**

| Self-contained (in the state) | Not self-contained (needs outside knowledge) |
|---|---|
| ✅ Classification (AG News 91%, Banking77 87% — [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) | ⚠️ Pure recall/trivia questions with no supporting passage (see [`suites/history-recall-context/`](suites/history-recall-context/)) |
| ✅ Citation support-checking (claim + quote both given — see [`suites/citation-support-check/`](suites/citation-support-check/)) | ⚠️ Scoring that needs comparison against an entire field (paper novelty, project significance) |
| ✅ Sarcasm/irony detection (the trigger is present in the given text, even across turns — see [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)) | ⚠️ Genuinely overlapping categories (DAIR Emotion 48% accuracy, with confidence staying misleadingly high — [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) |

Full methodology, source-provenance tagging (🔬 our own tests / 📚 third-party benchmarks / 📖 TypeSafe's own docs / 💭 our synthesis), and per-item data: **[Jev Evaluation Report](https://claude.ai/code/artifact/286d1a05-f51e-4e18-aba2-234bc0ceb29b)** (bilingual).

---

## How can I use Jev? (for people)

1. **Read TypeSafe's own [skill](https://github.com/typesafe-ai/skills) first** for how to call the API and design Choice/Score/Noul questions — they cover that well, we don't repeat it.
2. **Read [`capability-map.md`](capability-map.md)** and place your task on the self-contained vs. needs-outside-knowledge axis to calibrate your expectations.
3. **Validate your own confidence thresholds on your own data.** Don't copy a number from any report, including this one — TypeSafe's own docs say the same. A reasonable starting pattern: high confidence → act automatically; medium → confirm first; low → escalate to a person or a full reasoning-capable model.
4. **For tasks that require *knowing* something rather than *judging* something, retrieve first and put it in `state`.** Don't rely on its bare memory — see [`suites/history-recall-context/`](suites/history-recall-context/) for a concrete counter-example.

## For agents: where to try Jev, and how to report back

**Read [`AGENTS.md`](AGENTS.md) directly** rather than inferring from this page — it covers two situations: being asked to evaluate **another project** for where Jev could fit (a scanning checklist), or being brought into **this repo itself** to run or add suites (commands for running existing suites, steps for adding one, and a **concrete protocol for reporting results** — what to do with vs. without push access, and exactly what a report must include). A proper Claude Skill package of the "evaluate another project" half lives at [`skill/jev-fit-check/`](skill/jev-fit-check/SKILL.md), installable via `claude plugin install`.

## Contribute real experiment results

Three kinds of contributions welcome: ① a new test suite ② translating and organizing a foreign benchmark's results ③ pure analysis/write-up. **Receipts first — no hand-typed numbers.** ① needs the raw API response log attached; ② needs a verifiable source link. Full rules in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Layout

```
README.md / README.en.md   this page, bilingual (mechanism explained here, not a separate file)
AGENTS.md                  scanning checklist for agents
capability-map.md          the axis, kept up to date
CONTRIBUTING.md            contribution rules
skill/jev-fit-check/       AGENTS.md packaged as a Claude Skill
suites/                    each real test (methodology + protocol + raw logs + report)
translations/              foreign benchmarks, translated and organized (results only, not test items)
scripts/common/            shared API-calling boilerplate
```

## License

Code and original content: MIT. Before contributing a translation, **check the source dataset's license first** — details in CONTRIBUTING.md. This is a real legal question, not a formality.

Not affiliated with, endorsed by, or sponsored by TypeSafe. "Jev" and "TypeSafe" are trademarks of their respective owners, referenced here only to identify the subject.
