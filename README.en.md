🇹🇼 [中文](README.md)｜🇬🇧 English (this page)

# Jev Capability Atlas

**An independent, unofficial, community project — not sponsored by TypeSafe.** We map where TypeSafe's Jev (a "System One" calibrated-decision model) actually holds up versus where it breaks down, using receipts from real API calls — for people deciding how to use it, for agents deciding where in a codebase to try it, and as a place for anyone who's actually run real experiments to contribute their results.

This is not a leaderboard (that's already well covered by [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) — we cite them, we don't redo them). This answers a more basic question: **when is it strong, when is it weak, and why.**

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

## Where can I try swapping in Jev? (for agents)

If you're an agent asked to evaluate a codebase for "where could this save a slow model call," **read [`AGENTS.md`](AGENTS.md) directly** — it's a scanning checklist written for agents, not prose for people. A proper Claude Skill package of the same content lives at [`skill/jev-fit-check/`](skill/jev-fit-check/SKILL.md), installable via `claude plugin install`.

## Contribute real experiment results

Three kinds of contributions welcome: ① a new test suite ② a translated foreign benchmark ③ pure analysis/write-up. **Receipts first — no hand-typed numbers.** Every contribution needs the raw API response logs attached. Full rules in [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Layout

```
README.md / README.en.md   this page, bilingual
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
