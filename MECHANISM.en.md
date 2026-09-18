🇹🇼 [中文](MECHANISM.md)｜🇬🇧 English (this page)

# Not a state machine, not blind guessing — but also not a "thinking" reasoning model

**This page is required reading, not optional.** Most of this repo talks about "where it's strong, where it's weak." If that's all you read, it's easy to mentally round it down to "a lookup table" or "a guessing classifier" — both wrong, in different directions. This page covers the underlying mechanism; read it before [`capability-map.md`](capability-map.md) and [`AGENTS.md`](AGENTS.md).

## What it actually does

One request = one `state` (text or JSON) + one or more typed questions (Choice picks one option, Score rates against a rubric, Noul returns a yes/no probability). The response = a typed answer + the full probability distribution + a `confidence` number computed from that distribution. It **does not generate text, code, or an explanation of its reasoning** — that's a stated architectural constraint in TypeSafe's own docs, not a style choice. 📖

## Why it's not a state machine

A state machine's core is: finite discrete states plus hand-written transition rules. Jev isn't that — underneath, it's a trained language model doing distributed, statistical language understanding, not rule matching. Our own evidence:

- The `paraphrase_support` case (see [`suites/citation-support-check/`](suites/citation-support-check/)): the claim and quote share almost no literal words ("intervention" vs. "program," "drop" vs. "decreased"), yet genuinely support each other — it got this right. A pure keyword/rule-matching system can't, because there's no shared literal surface to match on. 🔬
- The `reversed_meaning_high_overlap` case (same suite): the claim and quote overlap almost word-for-word except for one word (increased/decreased), which flips the meaning entirely — it caught this too. That requires actually reading semantic direction, not comparing surface text. 🔬

**But there's one thing the "state machine" metaphor does get right** — not its internals, but its intended *position* in a system. TypeSafe's own framing: "code needs a narrow decision it can inspect and act on," "99% machine-to-machine interactions." It's designed to be a component embedded in your own program logic, not an autonomous conversational partner. Treating it as "a node in your state machine" is the right architectural instinct; imagining its *internals* as a state machine is not. 📖

## Why it's not blind guessing

`confidence` isn't a separate "how sure am I" faculty — it's a **statistic computed from** the probability distribution it already produced. A concentrated distribution means high confidence; a flat one means low. 📖 That number is trustworthy specifically because the training objective targets it directly: TypeSafe describes three post-training paths — RLHF (chatbots, trained to produce what people like), RLVR (reasoning models, trained to derive correctly), and **RLCD** (what Jev uses, explicitly trained so that "higher probability should correspond to a greater chance the answer is correct"). 📖

We've repeatedly seen this number carry real information, not uniform noise: the cross-turn sarcasm suite's two deliberately ambiguous control cases split — one genuinely dropped to 0.19 confidence (near a coin flip), the other stayed at 1.00 — same script, same batch of calls, confidence tracking actual case difficulty. 🔬 The pure-recall history suite is even more direct: the same question, with no supporting passage, came back with probabilities nearly flat across three options (0.25/0.37/0.38); with a passage supplied, probability concentrated to 0.98. 🔬

**The honest caveat belongs right here**: calibration is a **population-level** property, not a guarantee about any single answer — TypeSafe says this themselves, and a third-party benchmark we found shows exactly where it breaks: on the DAIR Emotion task, Jev's mean confidence was 0.819 while actual accuracy was only 48%, and on 16% of items it assigned the correct answer a probability of exactly zero. 📚 **This is where the "blind guessing" concern actually lands** — not that it's guessing everywhere, but that its confidence mechanism can fail on certain tasks (genuinely overlapping, blurred categories), and fails in the most dangerous direction: appearing more certain than it has any right to be.

## So what is it

A model trained for genuine language understanding, deliberately constrained to emit only typed answers, with a training objective specifically aimed at making its probability numbers trustworthy. It differs from a state machine because it has real language understanding; it differs from blind guessing because its confidence numbers carry empirical signal (with the caveat above — not unconditionally); it differs from current "reasoning models" (o1/DeepSeek-R1-class) because it doesn't do extended, multi-step, self-conditioning derivation — TypeSafe puts it in a genuinely third category, not a lesser reasoning model. Together, these three negations are a more honest description than reaching for any single existing label.

## What this means for an agent

If you're reading this repo to advise or report to someone on whether to use Jev, **don't compress it down to "state machine" or "guessing,"** and don't overcorrect into "it thinks" either. Use this page's three negations plus one positive description, or link directly to this page — don't re-simplify it yourself.
