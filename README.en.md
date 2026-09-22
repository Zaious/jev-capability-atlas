🇹🇼 [中文](README.md)｜🇬🇧 English (this page)

# Jev Capability Atlas

**An independent, unofficial, community project — not sponsored by TypeSafe** (beyond the standard early-access waitlist, we've received no payment or preferential access from TypeSafe). This repo exists to help you, us, and anyone using [Jev](https://typesafe.ai) (TypeSafe's System One model) **correctly identify whether a given task is a good fit for it** — using receipts from real API calls, mapping where its "calibrated decision" claim actually holds up versus where it breaks down. For people deciding how to use it, for agents deciding where in a codebase to try it, and as a place for anyone who's actually run real experiments to contribute their results.

This is not a leaderboard (that's already well covered by [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) — we cite them, we don't redo them). This answers a more basic question: **when is it strong, when is it weak, and why.**

## The 30-second version

**What it is, first**: Jev's applicability is "cross-cutting" — not confined to a handful of industries, but to a layer ("narrow judgment") that shows up inside nearly any system, whether that's browser automation, code review, content moderation, finance trading, news classification, or games — see the dozen-plus unrelated industries collected in [`capability-map.md`](capability-map.en.md). 💭 Its own built-in world knowledge is limited, but given sufficient information in the `state` you hand it, its reading-comprehension and extraction ability is absurdly good — a conclusion drawn from dozens of real cases we've collected (🔬 our own tests, 📚 third-party benchmarks); details in "the core finding" below.

**Mechanically**: it's fast and cheap, limited to narrow judgments — pick one option, rate on a scale, answer yes/no — and it never writes prose explaining itself. Because the answer space is one you declare up front, it's **structurally incapable of emitting anything outside that list** — a different class of guarantee than a free-text model occasionally breaking format or inventing a category you never listed; it's not low-probability, it's type-impossible (this only guarantees the answer lands in your list, not that it's the right one — details in "not blind guessing" below).

**It's accurate on tasks where the answer is written directly in the text you hand it** (classification, judging whether two passages relate, catching semantic-level contradictions), and also fits high-volume operations where "the candidates are numerous but all present in the given content" — like browser automation's "which of these on-screen elements should I click," see the worked example below. **The flip side: its judgment rests entirely on the text you hand it — when that text is wrong, it doesn't flag that something's off; it still picks confidently.** 🔬 We hit this ourselves: we misspelled the correct option of a history multiple-choice question, and it picked a wrong answer at 0.90 confidence; with only the typo fixed, it no longer picked that wrong answer (see [`suites/history-recall-context/`](suites/history-recall-context/); a reader caught the typo in [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2), and this paragraph's earlier version was corrected as a result). **When a task needs outside knowledge you didn't supply, you can't tell in advance whether it knows** — 📚 in a real third-party case it was weaker than a large model on background connections the article never states (see [`translations/libukai-hubei-news-classification-zh/`](translations/libukai-hubei-news-classification-zh/)), 🔬 yet it answered our own obscure history question at 0.87 confidence with no passage at all. Putting the needed facts in `state` is the safe move.

---

## Not a state machine, not blind guessing — but also not a "thinking" reasoning model

"Narrow judgments, no explanation" is easy to round down to "it's a state machine / lookup table" or "it's just guessing" — neither is accurate, and they're wrong in different directions.

The comparison isn't out of nowhere: "narrow, semantic-layer judgment" is an architectural slot that, for the past year or so, has typically been filled by rule-based state machines plus fast, small models — at the cost of being rigid, with a low ceiling on capability. Jev is aiming at that same slot, but with genuine language understanding underneath — which is exactly why "state machine" comes to mind naturally, and exactly why applying it literally is inaccurate.

**Why it's not a state machine**: a state machine's core is finite discrete states plus hand-written transition rules. Under the hood, Jev is a trained language model doing distributed language understanding, not rule matching — evidence in [`suites/citation-support-check/`](suites/citation-support-check/)'s two contrast cases: `paraphrase_support` (claim and quote share almost no literal words, but genuinely support each other — correctly judged) and `reversed_meaning_high_overlap` (near-word-for-word overlap except one word that flips the meaning — also correctly judged). 🔬 A pure rule/keyword system can't do either.

But the "state machine" metaphor gets one thing right — not the internals, the intended *position* in a system. TypeSafe's own framing: "code needs a narrow decision it can inspect and act on," "99% machine-to-machine interactions." 📖 It should be used as a component embedded in your own program logic, not an autonomous conversational partner. "A node in your state machine" is the right architectural instinct; "its internals are a state machine" is not.

**Why it's not blind guessing**: `confidence` isn't a separate "how sure am I" faculty — it's a statistic **computed from** the probability distribution it already produced. 📖 That number is trustworthy because the training objective targets it directly: TypeSafe splits post-training into three paths — RLHF (chatbots, trained for what people like), RLVR (reasoning models, trained to derive correctly), and **RLCD** (what Jev uses, explicitly trained so "higher probability should correspond to a greater chance the answer is correct"). 📖 We've repeatedly seen this number track real difficulty: the cross-turn sarcasm suite's two deliberately ambiguous controls split — one dropped to 0.19 confidence (near a coin flip), the other stayed at 1.00; 🔬 the history suite shows it too: on a question with no single answer ("7th Qing emperor" — counting from Nurhaci, Hong Taiji or Shunzhi gives three different answers, one per option), all three repeats came back near-flat at confidence 0.07–0.13, while the same suite's single-answer questions came back at 0.87–1.00. 🔬

The honest caveat: calibration is a **population-level** property, not a guarantee about any single answer — TypeSafe says so themselves. 📖 A third-party benchmark we found shows exactly where it breaks: on the DAIR Emotion task, Jev's mean confidence was 0.819 while actual accuracy was 48%, and on 16% of items it assigned the correct answer a probability of exactly zero. 📚 **This is where the "blind guessing" concern actually lands** — not that it guesses everywhere, but that its confidence mechanism can fail on certain tasks (genuinely overlapping, blurred categories), in the most dangerous direction: appearing more certain than it has any right to be.

**One more guarantee worth separating from "not blind guessing"**: because the Choice/Score/Noul answer space is one you declare up front, it's structurally incapable of selecting anything outside that list — TypeSafe's own wording is that "producing an invalid value or a hallucinated answer is mathematically impossible." 📖 That's different from a free-text model, which can break format, answer off-topic, or invent a category you never listed — leaving you to write a parser to catch the drift. Jev structurally can't do that; whatever it returns is guaranteed to be one of the values you defined. **But this is a type guarantee, not a correctness guarantee** — the DAIR Emotion case above is a live counter-example: the answer always lands on one of the six emotion options (the type guarantee holds), but which one it picks is often wrong (the correctness guarantee doesn't). Keep the two apart, or "can't go off-menu" quietly turns into "can't be wrong."

**So what is it**: a model trained for genuine language understanding, deliberately constrained to typed answers only, with a training objective aimed at making its probability numbers trustworthy. It differs from a state machine in having real language understanding; from blind guessing in that its confidence carries empirical signal (with the caveat above); from current "reasoning models" (o1/DeepSeek-R1-class) in not doing extended, multi-step, self-conditioning derivation — TypeSafe places it in a genuinely third category. All three negations together are more honest than reaching for any single label.

### "System One" is not a metaphor; it is the design goal

Take the name literally: the SDK method is `client.system_one(...)`, and the family is called System One models 📖. In Kahneman's split, System 1 is fast, automatic and does not explain itself; System 2 is slow, deliberate and works things out. So the line above — that it should be used as a component embedded in your own code — **is not a conclusion we derived, it is the vendor's own positioning**; and "let the slow model think and the fast one act" is nobody's invention, it is the reason this model exists.

💭 Two practical consequences for anyone reading this map:

1. **An architecture where a large model plans and Jev picks the actions is not a discovery** — it is the default. What's worth recording is **where the line falls, and the third layer**. Every implementation that actually runs has three: planning (a large model sets the objective), decision (Jev picks one per step) and **deterministic execution** (pathfinding, protocol, arithmetic, rule checks — not a model at all). That third layer is usually left out of the telling entirely, yet without it the first two layers' output never reaches a real system. Worked examples: the Minecraft section of [`analysis/jev-games-tcg.md`](analysis/jev-games-tcg.md) (35 planning calls, 131 decisions, execution handed to Mineflayer) and [`browser-automation.en.md`](browser-automation.en.md).
2. **What *is* non-obvious is inverting the default**: PlayJev hands its least confident steps **up** to System Two; wakegate spends one cheap judgment **before** waking the agent at all. Those are the "you wouldn't think of that" cases — [`jev-patterns.en.md`](jev-patterns.en.md) collects that kind, not the manual.

### A worked example: why browser automation benchmarks so well

Two independent third-party projects wired Jev into browser automation, with consistent results: `jev-browser` (an independent developer's MCP server, 1.5× faster and 1.6× cheaper than Playwright MCP at tied accuracy) and `jev-ultrafast` (Browser Use's own official integration, 25% faster median task time, 91% fewer browser protocol calls). 📚 Full methodology, numbers, and honest caveats for both, kept separate, are in [`capability-map.md`](capability-map.en.md) — not repeated here; this section is about the mechanism.

This isn't "Jev is good at browsing" — it currently accepts text only, no screenshots, per its own docs. What's actually happening is that both integrations hit the same two principles precisely:

1. **Trading "look at the screen" for "read given text"**: instead of a screenshot, it uses a structured DOM-snapshot as `state` — a task that used to need visual understanding gets translated into a purely textual, self-contained judgment, landing squarely in its strong zone.
2. **Trading "one step at a time" for "one batch"**: instead of asking a slow model "what do I click next" at every step, it asks about every candidate element in parallel in one call (TypeSafe's own term: "speculative fan-out") — exactly its strength: high-volume, narrow, parallel judgments.

In other words, what's strong here isn't the model's own browsing savvy — it's that someone placed it correctly. This is a worked example of the "component, not agent" framing above, not an exception to it. **But the same data also shows this principle's edge**: in the `jev-browser` results, a pure text-extraction task (no actions involved) ran slower and more expensive with Jev than with an LLM alone — the self-contained advantage only holds for *acting* on a page, not *reading* one. Details in `capability-map.md` as well.

**If you've seen this evidence and decided to wire your own system up to it, read [`browser-automation.en.md`](browser-automation.en.md)** — the reference architecture (one call, three questions), how to solve the typing problem, three real implementations to reference, and a checklist for before you touch your own system. Not repeated here.

---

## What "make Jev see images" actually amounts to today

**Jev itself still accepts text only** — no images, audio or video; the official Models page says "not supported (yet)" 📖. So when you see a claim that something "gives Jev vision," the first job is to work out which of three quite different things it is:

1. **Swap in a model that already sees images and dress it in Jev's question format** (decider-2b-vision, PlayJev, djev dev, jevlike, or LitJev on a vision Qwen). The vision is real, **but it isn't Jev** — it's someone else's weights wearing the same question shape, so calibration, accuracy and hardware all have to be asked again from scratch.
2. **Turn the scene into text or structured data first, then hand that to the real Jev** (DOM, OCR, depth plus segmentation, hand tracking). That is genuinely Jev, and Jev never saw an image.
3. **A claim with nothing behind it.**

💭 Laying out the published figures (all self-reported; we re-ran none of them), here is where the direction actually stands:

- **Only one of them has held-out numbers**: decider-2b-vision, 300 items per task, Visual7W held out 0.89 (ECE 0.03), ScienceQA 0.95, IconQA 0.94. But its own card says the text side is still on the older v5 weights, and playing from pixels scores 0 the moment it leaves the games it trained on (held-out Freeway, FrozenLake and the harder grid worlds are all 0). 📚
- **The most thoroughly measured one concludes "specialist, and it costs general ability"**: PlayJev averages 0.57 of its teacher's score across ten games, and training on games alone drops MMBench from the base model's 0.66 to 0.48, recovering to 0.78 only with a 20% general-data mix. 📚
- **The one with the deepest engineering has measured no quality at all**: djev dev genuinely patches vLLM's attention and scheduling (keeping an image span bidirectionally visible, forbidding a half-prefilled image, forcing the whole batch eager when an image is present) and does the one thing Jev cannot — options that are themselves images — but the first paragraph of its performance doc states that this release has no held-out external quality evaluation, and asks for one. 📚
- **Nobody has measured accuracy on the "convert to text first" path**; what gets measured there is cost and speed: on the same screenshot, OCR-then-Jev costs $0.0002 and 0.13-0.38 s per decision against $0.032 and 5.2 s for handing the screenshot straight to Claude Opus 5 — **that is a cost and speed comparison, not an accuracy one**. 📚

So what should the criterion be? Not "can it see images?" but **whether the signal you want has already been computed inside your system and simply isn't exposed** — usually it has, and that path is faster, more accurate and cheaper. The full table with per-item evidence is in [`jev-variants.en.md`](jev-variants.en.md#variants-that-read-images-directly); the decision rule is the "candidate signal isn't text" section of [`AGENTS.en.md`](AGENTS.en.md).

## Jev, BERT, Laya: what actually differs

These three get compared a lot, but they are three different kinds of thing. **BERT is a component you train yourself; Jev is a decision service you can ask directly; Laya is an open model that gives BERT Jev's question format while keeping BERT-level comprehension.**

### Technical

| | BERT (as a classifier) | Laya | Jev |
|---|---|---|---|
| What it is | Pretrained encoder (2018; original 110M / 340M parameters) | BERT-style encoder plus a decision head: ModernBERT-large (421M total) in English, mmBERT-base (322M total) multilingual | A pretrained language model post-trained with RLCD; parameter count and architecture not published 📖 |
| Where the question is defined | Fixed into the output layer at training time; a new label set means retraining | Given as text at request time (instructions + criteria), same format as Jev | Given as text at request time 📖 |
| How the state is read | One passage at a time, 512 tokens max in the original | **One sequence per question**, "question + options + state", 512 tokens (English) or 1,024 (multilingual); the state's tail is cut beyond that — at least 6 cases were truncated for the English checkpoint in our run 🔬 | The state is read once and shared by all questions; state plus the longest question can reach 32k tokens 📖 |
| How options are read | Options are just output-layer class indices; the model never reads their text | Option text sits in the same sequence, but all options share 192–256 tokens, so with many options each is cut to a few tokens (it self-reports 0.425 on 77-way Banking77) | Options are read together: an outside experiment found adding an irrelevant option shifts the ratios between the others 📚; 0.87 on 72-way Banking77 📚 |
| Probabilities | Softmax output, usually trained with cross-entropy; calibration is yours to check | Calibration trained with reinforcement learning, but by its own account it ships over-confident and needs a temperature refit | Calibration is the training objective (RLCD) 📖; we measured ECE 0.041 🔬 |
| Can you train it | You must (labelled data required) | Fine-tunable | No — every account shares the same weights; you steer it only through state, instructions and criteria 📖 |
| Deployment and cost | Self-hosted | Self-hosted, Apache 2.0, no per-call cost | API only: $0.042 per million input tokens, output free 📖; data leaves your environment |
| Languages | Depends on the base | The multilingual checkpoint claims 100+ languages, but scores 0.61 on Traditional-Chinese intent 🔬 | Officially best in English, weaker in CJK 📖; we measured 0.93 on Traditional-Chinese intent 🔬 |

What Jev looks like inside isn't published. One black-box study with a couple of thousand API calls ([Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked)) 📚 finds behavioral evidence that the state is encoded once, questions can't see each other, and a question's options are read jointly; "a causal transformer, possibly MoE, around 10B active parameters" is inference, and the author flags it as the least certain part.

### Application

💭 The dividing line isn't "which is more accurate" — it's **whether you have training data and whether your questions keep changing**:

- **Use BERT (or any small classifier you train)**: the task and labels are fixed, you have thousands of labelled examples, volume is high enough that per-call cost matters, and data can't leave your environment.
- **Use Laya**: the same conditions as BERT, but you want to keep Jev's question format (several questions per call, options written as text), or you want to label with Jev first and distil into a self-hosted model. Fine-tuned, it can catch Jev on its own distribution, but you'll need to recalibrate its confidences yourself.
- **Use Jev**: the task is new, unlabelled, the questions change often, the state is long, you need trustworthy probabilities to route on, and data can go to an external API.

A common combination: launch on Jev, accumulate labels, and once the workflow is fixed and volume is large enough, distil into a small self-hosted model — TypeSafe's own cookbook shows training a downstream classical model on Jev's probabilities 📖. The Laya head-to-head is in [`suites/laya-head-to-head/`](suites/laya-head-to-head/); a dozen-plus other open variants, compatible servers and extension libraries are sorted in [`jev-variants.en.md`](jev-variants.en.md).

## The core finding: one axis

Across our own tests (real API calls, not estimates) and every third-party benchmark we've read, one axis keeps explaining the results:

> **Is the correct answer fully recoverable from the `state` you hand the model, or does it require outside knowledge/comparison that isn't in `state`?**

| Self-contained (in the state) | Not self-contained (needs outside knowledge) |
|---|---|
| ✅ Classification (AG News 91%, Banking77 87% — [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) | ⚠️ Questions that need outside knowledge the text doesn't contain (real third-party case: [Hubei news classification](translations/libukai-hubei-news-classification-zh/); it doesn't necessarily not know, but you can't tell in advance — see [`suites/history-recall-context/`](suites/history-recall-context/)) |
| ✅ Citation support-checking (claim + quote both given — see [`suites/citation-support-check/`](suites/citation-support-check/)) | ⚠️ Scoring that needs comparison against an entire field (paper novelty, project significance) |
| ✅ Sarcasm/irony detection (the trigger is present in the given text, even across turns — see [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)) | ⚠️ Genuinely overlapping categories (DAIR Emotion 48% accuracy, with confidence staying misleadingly high — [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) |
| ✅ Picking an expression per line when the oracle is "what a human picks from the text" (0.807, ECE 0.049 — see [`suites/expression-selection/`](suites/expression-selection/)) | ⚠️ The same task when the oracle is "what the voice actor did" (0.436, ECE 0.239, choosing wrong at confidence 1.00 — same suite) |

This axis has a subtler failure mode too: not that a task genuinely needs outside knowledge, but that the caller never put the needed content into `state` in the first place. A real case: someone tried using Jev to decide whether to delete an agent's own past tool-call history (context compaction) — in real tests, the default scoring setup never saw the actual output content, and zero of 256 real results scored above 0.3 to keep, effectively deleting almost everything. **The judgment failure here is fixable; the fact that a bad deletion can't always be undone isn't** — this is exactly the "don't hand irreversible actions to a probabilistic model" principle AGENTS.md already states, just hiding inside "internal cleanup" instead of an obvious business action. **We don't recommend running this unsupervised or enabled by default.** Full trace: [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/).

**Someone later measured the same thing properly, and the result is worth more**: 📚 a third-party implementation ([hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)) measured "use Jev to pick which turns survive into a handoff capsule" across seven real sessions and a 104-question recall exam, **and then removed Jev** — the Jev arm scored 37.5% against 48.1% for a plain tail (4 questions won, 15 lost), and what shipped is the whole dialogue at 1,200 words with no Jev, at 58.7%. Note that its failure mode differs from the paragraph above: **here the state was complete and Jev's judgement really did beat recency (11 questions to 4); what lost is the shape of the question** — a kept turn still survives only as its first 400 characters, while turns average 1,400-7,400, so no choice of turns recovers what clipping throws away. That adds a corollary to the axis: **after rewriting a task into a shape Jev can answer, ask once more whether that shape can still do the original job**. See [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/).

Source tags: 🔬 our own tests (with receipts) / 📚 third-party sources (not re-run by us) / 📖 TypeSafe's own docs / 💭 our own judgment — full definitions and inclusion rules in [`CONTRIBUTING.md`](CONTRIBUTING.md#inclusion-rules); each experiment's methodology and per-item receipts live in its own [`suites/`](suites/) directory.

---

## How can I use Jev? (for people)

1. **Read TypeSafe's own [skill](https://github.com/typesafe-ai/skills) first** for how to call the API and design Choice/Score/Noul questions — they cover that well, we don't repeat it.
2. **Read [`capability-map.en.md`](capability-map.en.md)** (or the [Chinese original](capability-map.md)) and place your task on the self-contained vs. needs-outside-knowledge axis to calibrate your expectations. For ideas on ways to ask it that you might not think of, see [`jev-patterns.en.md`](jev-patterns.en.md): organized by technique rather than domain, with representative implementations and evidence.
3. **Validate your own confidence thresholds on your own data.** Don't copy a number from any report, including this one — TypeSafe's own docs say the same. A reasonable starting pattern: high confidence → act automatically; medium → confirm first; low → escalate to a person or a full reasoning-capable model.
4. **For tasks that require *knowing* something rather than *judging* something, retrieve first and put it in `state`.** Not because it necessarily can't remember (it answered our obscure history question at 0.87 confidence with no passage), but because you can't tell in advance whether it does; with the passage in `state`, the same question went to 1.00. See [`suites/history-recall-context/`](suites/history-recall-context/) and the real third-party case [Hubei news classification](translations/libukai-hubei-news-classification-zh/).
5. **Only decompose into atomic questions when the single-question judgment is genuinely weak — don't assume decomposition is always more accurate.** A third-party benchmark measured it: decomposition did raise accuracy on three tasks, but on "looks dangerous, is actually benign" hard benign cases, the false-positive rate worsened from 1.5% single-question to 37.2% decomposed — roughly 25x; also don't ask one question with many options for multi-class problems (a 12-option single call scored only 0.3998 in that same benchmark, the worst result in it). Decomposed results are a good secondary opinion, not something we'd recommend as the sole gate for a guardrail. Details in [`capability-map.en.md`](capability-map.en.md#the-cost-of-decomposing-a-judgment).
6. **Ask whether your judgment's marginal cost is already zero before wiring Jev in at all.** If you're already on a flat-rate subscription tool (Claude Code, Codex, etc.), the marginal cost of one more LLM call is already near zero — adding a Jev layer only adds latency and a new failure surface, with no real savings; Jev actually pays off where you'd otherwise be paying per-call for an LLM. Separately, "fast" really means **no long tail, not a leading median** — both a third-party benchmark and our own re-test found Jev's median latency doesn't necessarily beat a lightweight LLM's, but it almost never produces the kind of maddening slow outlier that a lightweight model occasionally does, which matters more than median speed for anything user-facing and real-time. Details in [`capability-map.en.md`](capability-map.en.md#you-got-jev-now-what-a-hype-free-landing-list), [`suites/jev-latency-distribution/`](suites/jev-latency-distribution/).
7. **Before swapping in a self-hosted open alternative (e.g. Laya), separate "fixed workflow with training data" from "new task, ask it directly"** — on identical inputs, Laya's fine-tuned specialist beats Jev by 3 points of accuracy on its own training distribution but with five times the calibration error; its general checkpoints score below an input-blind baseline and trail Jev by about 30 points on Chinese intent classification. See [`suites/laya-head-to-head/`](suites/laya-head-to-head/).
8. **Write every level of a Score question as something directly observable in the text** — TypeSafe's own composite-scoring example uses resume screening, with levels like "No Python experience mentioned," "Mentioned but no detail," "Used in projects, some specifics" that can be checked against the resume, each dimension scored separately and the weights kept in your own code 📖 ([Composite scoring](https://docs.typesafe.ai/patterns/composite-scoring)). A level that needs outside comparison ("this result is important") can't be read from the text — that's the core axis, applied to scoring.
9. **Know what's in the `state` before you send it** — Jev is a cloud API with no on-premise build, so **every character you put in the `state` has left the machine**. One third-party implementation works the layering through carefully and it's worth copying 📚: redact emails, phones and tokens; replace a retrieved passage's source id and path with `P0`/`P1` so the content goes and the provenance doesn't; drop a passage that looks like a credential entirely rather than redacting it; and on sensitive paths send coarse features only (length, whether code is present, whether risk words appear). One detail is easy to miss: **decode before you screen** — a newsletter footer carries the recipient's address percent-encoded in the unsubscribe link and base64'd in the tracking link, and a plain-text redactor sees neither. And an ordering problem: if the decision happens before the agent acts (using Jev to pick this turn's model, say), telling the agent never to send customer data does nothing. See [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/) and [`AGENTS.md`](AGENTS.md).

## For agents: where to try Jev, and how to report back

**Read [`AGENTS.md`](AGENTS.md) directly** rather than inferring from this page — it covers two situations: being asked to evaluate **another project** for where Jev could fit (a scanning checklist), or being brought into **this repo itself** to run or add suites (commands for running existing suites, steps for adding one, and a **concrete protocol for reporting results** — what to do with vs. without push access, and exactly what a report must include). A proper Claude Skill package of the "evaluate another project" half lives at [`skill/jev-fit-check/`](skill/jev-fit-check/SKILL.md), installable via `claude plugin install`.

## Contribute real experiment results

Four kinds of contributions welcome: ① a new test suite ② organizing and verifying an external source (benchmarks, articles, posts, repos) ③ pure analysis/write-up ④ correcting or extending existing pages (variants page, implementation guides, capability map). **Receipts first — no hand-typed numbers.** ① needs the raw API response log attached; the others need a verifiable primary-source link. What we accept, and where new material goes, is in the inclusion rules in [`CONTRIBUTING.md`](CONTRIBUTING.md#inclusion-rules).

## Layout

```
README.md / README.en.md   this page, bilingual (mechanism explained here, not a separate file)
AGENTS.md                  scanning checklist for agents
capability-map.md / .en.md the axis, kept up to date
browser-automation.md / .en.md  implementation guide for browser automation (architecture, typing problem, real implementations)
jev-variants.md / .en.md   open Jev variants, compatible servers and extension libraries (with verification status)
jev-patterns.md / .en.md   usage patterns: non-obvious techniques organized by approach (with evidence and failure conditions)
CONTRIBUTING.md            contribution rules
skill/jev-fit-check/       AGENTS.md packaged as a Claude Skill
suites/                    each real test (methodology + protocol + raw logs + report)
translations/              foreign benchmarks, translated and organized (results only, not test items)
analysis/                  pure analysis with no single existing entry to attach to (cross-entry observations, critiques of the axis itself)
scripts/common/            shared API-calling boilerplate
scripts/zh-check/          Simplified-character check (runs on every PR) and a Jev proofreading helper
```

## License

Code and original content: MIT (see [`LICENSE`](LICENSE)). `translations/` holds our own summaries and verification, not translations of the originals; rights in quoted material stay with their authors — details in [`NOTICE`](NOTICE). Read `CONTRIBUTING.md` before contributing an entry: reproducing more than short phrases of an original requires checking its license first. This is a real legal question, not a formality.

Not affiliated with, endorsed by, or sponsored by TypeSafe. "Jev" and "TypeSafe" are trademarks of their respective owners, referenced here only to identify the subject.
