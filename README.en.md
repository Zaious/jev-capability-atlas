🇹🇼 [中文](README.md)｜🇬🇧 English (this page)

# Jev Capability Atlas

**An independent, unofficial, community project — not sponsored by TypeSafe.** We map where TypeSafe's Jev (a "System One" calibrated-decision model) actually holds up versus where it breaks down, using receipts from real API calls — for people deciding how to use it, for agents deciding where in a codebase to try it, and as a place for anyone who's actually run real experiments to contribute their results.

This is not a leaderboard (that's already well covered by [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) — we cite them, we don't redo them). This answers a more basic question: **when is it strong, when is it weak, and why.**

## The 30-second version

Jev is fast and cheap, but limited to narrow judgments — pick one option, rate on a scale, answer yes/no — and it never writes prose explaining itself. **It's accurate on tasks where the answer is written directly in the text you hand it** (classification, judging whether two passages relate, catching semantic-level contradictions). **It breaks — often confidently — on tasks needing knowledge you didn't supply.** The clearest example: the same history multiple-choice question answered wrong at 0.90 confidence with no supporting passage, then correctly at 0.97 confidence once that passage was included (see [`suites/history-recall-context/`](suites/history-recall-context/), real API receipts). This repo exists to help you tell which kind of task you have, and to keep accumulating real cases.

> ⚠️ **"Narrow judgments, no explanation" is not the same as "it's a state machine / lookup table" or "it's just guessing" — neither is accurate.** The actual distinction is laid out in **[`MECHANISM.md`](MECHANISM.md)** — required reading, not optional, especially if you're going to relay this repo's conclusions to someone else.

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

Three kinds of contributions welcome: ① a new test suite ② a translated foreign benchmark ③ pure analysis/write-up. **Receipts first — no hand-typed numbers.** Every contribution needs the raw API response logs attached. Full rules in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Layout

```
README.md / README.en.md   this page, bilingual
MECHANISM.md                required reading: not a state machine, not guessing, not a reasoning model either
AGENTS.md                  scanning checklist for agents
capability-map.md          the axis, kept up to date
CONTRIBUTING.md            contribution rules
skill/jev-fit-check/       AGENTS.md packaged as a Claude Skill
suites/                    each real test (methodology + protocol + raw logs + report)
translations/              translated foreign benchmarks
scripts/common/            shared API-calling boilerplate
```

## License

Code and original content: MIT. Before contributing a translation, **check the source dataset's license first** — details in CONTRIBUTING.md. This is a real legal question, not a formality.

Not affiliated with, endorsed by, or sponsored by TypeSafe. "Jev" and "TypeSafe" are trademarks of their respective owners, referenced here only to identify the subject.
