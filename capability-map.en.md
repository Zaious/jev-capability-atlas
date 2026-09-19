🇹🇼 [中文](capability-map.md)｜🇬🇧 English (this page)

# Capability Map

This document is living — updated with every new contribution. Axis explained in [README](README.en.md). Tags: 🔬 our/contributor's own test, 📚 third-party benchmark, 📖 TypeSafe's own docs.

Split into two sections: **public benchmarks** are results published by others that we haven't re-run ourselves — we only translate and organize them (see [`translations/`](translations/)); **our own verified tests** went through this repo's full receipts process (see [`CONTRIBUTING.md`](CONTRIBUTING.md)) — real API calls, made by us. The two rest on different kinds of trust, so they're kept apart rather than mixed.

## Index

| Entry | Axis position | One-line result | Tag |
|---|---|---|---|
| [ThaiExam](#thaiexam-567-real-thai-standardized-exam-questions-vs-110-other-models) | Mixed | 70.7% acc, mid-pack of 111 models, fastest/2nd-cheapest in the group | 📚 |
| [jev-benchmarks: AG News](#jev-benchmarks-ag-newsbanking77dair-emotion) | Self-contained | 91.0% acc, clearly beats a specialized small classifier | 📚 |
| [jev-benchmarks: Banking77](#jev-benchmarks-ag-newsbanking77dair-emotion) | Self-contained | 87.0% acc, same, and latency wins too | 📚 |
| [jev-benchmarks: DAIR Emotion](#jev-benchmarks-ag-newsbanking77dair-emotion) | Overlapping categories (edge case) | 48.0% acc tied, but confidence miscalibrated | 📚 |
| [jev-browser vs Playwright MCP](#jev-browser-vs-playwright-mcp) | Mixed (strong at acting, weak at pure reading) | Hybrid: 1.5x faster / 1.6x cheaper; but pure text-extraction tasks are slower and more expensive | 📚 |
| [jev-ultrafast (Browser Use official)](#jev-ultrafast-browser-use-official-integration) | Self-contained | Median task time 25% faster, 91% fewer browser protocol calls | 📚 |
| [TypeSafe's launch evals: Vercel + methodology critique](#typesafes-launch-evals-vercels-independent-validation-and-methodology-critique) | — | 67.8% acc / $0.0004 / 0.4s, but reference labels are an average of two LLMs, not human-labeled | 📚 |
| [Tool-call risk classification (jev-benchmark)](#tool-call-risk-classification-jev-benchmark) | Self-contained | 91.7% acc, confidence honestly drops on wrong answers — no confidently-wrong cases | 📚 |
| [Confidence-gated abstention (jev-dspy-lab)](#confidence-gated-abstention-jev-dspy-lab) | Self-contained | At a 0.7 confidence gate: 95.8% coverage, 91.3% accuracy, ECE 0.0583 | 📚 |
| Praise vs. sarcasm (dedicated public benchmark) | — | None found as of this writing — an open slot you could fill | — |
| [Citation support-checking](#citation-support-checking) | Self-contained | 9/12 supports, 0 contradicts, low confidence correctly tracked hard cases | 🔬 |
| [Sarcasm detection, same-clause/cross-turn](#sarcasm-detection) | Self-contained | 12/12, 10/10 correct, including a correctly-low-confidence case | 🔬 |
| [Pure-recall trivia vs. supplied context](#pure-recall-trivia-vs-supplied-context) | Not self-contained → self-contained | Confidently wrong on a common-knowledge question with no context; confidence and accuracy both recover once context is supplied | 🔬 |

---

## Public benchmarks (third-party, 📚)

None of the following were run by us — this is what we found after reading the original repos/articles/READMEs ourselves. Every entry carries a primary-source link; if a number here doesn't match the source, that's our mistake, not the original author's.

### ThaiExam: 567 real Thai standardized-exam questions, vs. 110 other models

**What was done**: Jev (`jev-1.13.0`) was scored against 110 other language models on the same 567 real Thai standardized-exam questions (mixed subjects).

**Results**: **70.7% accuracy**, **0.35s/question**, **$0.000029/question** — fastest and second-cheapest in the whole comparison, with confidence tracking actual accuracy closely (expected calibration error of 7.5 percentage points).

**What this means**: "mid-pack of 111 models" isn't a throwaway line — it's an expected result. This is a mixed-subject exam, blending questions whose answers are self-contained readable comprehension against questions needing knowledge recall/derivation from outside the given state; per this repo's core axis, that exact mix predicts a middling, blended score. What's actually worth looking at is that **accuracy holds up as not-last-place while running an order of magnitude faster and multiple orders of magnitude cheaper** — supporting its use as a high-volume pre-filter layer, not a replacement for a full reasoning model.

Source: [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts)

### jev-benchmarks: AG News/Banking77/DAIR Emotion

**What was done**: Jev compared against a specialized local zero-shot classifier, `GLiNER2.5`, on three classification datasets (100 class-balanced examples each). Methodology pinned model versions, used deterministic sampling and paired bootstrap confidence intervals — not a casual one-off run.

**Results**:

| Dataset | Jev | GLiNER | Confidence interval |
|---|---|---|---|
| AG News (4-class news topic) | **91.0%** | 70.0% | `[+0.130, +0.290]`, Jev clearly ahead |
| Banking77 (72-class banking intent) | **87.0%** | 61.0% | `[+0.220, +0.300]`, Jev clearly ahead, and latency (246ms) slightly beat GLiNER's local CPU inference (296ms) too |
| DAIR Emotion (6-class emotion) | 48.0% | 44.0% | **includes zero** — statistically indistinguishable |

**What this means**: accuracy wins or loses depending on how cleanly the categories separate — news topics and banking intents are relatively clean, emotions genuinely overlap. DAIR Emotion's real finding isn't the 48% — it's that **confidence broke down at the same time**: Jev's mean confidence was 0.819 (against GLiNER's honest 0.438), and on 16% of items it assigned the correct answer a probability of exactly zero. This risk is only visible once accuracy is roughly tied — looking at accuracy alone would miss it entirely.

Source: [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)

### jev-browser vs. Playwright MCP

**What was done**: An independent developer's Jev-powered browser MCP server, compared against `@playwright/mcp` (an accessibility-snapshot tool server) on 12 tasks (10 local deterministic tasks + 2 live Wikipedia tasks), across three stacks: an autonomous Jev-only loop (zero LLM), Claude + Playwright MCP, and Claude + jev-browser MCP. **Verification is programmatic, not LLM-judged** — every local task ends in a random code that's only revealed once the task is genuinely complete, and the benchmark checks that code directly, eliminating judge bias.

**Results**:

| Stack | Success | Avg wall/task | Avg cost/task |
|---|---|---|---|
| Jev-only (zero LLM) | 32/33 (97%, n=3) | 1.8s (p50) | ~$0.0005 |
| Claude + Playwright MCP | 12/12 (100%) | 18.4s | $0.31 |
| Claude + jev-browser MCP | 12/12 (100%) | 12.2s | $0.20 |

**Claude+jev-browser vs. Claude+Playwright: 1.5× faster, 1.6× cheaper, tied accuracy (12/12 vs. 12/12)**. The biggest wins were on tasks that required re-reading a growing page state (a lazy-load list task was 4.1× faster).

**The honest counter-example, exactly the kind of detail worth having**: this same benchmark caught where Jev **isn't** good — task l02 (Wikipedia infobox extraction, pure reading, no actions) actually ran slower (0.7×) and more expensive (0.3×, i.e. costlier) than Claude alone. The author's own conclusion: "this is not Jev's territory — route read-and-answer tasks to the LLM, act-on-the-page tasks to Jev." This lines up exactly with the axis in this repo's README: browser automation is a strong fit because the candidate elements are all present in the given DOM snapshot (self-contained); once the task becomes reading and interpreting a large block of text, that self-contained advantage disappears.

The author's own caveats: the two Claude stacks ran n=1 (time/cost budget), the Jev-only stack ran n=3; 12 tasks is a smoke-test scale, not a full WebVoyager-style benchmark; "Jev's public accuracy benchmarks are mid-tier vs. frontier models; the hybrid design assumes escalations will happen and prices them in" — a statement that corroborates the ThaiExam mid-pack finding above.

Source: [jev-browser](https://github.com/MahmoudAdelbghany/jev-browser) ([README](https://github.com/MahmoudAdelbghany/jev-browser/blob/main/README.md), [full results](https://github.com/MahmoudAdelbghany/jev-browser/blob/main/RESULTS.md))

### jev-ultrafast (Browser Use official integration)

**What was done**: an official integration by Browser Use, the open-source browser-agent project itself (not an independent community project — 5,700+ stars), wiring Jev into its agent loop. **This is a separate project from jev-browser** — don't conflate the two. By design, Jev only picks the operation (CLICK/TYPE_TEXT/SELECT/SCROLL/WAIT/DONE...) and the target element, both in one parallel request; when actual typing is needed, a separate small text-generation model (`inception/mercury-2.5`, via OpenRouter, reasoning disabled) produces the keystrokes — reinforcing, once again from an official integration, that Jev itself does not generate text, even here a small model is bolted on for that.

**Results** (numbers from the official repo itself, six alternating runs, both versions 3/3): median time for a Google Flights search (Zürich→London, one-way economy) went from **9.450s to 7.092s (25% faster)**; median browser protocol calls went from **1,092 to 101 (91% fewer)**. Two other tasks: opening a specified Wikipedia article in 2.798s, a local hotel search+filter in 1.896s.

**Honest caveats, from the source itself**: "this is three repeats of one task on one browser profile, not a general reliability benchmark"; the DOM reader currently doesn't support shadow DOM, iframes, canvas, file uploads, pop-up tabs, or nested scrolling — explicitly out of scope for this MVP.

Source: [jev-ultrafast](https://github.com/browser-use/jev-ultrafast) ([README](https://github.com/browser-use/jev-ultrafast/blob/main/README.md)), [LavX News coverage](https://news.lavx.hu/article/jev-ultrafast-cuts-browser-agent-time-by-25-with-typesafe-action-space)

### TypeSafe's launch evals: Vercel's independent validation and methodology critique

**What was done**: TypeSafe's own "workflow evals" published at Jev's launch — nine models scored across four workflows (customer service, agent-trace observability, security incidents, invoice processing). Independent blogger Anthony Maio wrote a methodology critique of these evals. Separately, Vercel's CEO Guillermo Rauch and engineer Pranit Kumar posted on X about swapping Jev in for GPT-5.6 Luna as their `fx` tool's command safety reviewer, in production. A dev.to article ties all three threads together with a critical read.

**Results**: Jev scored 67.8% accuracy overall across the nine models, at $0.0004/case and 0.4s/case — 6.3 points behind the best model (GPT-5.6 Sol, 74.1%), but 209x cheaper and 58x faster. At the workflow level, the gap ranges from 2.3 points (customer service) to 17.3 (invoice processing). Vercel reported "5-18x faster and more accurate," but without a published dataset or case count.

**What this means**: **the reference labels in this eval are themselves an average of GPT-6 Astra and Claude Fable 5.1's responses, not human-labeled** — it measures closeness to these two frontier models' consensus, not closeness to human judgment; a model that's actually right where both frontier models share a blind spot gets marked down for it. Maio quotes TypeSafe's own launch post directly: "Our number is not empirical. Schema matching is guaranteed" — nearly identical to the type-guarantee-vs-correctness-guarantee distinction this repo's README draws in "not blind guessing," stated by the vendor itself in almost the same words. Maio also raises a layer this repo hadn't covered before: "individually calibrated judgments do not automatically compose into a calibrated workflow once you run them through thresholds, weights, and branches" — a real caveat for the composite-scoring guidance in the README's practical-guidance section. Full write-up: [`translations/typesafe-launch-evals-zh/`](translations/typesafe-launch-evals-zh/) (Chinese, with an English section below the divider).

Source: [Jev Beat GPT Luna by 1 Point (dev.to)](https://dev.to/gabrielanhaia/jev-beat-gpt-luna-by-1-point-gpt-6-and-claude-wrote-the-answer-key-314k), [Jev: The Language Model That Won't Talk (Anthony Maio)](https://anthonymaio.substack.com/p/jev-the-language-model-that-wont)

### Tool-call risk classification (jev-benchmark)

**What was done**: 60 tool-call cases, hand-labeled with a four-tier risk classification (readonly/destructive/privileged/exfiltration), split by difficulty into clear/ambiguous/adversarial groups; Jev classified each case with confidence recorded per case.

**Results**: 91.7% accuracy overall (55/60). The interesting part isn't the accuracy — it's the confidence behavior: "every incorrect answer came with hedged confidence; the model never returned 1.000 and was wrong."

**What this means**: this is the cleanest positive counter-example to calibration failure collected so far — the mirror image of jev-benchmarks' DAIR Emotion result (0.819 mean confidence against 48% actual accuracy), showing calibration working as intended. The likely difference is task type: tool-call risk classification is a self-contained task where the answer lives almost entirely in the call content itself, unlike DAIR Emotion's genuinely blurred categories — supporting this repo's core axis: how self-contained a task is affects not just accuracy but whether its confidence can be trusted. Full write-up: [`translations/jev-benchmark-toolcall-risk-zh/`](translations/jev-benchmark-toolcall-risk-zh/) (Chinese, with an English section below the divider).

Source: [themsquared/jev-benchmark](https://github.com/themsquared/jev-benchmark)

### Confidence-gated abstention (jev-dspy-lab)

**What was done**: measurement infrastructure (built on the DSPy framework) for confidence-gated abstention behavior; the repo includes one real recorded run using `jev-latest` — 24 support-ticket-routing cases, confidence threshold set at 0.7.

**Results**: 95.8% coverage (roughly 1 case abstained), 91.3% accuracy among answered cases, Brier score 0.1546, ECE 0.0583.

**What this means**: the first case in this repo's collection demonstrating an abstention mechanism rather than plain right/wrong — it turns the "low confidence → escalate to a human" leg of the README's practical-guidance routing pattern into an actual measured coverage/accuracy number. But the sample is only 24 cases (roughly 1 abstention), small enough that any single case swings the numbers substantially — this entry's value is **demonstrating a measurement methodology applicable to any task**, not a citable benchmark result. Full write-up: [`translations/jev-dspy-lab-zh/`](translations/jev-dspy-lab-zh/) (Chinese, with an English section below the divider).

Source: [jmanhype/jev-dspy-lab](https://github.com/jmanhype/jev-dspy-lab)

### Praise vs. sarcasm (dedicated public benchmark)

No one appears to have published a dedicated public benchmark for Jev's sarcasm/irony detection specifically — we tested this ourselves (see below), but that's our own small test, not an independent third-party benchmark. This is an open slot you could fill: find or publish one, then translate/organize it into [`translations/`](translations/).

---

## Our own verified tests (🔬, via CONTRIBUTING's receipts process)

Every entry below made real API calls; raw logs live under the matching `suites/<slug>/runs/`, full methodology in each one's `README.md`. This is just the summary.

### Citation support-checking

**What was done**: given a claim and a verbatim quote, ask Jev a single Choice question: does the quote support, contradict, or fail to address the claim? 5 synthetic cases covering a clean contradiction, complete irrelevance, a subtle-but-thin case, and two key contrasts (a paraphrase with low literal overlap that genuinely supports; a near-verbatim overlap whose meaning is flipped by one word).

**Results**: 5/5 correct, including both contrast cases judged correctly at 1.00 confidence; the one low-confidence case (0.45) was a genuinely subtle semantic distinction — flagging it for review is exactly the behavior we want. This same methodology was separately cross-validated against 16 real citations from an actual unpublished academic manuscript, with consistent results (see the full evaluation report linked from the README).

Source: [`suites/citation-support-check/`](suites/citation-support-check/)

### Sarcasm detection

**What was done**: two rounds — same-clause (the ironic trigger and the positive words share one sentence) and cross-turn (the negative context and a lexically pure positive statement are split across separate turns, removing the same-clause lexical contradiction). Each round includes deliberate "trap" cases designed to look sarcastic but are actually sincere; the cross-turn round adds two deliberately ambiguous, unscored controls.

**Results**: same-clause 12/12, cross-turn (scored) 10/10, both mostly above 0.80 confidence. The two ambiguous controls diverged: one landed honestly low (0.19), the other maxed out (1.00, on reflection probably not genuinely ambiguous). **We initially predicted sarcasm detection would be a weak spot** (reasoning from the RLCD/RLVR architecture distinction) **— that prediction was wrong**: as long as the ironic trigger is fully present in the given state, a single parallel judgment catches it.

Source: [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)

### Pure-recall trivia vs. supplied context

**What was done**: three Traditional-Chinese history multiple-choice questions — (1) a commonly-known fact, no context; (2) an obscure fact, no context; (3) the same question as (2), but with a supporting passage included. The goal was isolating "bare memory" from "reading comprehension given supplied text."

**Results**: case (1) was answered wrong at 0.90 confidence on what's generally considered common knowledge, with no context given; case (2)'s confidence sat honestly near a coin flip (probabilities 0.25/0.37/0.38 across the three options); case (3) — the same obscure question with a passage supplied — concentrated to 0.98 confidence and was answered correctly. **Confidently wrong on a common-knowledge question is the single most important counter-example in this whole repo** — with no context, Jev is drawing purely on opaque pretraining memory, the same risk profile as asking any LLM a bare trivia question.

Source: [`suites/history-recall-context/`](suites/history-recall-context/)

---

**Untested, contributions welcome**: multimodal input (Jev currently only accepts text, per its own docs), composite multi-dimensional scoring in real product settings, non-English languages other than Thai, sarcasm/implied-intent detection spanning more than two conversational turns, and a dedicated third-party benchmark for praise vs. sarcasm.
