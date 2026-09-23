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
| [Pruning an agent's own execution history with Jev: a public debate](#pruning-an-agents-own-execution-history-with-jev-a-public-debate) | — | Ranking correct, threshold miscalibrated; real replay: 0/256 results scored above 0.3 | 📚 |
| [Does sorting by a Jev probability via SQL ORDER BY hold up?](#does-sorting-by-a-jev-probability-via-sql-order-by-hold-up) | Mixed (easy passes, hard fails) | 20 Newsgroups passes all 6 gates; Amazon ESCI fails 4 of 6 | 📚 |
| [Reranking for LlamaIndex with Jev](#reranking-for-llamaindex-with-jev) | Self-contained (narrow passage-level relevance) | nDCG@5 significantly improved on both datasets (+0.056 / +0.086) | 📚 |
| [Jev alone doesn't beat vector retrieval for reranking, but fusing it does](#jev-alone-doesnt-beat-vector-retrieval-for-reranking-but-fusing-it-does) | Mixed (alone not self-contained enough, fused as a second signal works) | Alone: CI crosses zero / -0.028 judge-bias-free; RRF fusion: +0.064 to +0.090 | 📚 |
| [The cost of decomposing a judgment](#the-cost-of-decomposing-a-judgment) | — | Accuracy up on 3 tasks, but false positives on hard benign cases up 25x | 📚 |
| [Content moderation in production (mastra-jev-moderation)](#content-moderation-in-production-mastra-jev-moderation) | Self-contained | 9/9 hostile messages blocked, 0/49 real messages false-flagged | 📚 |
| [A real production Simplified-Chinese classification task: does this news article involve Hubei?](#a-real-production-simplified-chinese-classification-task-does-this-news-article-involve-hubei) | Mixed (mostly self-contained, disagreements cluster where not) | ~85% agreement with Flash Lite; disagreements mostly named-entity cases needing outside knowledge | 📚 |
| [The viral ad-breakdown tweet: can Jev read a Gemini embedding?](#the-viral-ad-breakdown-tweet-can-jev-actually-read-color-and-style-from-a-gemini-embedding) | — | Performance numbers plausible; the "embedding carries visual semantics to Jev" explanation doesn't hold up | 📚 |
| [You got Jev, now what? A hype-free landing list](#you-got-jev-now-what-a-hype-free-landing-list) | — | Only 15 of 217 projects usable today; the author's own 4 integration attempts all failed, with specific root causes | 📚 |
| [Jev as an agent judge (LangChain)](#jev-as-an-agent-judge-langchain) | Self-contained (the trace and evidence are in the state) | Matched the human on all five pass/fail items, 92–913× lower score variance than three LLM judges, $0.00035 per call; but five items, one reviewer, and the control group's sampling was never turned off | 📚 |
| [An agent's small internal decisions](#an-agents-small-internal-decisions-routing-skill-selection-action-choice-hermes-jev-skills) | Self-contained (the candidates are on the screen, in the catalog, in this turn's text) | A verification step turned 2 confident-wrong skill picks (0.94-0.96) into 0; the single 0.65 action floor gave zero wrong actions across five runs | 📚 |
| [Compaction and handoffs: measured, then Jev removed](#compaction-and-handoffs-measured-then-jev-was-removed-hermes-jev-skills) | Wrong shape (the state was complete and the judgement was good; picking turns is what lost) | The Jev arm scored 37.5% against 48.1% for a plain tail (4 questions won, 15 lost); what shipped drops Jev and scores 58.7% | 📚 |
| [HA-Jev: question-writing rules from a Home Assistant integration](#ha-jev-question-writing-rules-measured-against-the-live-api-in-a-home-assistant-integration) | Self-contained (provided the threshold is in the question, or code does the comparison first) | Separation +0.21 on readings alone, +0.60/+0.69 with the rule in the question or the comparison pre-computed; 97 more questions cost 24 ms; structured option definitions 12/15 vs 12/15, no gain | 📚 |
| [jev-mcp (blakestone-x): definitions, ordering, calibration](#jev-mcp-blakestone-x-definitions-ordering-and-calibration-on-production-data) | Self-contained | Bare label names to a one-line definition: 64.5% to 81.0%; reversing option order flipped 32 of 200, flipped items averaged 0.42 confidence; data not public | 📚 |
| Praise vs. sarcasm (dedicated public benchmark) | — | None found as of this writing — an open slot you could fill | — |
| [Citation support-checking](#citation-support-checking) | Self-contained | 9/12 supports, 0 contradicts, low confidence correctly tracked hard cases | 🔬 |
| [Sarcasm detection, same-clause/cross-turn](#sarcasm-detection) | Self-contained | 12/12, 10/10 correct, including a correctly-low-confidence case | 🔬 |
| [Pure-recall trivia vs. supplied context](#pure-recall-trivia-vs-supplied-context) | Not self-contained → self-contained | With clean questions it knew even the obscure fact (confidence 0.87→1.00 with a passage); the earlier "confidently wrong" result came from our own typo — a wrong state doesn't dent its confidence | 🔬 |
| [Latency distribution: median vs. tail](#latency-distribution-median-vs-tail) | — | Median 247ms, p95 281ms; no outlier in 30 calls once the warm-up is excluded — the older run's outlier is confirmed as connection cold-start | 🔬 |
| [A stage-one filter: which half of a two-stage pipeline should Jev own](#a-stage-one-filter-which-half-of-a-two-stage-pipeline-should-jev-own) | Self-contained (content + the watch reason both supplied) | Three rounds of question-design iteration; none of the three failures was about judgment | 🔬 |
| [Jev vs Laya: a head-to-head on identical inputs](#jev-vs-laya-a-head-to-head-on-identical-inputs) | Self-contained (both sides get identical input) | Zero-shot: Jev 0.736, Laya 0.36 (below an input-blind baseline); Laya's fine-tuned specialist wins by 3 points with 5× the calibration error; zh-TW intent 0.93 vs 0.61 | 🔬 |
| [Picking an expression per line](#virtual-humans-picking-an-expression-per-line-one-task-both-sides-of-the-axis) | The same task on both sides | 0.807 with ECE 0.049 when the answer is in the text; 0.436 with ECE 0.239 when it is in the performance, and confidence doesn't drop | 🔬 |
| [The listening expression: what face should the person being spoken to wear](#expressions-across-a-whole-dialogue-the-listening-expression-fails-flicker-doesnt) | Not self-contained (the reaction depends on the listener's goals and relationship, which aren't in the state) | 0.403-0.431, **failing to beat always-neutral at 0.437**; handing it a **perfect** character-emotion tracker moves it by **+0.000** (CI [−0.069, +0.067]) and only changes what it copies, from the speaker's emotion to the listener's (72%) -- overturning our own prediction | 🔬 |
| [Flicker between lines, and what context actually buys](#expressions-across-a-whole-dialogue-the-listening-expression-fails-flicker-doesnt) | — | Switch rate 0.492-0.498 against gold's 0.509 (no worse than human labels); context cuts ECE 0.119->0.050 while its +0.038 accuracy CI crosses zero | 🔬 |
| [Japanese: how far from a human](#japanese-expression-selection-one-sentence-two-oracles-and-a-human-ceiling) | Mixed (both oracles measured) | As a fourth annotator it agrees with any single human **0.459** where humans agree **0.722**; reader oracle 0.594 against a 0.722 ceiling, writer oracle 0.448 against 0.524 | 🔬 |
| [One abstention clause costs 11 points](#japanese-expression-selection-one-sentence-two-oracles-and-a-human-ceiling) | — | Same call, same state, same options: with "choose neutral when unsure" 0.483, without it 0.594 -- **wording outweighs changing the model** | 🔬 |
| [What kind of utterance is this (speech acts)](#what-kind-of-utterance-is-this-the-alternative-when-emotion-cant-be-asked) | Self-contained, but weaker than expected | 0.756 on the no-question-mark subset (punctuation shortcut 0.708, always-inform 0.639); but directive 0.680 and commissive 0.477 -- the strong class is the one a regex already handles | 🔬 |
| [Proofreading with Jev: catching wrong characters](#proofreading-with-jev-catching-wrong-characters) | Self-contained (the answer is in the sentence) | At 0.5: 67% of learner typos caught, 2% false alarms on this repo's correct sentences; a full pass over the repo's 677 sentences missed nothing; it's poor at Simplified characters, which go to a character list | 🔬 |
| [Catching self-justifying explanations (vs a deterministic scanner)](#catching-self-justifying-explanations-the-dimension-regexes-cant-see) | Self-contained (provided the criterion is written out with its exceptions) | **Corrected**: on review, the criterion's author judged all 15 of our invented "no-marker" cases legitimate; under the author's labels, criterion-only Jev false-alarms on 24 of 45 legitimate explanations (accuracy 0.60, below the scanner's 0.73). The original question is unanswered and needs real writing | 🔬 |
| [Defending the author in a real draft (pilot)](#defending-the-author-in-a-real-draft-a-pilot) | Not self-contained (it turns on judgment the author never writes down) | Labels from the author's real cuts. One paragraph: can't tell author-protecting from reader-guiding (AUC 0.59); **whole section + reader profile, asked directly "unnecessary for this reader?": 0.898**, the top four of 34 all cut by the author — but that's the best of eight dimensions; the pre-registered combination is 0.674, pending replication | 🔬 |
| [Checking a citation-audit ledger claim by claim](#checking-a-citation-audit-ledger-claim-by-claim) | Not self-contained (verdicts rest on the cited full text; the ledger keeps one quote) | Fails as a misread detector: the current audit-jev scores AUC 0.56; the primary flags 57 of 66 ok rows. But it accurately ranks where the recorded evidence doesn't cover the claim — 57 of 66 ok rows | 🔬 |
| [ICU alarm classification: testing a viral tweet](#icu-arrhythmia-alarm-classification-a-viral-tweet-tested-against-a-public-dataset) | Mixed (physiological signal needs converting to text features) | Official score 0.271, worse than "let every alarm through"; 0% sensitivity on asystole/V-tach | 🔬 |

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

### Pruning an agent's own execution history with Jev: a public debate

**What was done**: a use case unlike every other entry above — not "give Jev some content and ask it one question," but "let Jev decide which of an agent's own tool-call records can be permanently deleted." `fast-jev-compaction` (a real open-source project, 3,482 stars) replaces Claude Code's built-in summarization-based compaction with two per-call questions to Jev: should this call stay, should its result stay verbatim. After developer Tamara Tran published it, TypeSafe co-founder Diogo Almeida (`@CompleteSkeptic`) replied approvingly; independent developer Theo (t3.gg) publicly rebutted it as "a terrible compaction strategy that fundamentally doesn't understand how compaction works," flagging cache economics (cache writes cost far more than reads; deleting mid-history forces everything after it to be rewritten at full price) and lost reasoning continuity on frontier models as real risks.

**Results**: more weight than either side's tweets comes from real replay numbers other users posted to the project's own issue tracker — [issue #26](https://github.com/tamaratran/fast-jev-compaction/issues/26): replaying 8 real sessions / 256 tool results at default settings found **zero results scored above 0.3** on "should keep," because the state only shows Jev a length placeholder, never the actual content; [issue #56](https://github.com/tamaratran/fast-jev-compaction/issues/56): a synthetic reproduction where a bug-fixing error message gets judged safe to delete, but **the ranking was entirely correct** — the bug is that the two scores land on different scales and one threshold can't compare both; [issue #52](https://github.com/tamaratran/fast-jev-compaction/issues/52): rewording the questions turned a total wipeout into a defensible 40% reduction on the same data; [issue #25](https://github.com/tamaratran/fast-jev-compaction/issues/25): a new failure class — "relevance ≠ reproducibility" — a deleted historical value can't be recovered by re-running (you get today's answer, not the original), but the downstream model chose to abstain rather than fabricate, an honest positive signal. Against the cache critique, a fork implemented "sticky reduction," measured for real: it helps (10-20% savings) but hasn't yet reached the theoretical break-even point.

**What this means**: both sides' tweets were half right; the issue tracker gives a more careful answer — when the signal isn't self-contained (Jev can't see the content), judgment degrades, exactly this repo's core axis; confidence carries real relative-ranking signal, and what broke was threshold engineering, not the model guessing blindly; and deletion decisions carry a risk this repo hadn't recorded before — some content, once deleted, can't be recovered by simply re-running the tool. Full write-up (including two corrections to the originally-pasted social posts) at [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/); mirrored into a new caution in [`AGENTS.en.md`](AGENTS.en.md).

Source: [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction), [Theo's rebuttal thread](https://x.com/theo/status/2100762304862384257), [jerryfane/omp-jev-compaction](https://github.com/jerryfane/omp-jev-compaction/issues/1)

### Does sorting by a Jev probability via SQL ORDER BY hold up?

**What was done**: three DuckDB extensions and one Postgres extension all let you write `ORDER BY jev_prob(...)`, but none ships a measurement of whether that order is defensible. This independent benchmark fills that gap — gate thresholds fixed before any results were seen, using 20 Newsgroups (human-labeled, unrelated to this project) to measure calibration and ranking, then a hard probe on Amazon ESCI's human-graded product relevance, plus a separate measurement of how batch size affects the numbers.

**Results**: the easy task (20 Newsgroups, topic classification) passes all six gate conditions; the hard task (ESCI, graded product relevance) fails four of six (`jev_bool` ECE worsens from 0.045 to 0.242, inversion rate from 0.143 to 0.254). Separately: packing 40 rows into one state in a single call breaks the ranking gate outright (inversion rate worsens from 0.038 to 0.171); one row per request passes — not a wording issue, a position effect, with rows later in the batch pulled closer to 0.5.

**What this means**: a good result on an easy task is an upper bound, not a floor — exactly this repo's core axis: topic classification's answer is nearly written into the text; product relevance requires judging which facet of the query a product matches and how well, landing on the "not self-contained" side. The batch-size finding is another facet of the same phenomenon already found in `translations/jev-context-compaction-debate-zh/`'s batching/visibility issue: Jev's quality depends not just on question design but on what — and how much — goes into one request, and it fails quietly — sorting doesn't error, it's just wrong. Full write-up: [`translations/jev-orderby-bench-zh/`](translations/jev-orderby-bench-zh/) (Chinese, with an English section below the divider).

Source: [yodablocks/jev-orderby-bench](https://github.com/yodablocks/jev-orderby-bench)

### Reranking for LlamaIndex with Jev

**What was done**: LlamaIndex's Jev reranker asks, per passage, "how relevant is this to the query" (a 0-3 score), compared against plain vector retrieval (MiniLM) on the standard BEIR `nfcorpus`/`SciFact` evaluation sets, with confidence intervals.

**Results**: `nfcorpus`: MiniLM 0.340 → MiniLM+Jev 0.396 nDCG@5, +0.056 (95% CI 0.042–0.072, excludes zero), about $0.0003/query; `SciFact`: 0.629 → 0.715, +0.086 (95% CI 0.059–0.113).

**What this means**: read alongside `jev-orderby-bench` above, this draws a sharp line — that entry's hard probe asks "which facets of the query does this product match," not self-contained; this reranker's question is "how relevant is this one passage to this query," with the answer fully in the given state, self-contained. Together they map this axis's boundary within search/ranking more precisely than either alone: narrow, passage-level relevance wins; graded, multi-facet product relevance loses. Asking one question per passage instead of batching also happens to avoid the batch effect `jev-orderby-bench` measured. Full write-up: [`translations/llama-index-jev-zh/`](translations/llama-index-jev-zh/) (Chinese, with an English section below the divider).

Source: [WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)

### Jev alone doesn't beat vector retrieval for reranking, but fusing it does

**What was done**: a graded relevance evaluation over a real skill/tool catalog (33,047 items), 164 Chinese/English queries, 9,831 hand-labeled pairs, comparing a keyword ranker, BM25, bge-m3, Jev reranking, and several RRF fusion combinations. **Core design**: two independent judges (Jev and Claude Haiku) label the data separately — since Jev is simultaneously the judge and the system under test, any conclusion about Jev's own performance is read only from the Haiku-only column, removing the self-grading circularity.

**Results**: Jev alone reranking bge-m3's top-30 wins only +0.012 NDCG@10 under merged labels (CI crosses zero), and is actually **-0.028** (significantly worse) once Jev's own labeling circularity is removed; the same comparison flips sign entirely depending on the judge (+0.053 under Jev-only labels). But fusing Jev's score with bge-m3 via RRF reaches 0.864 NDCG@10, still +0.064 after removing the circularity, holding under all three judge configurations — the only positive finding in this benchmark that survives circularity scrutiny. Bonus finding: when the base candidate list is weak (a keyword ranker), Jev actually is the better reranker versus bge-m3; the real bottleneck in a candidate list is often recall, not ranking precision.

**What this means**: read alongside `jev-orderby-bench` and `llama-index-jev`, this draws a fuller picture than "self-contained wins, not-self-contained loses" — reranking an already-strong candidate list with Jev alone barely wins; treating its score as a second signal and fusing it into the existing ranking with something as simple as RRF wins reliably. The judge-circularity finding is also the cleanest quantification of that risk in this collection, echoing our own skepticism of `translations/typesafe-launch-evals-zh/`'s reference labels — the same comparison, judged by someone unrelated to the system under test, flips from winning to losing. Full write-up: [`translations/jev-search-rerank-eval-zh/`](translations/jev-search-rerank-eval-zh/) (Chinese, with an English section below the divider).

Source: [Jason Zhu (@GoSailGlobal)'s post](https://x.com/GoSailGlobal/status/2100877682972258619), [zhuyansen/jev-search-rerank-eval](https://github.com/zhuyansen/jev-search-rerank-eval)

### The cost of decomposing a judgment

**What was done**: we've recommended decomposing a judgment into atomic questions throughout this repo — this benchmark tests that recommendation directly, across four classification tasks, comparing "one question straight to the conclusion" against "12-14 narrow questions with locally fitted weights," measuring not just accuracy and cost but the false-positive rate on a deliberately chosen set of "hard benign" cases (security documentation that reads as dangerous but isn't).

**Results**: the decomposed version scored higher accuracy on three tasks (Japanese NLI's +7.03 points is the cleanest), but on hard benign cases, the false-positive rate worsened from 1.5% single-question to 37.2% decomposed — **roughly 25x** — because sub-questions like "is this obfuscated encoding" scored equally high for malicious text and legitimate security documentation, unable to distinguish intent. Cost was also 1.6-2.3x higher.

**What this means**: the decomposition recommendation isn't wrong, but "decomposition is always more accurate" is — whether it wins depends on whether the single-question judgment is genuinely weak. The original author's priority order is worth carrying directly into [`README.en.md`](README.en.md#how-can-i-use-jev-for-people): try a free baseline first, stop if a single question is already strong, decompose only where it's genuinely weak, and never let a decomposed result be the sole gate for a guardrail — treat it as a secondary opinion. Don't ask one question with many options for multi-class problems either — the bookkeeping task's 12-option single call scored only 0.3998, the worst result of any task here. Full write-up: [`translations/jev-decomposition-tradeoff-zh/`](translations/jev-decomposition-tradeoff-zh/) (Chinese, with an English section below the divider).

Source: [Jev judge call vs dimension scores (agentjournal.dev)](https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/)

### Content moderation in production (mastra-jev-moderation)

**What was done**: Mastra's built-in moderation processor parses a verdict out of an LLM's free text, and fails open when the model can't produce a parsable answer; this project replaces that step with Jev (one yes/no question, one classification question, typed output, nothing to parse), compared against the built-in version (`gpt-oss-120b`) on the same batch of real production data.

**Results**: 58 real support messages (9 hostile + 49 real questions): Jev version blocked 9/9 hostile messages, 0 of 49 real questions false-flagged, median latency 0.39-0.44s; the built-in version caught 8-9/9, also 0/49 false-flagged, latency 1.97s, roughly 4x the price.

**What this means**: typed output structurally eliminates the entire "couldn't produce a parsable answer" failure class, not a claim of better judgment — the flip side of the type-guarantee-vs-correctness-guarantee distinction in README's "not blind guessing" section: the type guarantee here solves one specific failure mode, not a promise of always being right. **Take the sample size honestly**: 58 cases, 0/49 false positives, and the author states plainly "your domain is not ours — measure on your own messages" — don't treat these numbers as universal. Full write-up: [`translations/mastra-jev-moderation-zh/`](translations/mastra-jev-moderation-zh/) (Chinese, with an English section below the divider).

Source: [CodeAlive-AI/mastra-jev-moderation](https://github.com/CodeAlive-AI/mastra-jev-moderation)

### A real production Simplified-Chinese classification task: does this news article involve Hubei?

**What was done**: a real personal project running for a year, classifying each day's People's Daily news articles for whether they involve Hubei; previously run on Gemini Flash Lite, compared against Jev the day it launched on OpenRouter using the same prompt — nearly 24,000 real accumulated items, with 1,000 sampled as a test set (500 "included" / 500 "not included").

**Results**: speed went from Flash Lite's 3s/article to Jev's 0.35s/article, nearly 10x faster; cost was about $1 for 5,000 items; agreement with Flash Lite was about 85%, with disagreements mostly on articles naming an official who once served in Hubei — Flash Lite's larger world knowledge recognizes the connection, Jev marks it "not included."

**What this means**: the most intuitive live demonstration of the core axis in this collection — the two models agree where the answer is written in the text, and disagree only where it needs outside world knowledge (a person-to-place historical connection the article never states) — currently this repo's most direct evidence for the outside-knowledge failure mode, hit and correctly diagnosed by an ordinary user in a real application; our own synthetic history suite (`suites/history-recall-context/`) didn't reproduce it once its typos were fixed — it answered the clean obscure question correctly — so together they read as "it isn't ignorant, but you can't tell in advance what it knows." The 0.35s/item figure happens to exactly match ThaiExam's, an unplanned cross-validation. **Take honestly that this isn't a formal benchmark**: no ground truth, the comparison baseline is another LLM, and 15% disagreement isn't the same as a 15% error rate. Also the first Simplified-Chinese, real production-scale case in this collection. Full write-up: [`translations/libukai-hubei-news-classification-zh/`](translations/libukai-hubei-news-classification-zh/) (Chinese, with an English section below the divider).

Source: [libukai's post on X](https://x.com/libukai/status/2100984923926728920)

### The viral ad-breakdown tweet: can Jev actually read color and style from a Gemini embedding?

**What was done**: a viral tweet claimed Jev broke down 724 real ads (37 brands, 9 cents) in 40 seconds; since Jev only takes text, not images, the original poster added "gemini pipeline with embedding," and Grok filled in the details on the spot: Gemini vision produces OCR text plus a Gemini Embedding 2 3072-dimensional float vector, both fed as `state` to Jev, letting it read visual semantics directly. We checked whether that explanation holds up.

**Results**: Grok's inference has a real technical flaw — an embedding vector only carries semantics within its own trained vector space (via similarity operations, or fed to a model jointly trained on that same space); nothing indicates Jev was jointly trained on Gemini Embedding 2's space, so serializing floats into text gives Jev only digit tokens. `@alaamurad` in the same thread asked the right question ("why not just have Gemini return the output directly?") and got no answer. Independently, we found a real team (`Nishfleet/0509`) that planned its own integration after seeing the same tweet, skipping embeddings entirely in favor of "convert to text first, then let Jev judge" — and insisting on a hand-labeled calibration benchmark before shipping.

**What this means**: the performance numbers (724 ads/40s/9 cents) aren't particularly suspect, matching Jev's known profile; but the technical detail of "how Jev is made to understand visual elements" currently has no credible answer — Grok's explanation was generated on the spot under questioning, not stated by the original poster or any documentation, a textbook case of an AI confabulating a plausible-sounding explanation for a black box — the more specific it sounds, the more convincing and the less true. The independent team's real engineering record happens to confirm the principle we recently added to `AGENTS.md`: convert to text first, don't feed in an undecoded vector. Full write-up: [`translations/jev-ad-breakdown-embedding-claim-zh/`](translations/jev-ad-breakdown-embedding-claim-zh/) (Chinese, with an English section below the divider).

Source: [Matthew Berman's post](https://x.com/TheMattBerman/status/2100654891756589230), [Nishfleet/0509's internal tickets](https://github.com/Nishfleet/0509/issues/3606)

### You got Jev, now what? A hype-free landing list

**What was done**: a Chinese-language article with unusually high methodological discipline — explicitly excluding Jev-imitating alternative models and ideas with no running evidence, organizing what actually shipped by use case; the author also personally tried wiring Jev into daily tools, four attempts, four honestly-reported failures; then ran two formal tests: having Jev self-assess 217 Jev-related projects' real usability, and validating confidence calibration across 300 judgments.

**Results**: all four failures (a context-compaction plugin, model routing to save quota, "AI flavor" detection, deciding which videos to delete) came with honestly reported root causes — including "the compaction plugin stripped all content to fit the 32K limit, leaving Jev only tool names and lengths," which **independently converges on the exact same conclusion** we dug out of a GitHub issue in `translations/jev-context-compaction-debate-zh/`. Self-assessing 217 projects, only 15 were judged genuinely usable today, 14 of them framework-level integrations, not applications. Of 300 judgments, the 255 made at 90%+ confidence were **all correct**; real Shanghai-measured median latency was 0.7s but the worst case only 1.5s, against a lightweight LLM control (Qwen 3.8 Flash) with a similar median but a 32-second worst case — "Jev's win is the absence of a long tail, not raw speed."

**What this means**: three specific numbers in this article (the official 68% accuracy figure, jev-ultrafast's 9.5→7.1s, and the compaction plugin's root cause) each independently match entries already collected in this repo — the highest convergence of any source we've verified. We re-tested the "no long tail" finding ourselves at small scale, see [`Latency distribution`](#latency-distribution-median-vs-tail) below. Two genuinely new findings were folded directly into `README.md`'s practical guidance: **under subscription pricing, the marginal cost is already zero, so adding Jev only adds latency without saving money**; and "fast" really means **no long tail, not a leading median**. Full write-up: [`translations/jev-benchmark-article-huangserva-zh/`](translations/jev-benchmark-article-huangserva-zh/) (Chinese, with an English section below the divider).

Source: [huangserva's post on X](https://x.com/servasyy_ai/status/2101132667056185544)

### Praise vs. sarcasm (dedicated public benchmark)

No one appears to have published a dedicated public benchmark for Jev's sarcasm/irony detection specifically — we tested this ourselves (see below), but that's our own small test, not an independent third-party benchmark. This is an open slot you could fill: find or publish one, then translate/organize it into [`translations/`](translations/).

---

### Jev as an agent judge (LangChain)

**What was done**: LangChain asked whether agent evaluation has a third option beyond hand-written code and LLM-as-judge. They built a weather agent with their own Deep Agents, defined five cases, **ran the agent once per case and froze the complete output**, so every judge saw the same fixed runs and only the judge changed; each judge scored them 100 times, with one human reviewer providing the oracle.

**Results**: pass/fail accuracy — Jev 100%, Terra 99.8%, Luna 96.4%, Claude Sonnet 4.6 80.0%; mean variance of the continuous score — Jev 0.0000149, 92 to 913× lower than the three LLM judges; $0.00035 and 0.44 s per call, $0.34 for the whole run against $28.17 for Claude.

**What this means**: the method is worth copying — frozen runs, identical inputs, and keeping "agrees with the human" separate from "agrees with itself." But **it proves much less than the headline suggests**: the sample is 5 items × 100 repeats (not 500 items), the oracle is a single reviewer, and reading the code shows **none of the three LLM judges had a temperature set, so they ran on their providers' default sampling** — part of the variance gap comes from that setting. The Jev version wasn't recorded either. The direction fits this repo's core axis: everything needed to judge an agent run is already in the state. Full write-up and all three caveats: [`translations/langchain-jev-as-judge-zh/`](translations/langchain-jev-as-judge-zh/).

Source: [`translations/langchain-jev-as-judge-zh/`](translations/langchain-jev-as-judge-zh/)

---

### An agent's small internal decisions: routing, skill selection, action choice (hermes-jev-skills)

**What was done**: [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) (MIT) hands an agent's small internal decisions to Jev — which model answers this turn, which skill to load, which element to click next — and measures each one.

**Results**: on a 379-skill catalog, skill selection's first stage alone sent "click through the checkout flow in the browser" to `dogfood` at 0.96 confidence, and 0.94 on the repeat — **wrong both times**. Adding a second request (one `needs_skill` plus one Noul per finalist) took confident-wrong picks from 2 to 0 over 28 cases, at a 489 ms median. Action choice went the other way: over 31 labelled cases run five times, the current single 0.65 confidence floor produced **zero wrong actions**, so the second question they tested ("does any candidate match the goal at all") was **not adopted** despite carrying real signal (no-answer cases top out at 0.43-0.45 while everything else starts at 0.61) — used alone as the gate, it clicks the one wrong button in every run.

**What this means**: routing, skill selection and action choice all sit on the self-contained side of the core axis — the candidates are on the screen, in the catalog, in this turn's text — the same shape [`browser-automation.en.md`](browser-automation.en.md) converged on. The new thing here is those two confident-wrong picks: **a floor only sees how sure the answer is, and this one was sure.** It's the cleanest third-party instance of confident-wrong we've collected, caught on a shipping product's decision path. The author notes that the expectations were written by the same hands running the eval, and that the floor was calibrated on the same cases. Full write-up and our four caveats: [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/).

Source: [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)

---

### Compaction and handoffs: measured, then Jev was removed (hermes-jev-skills)

**What was done**: the same repo measured using Jev to pick which transcript turns survive into a handoff capsule. Seven real working sessions (12-194 turns, 25,000-118,000 characters, all with heavy tool use), a 15-question recall exam each, 104 of 105 questions answerable by an oracle holding the whole transcript; every arm writes the same 400-word capsule with the same writer.

**Results**: the Jev arm scored **37.5%** closed-book against **48.1%** for a plain last-24,000-characters tail — **4 questions won, 15 lost**. What shipped afterwards is the whole dialogue with a 1,200-word budget and no Jev at all: **58.7% / 75.0%**. Two "obviously right" improvements were also measured, and both made it worse.

**What this means**: this is the map's first instance of a third party measuring Jev on a task and then removing it — and its failure mode differs from the one we had already recorded. In [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/) the state carried only length placeholders, so the content was never exposed. Here the state was complete and **Jev's judgement really was good**: given the same number of marks, its picks beat recency 11 questions to 4. What lost is the shape of the question — a kept turn still survives only as its first 400 characters, while five of the seven sessions average 1,400-7,400 characters a turn, so **no choice of turns recovers what clipping throws away**. The lesson: after rewriting a task into a shape Jev can answer, ask once more whether that shape can still do the original job. Quote the per-question 4-won-15-lost rather than the two averages — the author measured that prompt wording alone moves about 7.7 points, and these two percentages differ by 10.6. Full write-up and caveats: [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/).

Source: [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)

---

### HA-Jev: question-writing rules measured against the live API in a Home Assistant integration

**What was done**: [AboveColin/HA-Jev](https://github.com/AboveColin/HA-Jev) (MIT) wires Jev into Home Assistant, and its author measured question wording, latency, batching and cost against the live API — opening with the noise floor: repeated runs of a cell wander by about 0.15, so "treat the gaps as the finding rather than the digits."

**Results**: asking whether the laundry is finished, the power reading alone gave +0.21 separation; putting "under 5 W means idle" in the question's background raised it to +0.60; letting the template do the comparison and hand over only "it's idle" gave +0.69; both together +0.68 — they don't stack. The same rule sentence placed in the state instead of the question was worth about half. Three questions in one request took 712 ms, a hundred took 714. Structured option definitions matched flat strings at 12/15 on five ambiguous cases × three runs. Two real failures besides: with several questions answered at once, the code trusted the 0.41 answer over the 1.00 one and turned on every light in the house; offered a room with nothing controllable in it, the model answered the question right at 0.98 and named a place the agent couldn't act.

**What this means**: it's quantitative evidence for the core axis in a second independent domain — the chess finding that code-computed facts in the state matter most had one source; this measures the same thing on sensor readings and sizes it at roughly triple the separation. Its latency (250–580 ms warm, 700–900 ms cold) also independently matches our own latency suite. But no raw responses are published, samples are small, and it's one author. Full write-up: [`translations/ha-jev-home-assistant-zh/`](translations/ha-jev-home-assistant-zh/).

Source: [`translations/ha-jev-home-assistant-zh/`](translations/ha-jev-home-assistant-zh/)

---

### jev-mcp (blakestone-x): definitions, ordering and calibration on production data

**What was done**: [blakestone-x/jev-mcp](https://github.com/blakestone-x/jev-mcp) (MIT; not the same project as the jkudish/jev-mcp in [`browser-automation.en.md`](browser-automation.en.md), despite the name) wraps Jev as an MCP server, and its author measured option definitions, ordering, calibration and comparison on a field-service company's production data.

**Results**: bare label names 64.5%, a one-line definition per label 81.0%, adding "not for" and examples 84.5% (tokens 1,689 to 4,745). Reversing the option order flipped 32 of 200 answers; flipped items averaged 0.42 confidence, stable ones 0.81. On clean labels, confidence 0.8–1.0 agreed 95% and below 0.6 was near a coin flip; one label set that was wrong as often as the judgment flattened the calibration curve. With both amounts in the state and the question "which is larger," 64 of 64.

**What this means**: "no definition to one sentence: +16.5 points" is the most direct evidence we have that **you have to define the thing before Jev can judge it**, with further detail only a marginal gain (consistent with HA-Jev's "structured definitions made no difference"). It doesn't contradict HA-Jev's "it won't apply a threshold": it can compare two values in front of it; don't expect it to apply a threshold the question never states. Option-order bias is new to the map in quantitative form, and the flips concentrate in low confidence, so a confidence gate already catches most of them. But the data isn't public and label quality isn't described. Full write-up: [`translations/blakestone-jev-mcp-zh/`](translations/blakestone-jev-mcp-zh/).

Source: [`translations/blakestone-jev-mcp-zh/`](translations/blakestone-jev-mcp-zh/)

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

**What was done**: Traditional-Chinese history multiple-choice questions — (1) a commonly-known fact, no context; (2) an obscure fact, no context; (3) the same question as (2), with a supporting passage included — each asked three times; plus two unscored diagnostics re-asking the earlier version's two questions with only the typos fixed. The goal was isolating "bare memory" from "reading comprehension given supplied text."

**Results**: (1) the common fact at 1.00 confidence, correct; (2) the obscure fact at 0.87 with no passage, correct; (3) 1.00 once the passage was supplied. **This section's earlier claim — "confidently wrong on a common-knowledge question at 0.90, the single most important counter-example in this repo" — was wrong and has been withdrawn**: that item's correct option was misspelled by us (康熙→康燕), and with only the typo fixed it no longer picked the wrong answer; the earlier version's other item, "7th Qing emperor," has no single answer because counting conventions differ, and stayed near-flat after the typo fix (confidence 0.07–0.13). The typos and README mis-pairing were reported by a reader in [issue #2](https://github.com/Zaious/jev-capability-atlas/issues/2); the counting ambiguity we found while re-checking. **The lesson that survives is a different one: when `state` itself is wrong, it doesn't flag that something's off — it still picks confidently.** The outside-knowledge risk is still real, but you can't tell in advance whether it knows; three scored items can't quantify how broad its knowledge is.

Source: [`suites/history-recall-context/`](suites/history-recall-context/)

### ICU arrhythmia alarm classification: a viral tweet, tested against a public dataset

> ⚠️ This is a classification exercise on a public academic dataset, not clinical validation, and not recommended for any real patient-care decision — full disclaimer in the suite's README.

**What was done**: a viral Japanese tweet claimed Jev could judge acute vital-sign deterioration more reliably than hospital monitor alarms, with no code or data attached. We reconstructed a simplified, honest version of that claim on a recognized, authoritative public dataset — PhysioNet/CinC Challenge 2015 (750 ICU alarm recordings, 5 arrhythmia types including extreme bradycardia) — stratified-sampling 30 records. Feature extraction was deliberately kept naive (heart-rate median/IQR plus a crude noise flag, no signal-quality gating or morphology features), independently written using only MIT-licensed `wfdb`/`neurokit2`.

**Results**: the official score (a suppressed true alarm costs 5x) was **0.271** — worse than the do-nothing "treat every alarm as real" baseline (0.39), and far behind a published open-source baseline's naive ML model (0.65) and full pipeline (0.73-0.81). Broken down: **sensitivity was 0% on both life-critical categories, asystole and ventricular tachycardia**; bradycardia/tachycardia/fibrillation did comparatively better (33-67%).

**What this means**: the failure maps precisely onto what the feature set is missing, not random degradation — asystole's criterion is "no heartbeat for ≥4s," which a 30-second-window median heart rate averages into invisibility; V-tach's criterion is fundamentally about QRS morphology, not rate, and this feature set carries no morphological information at all. The three better-performing types are exactly the ones where the numeric value of heart rate itself is the diagnostic signal — again, this repo's core axis: when `state` lacks what a judgment needs, Jev can't conjure it. Confidence on the wrong answers stayed in the 0.14-0.51 range, with no "confidently wrong" pattern. **The conclusion isn't "Jev can't be used for physiological signal classification" — it's that the tweet's claim doesn't survive an honest reconstruction, and the reason is traceable specifically to naive feature extraction, not the model.** Full methodology, the NeillWhite baseline citation, and honestly stated limitations are in the suite itself.

Source: [`suites/icu-alarm-classification/`](suites/icu-alarm-classification/) (original claim: [@roiyaruRIZ's post](https://x.com/roiyaruRIZ); comparison baseline: [NeillWhite/icu-false-alarm-reduction](https://github.com/NeillWhite/icu-false-alarm-reduction))

### Latency distribution: median vs. tail

**What was done**: verifying the finding in [the article entry above](#you-got-jev-now-what-a-hype-free-landing-list) that "Jev's real win isn't median speed, it's the absence of a long tail" — 30 short Chinese sentences, the same Noul question each time, recording each real call's wall-clock time.

**Results**: the receipt of record (2026-09-22, one warm-up call made first and excluded from the stats) has a median of 247.0ms (within the official 0.07-0.5s spec), p95 280.8ms, max 313.5ms, with all 30 calls in 208–314ms and no outlier; the warm-up itself took 699.3ms. The older 2026-09-19 run counted the first call, and its only outlier (667.9ms) was exactly that call. Probabilities differed by at most 0.02 between the two runs.

**What this means**: an independent replication of "no long tail" from our own network environment — the older run's guess that the slow first call was connection-setup overhead is now directly confirmed by splitting out the warm-up; in practice, expect the first request after startup or idling to be 2–3× slower. **Honest limitation**: N=30 is far smaller than the original article's 300, and we ran no side-by-side comparison against another cheap LLM, so this only verifies "Jev itself is stable," not the other half of the claim. Full write-up: [`suites/jev-latency-distribution/`](suites/jev-latency-distribution/).

Source: [`suites/jev-latency-distribution/`](suites/jev-latency-distribution/)

### A stage-one filter: which half of a two-stage pipeline should Jev own

**What was done**: a real, running personal knowledge pipeline captures a batch of content nightly; stage one decides per item whether to hand it to an LLM agent for deep processing, discard it, or park it — and stage one is currently an agent reading every item, which is where the cost and latency sit. Using 15 real historical cases from the pipeline's own registry (real titles/URLs/dispositions), we tested what happens with Jev in that slot.

**Results**: the real output isn't a hit rate — it's **three rounds of question-design iteration where none of the three failures was about the model's judgment**. (1) One three-way Choice with criteria written from the documented rules: Jev chose "handle immediately" 47% of the time against a real base rate of 4.3% — the question never conveyed the base rate. (2) Adding the real per-topic "why is this watched at all" reason to `state`: both ends improved sharply (both genuine "immediate" cases correct, 5 of 6 discards correct), but the middle option was chosen 0 times out of 15 — two concrete option descriptions squeeze out a vague third. (3) Replaced with two independent Noul questions guarding the two expensive extremes (threshold 0.75), everything else routed to a bounded human batch review: 2 immediate triggers, 1 discard trigger, 12 to review; re-running a day later reproduced identical routing (probabilities within ±0.03).

**What this means**: **asymmetric cost belongs in the routing design, not in the criteria prose** — a wrong "handle immediately" burns human attention, a wrong "discard" loses content permanently, a wrong "park" costs almost nothing; packing three differently-priced decisions into one three-way question asks the model to dodge three kinds of error at once. Separately, both "false" immediate-triggers (an upstream deprecation RFC, and a major protocol revision historically scored 69 against a 70 threshold) look more like catching the old policy's conservative blind spots — **historical labels are one policy's output and shouldn't be treated as ground truth**. That question design outweighs model choice is the same lesson as the third-party issue #52 recorded in `translations/jev-context-compaction-debate-zh/`. Full methodology and limitations: [`suites/stage1-triage-filter/`](suites/stage1-triage-filter/).

Source: [`suites/stage1-triage-filter/`](suites/stage1-triage-filter/)

### Jev vs Laya: a head-to-head on identical inputs

**What was done**: the open-source Laya (Apache 2.0, a BERT-style encoder plus a decision head) went viral as "more accurate than Jev, 3× better calibrated, 7× faster," but the Jev numbers in its table are quoted — it has no Jev API access. We sent the same `state` and questions to Jev and to local Laya on two sets: the typed-decisions test split (400 cases / 2,000 decisions — the dataset behind Laya's headline win) and MASSIVE intent classification (100 utterances each in Traditional Chinese, Simplified Chinese and English, human labels, built Laya's own way). Metric definitions are copied from Laya's own evaluation script, and we reproduce Laya's published numbers.

**Results**: on typed-decisions, Jev (never trained on these workflows) scores 0.736; Laya's general checkpoints 0.35–0.36, **below the 0.484 input-blind baseline**; only the checkpoint fine-tuned on this dataset's train split, at 0.766, beats Jev — by 3 points (95% CI 1 to 5) — while its calibration error of 0.213 is five times Jev's 0.041. On MASSIVE, Jev scores 0.93 / 0.94 / 0.92 (zh-TW / zh-CN / en); Laya's best checkpoint 0.61 / 0.65 / 0.82. Given Traditional Chinese, Laya's English checkpoint is 0.46 accurate at 0.98 mean confidence.

**What this means**: "Laya beats Jev" holds only for a fixed workflow, with training data, compared on its own distribution — and it wins on accuracy while losing on calibration. For new tasks, tasks without training data, or Chinese, today's Laya isn't a Jev replacement; its real value is self-hosting, data that never leaves the machine, and fine-tunability. Speed wasn't tested (Laya ran on a loaded CPU), and the dataset's teacher is an undisclosed model that may share lineage with Jev — full limitations in the suite README.

Source: [`suites/laya-head-to-head/`](suites/laya-head-to-head/)

### Virtual humans picking an expression per line: one task, both sides of the axis

**What we did**: people are shipping products and public implementations that have Jev read a line and pick the character's expression, and none of them has published a number. Rather than writing our own items we used two **existing dialogue corpora**: MELD (English Friends scripts, with turn order) and a Traditional Chinese multi-emotion dialogue set (no turn order). One Choice per line — *which expression should the avatar wear while speaking this* — 40 lines per class, each asked 3 times, 2,640 calls.

**Results**: Chinese, line only, **0.807** (chance 0.125) with ECE **0.049**; English, line only, **0.436** (chance 0.143) with ECE **0.239**; English with four preceding turns, 0.485 and ECE 0.121. The paired effect of context is **+0.049, 95% CI [+0.002, +0.095]**, winning 91 items and losing 50. Latency is p50 around 270 ms and p95 around 390 ms on all three arms, and 0.971-0.988 of items gave the same answer across all three repeats.

**What this means**: **this is not "it's better at Chinese"** — the difference is in how each corpus was labelled. MELD's annotators watched the video and heard the delivery, so part of the answer isn't in the text at all (`Where is Leslie?` is labelled fear, `Sorry.` sadness); the Chinese set was labelled from text alone. So this measures **the core axis on a single task**: 0.807 when the answer is in the text, 0.436 when it is in the performance. And it fails in the usual direction — where the answer isn't in the text it doesn't hesitate, it picks neutral at confidence 1.00. The second finding: **context buys calibration more than accuracy**, cutting ECE from 0.239 to 0.121 while adding only 4.9 points. Anyone building this should decide which oracle they mean: "what a human picks from the text" is the 0.8 regime, "what the voice actor did" is the 0.45 regime. Limitations (balanced sampling, different label sets, AI-generated lines in the Chinese set whose card disagrees with its file) are in the suite.

Source: [`suites/expression-selection/`](suites/expression-selection/)

---

### Expressions across a whole dialogue: the listening expression fails, flicker doesn't

**What we did**: the previous entry measured one line, one expression. Two further questions only show up across a whole dialogue: **what face should the listener wear**, and **how often the face changes**. So this samples whole dialogues in order — 30 MELD test dialogues of at least 6 utterances, all 357 lines, four arms, 3 repeats, 3,516 calls, on the natural distribution (45.9% of gold is neutral). The listening arm has no ready oracle, so it uses the emotion label of the listener's own next utterance as a proxy.

**Results**: the speaker's expression scores 0.639 (line only) to 0.669 (plus four turns) against an always-neutral baseline of 0.459. **The listening expression scores 0.403 and 0.431, failing to beat always-neutral at 0.437**, and 50.8-53.6% of its answers are simply the speaker's own emotion. A further arm handing it the listener's **human-annotated** emotions (a perfect character-emotion tracker) scores 0.432 against 0.429 for always-neutral on those same items: paired, **+0.000, 95% CI [−0.069, +0.067], 61 won and 61 lost** — while **72%** of its answers now simply equal the listener's previous emotion. The switch rate is 0.492-0.498, **slightly below gold's 0.509**. Context cuts ECE from 0.119 to 0.050 while adding only +0.038 accuracy, 95% CI [−0.003, +0.075], crossing zero.

**What this means**: **the listening result overturns our own earlier call.** We had reasoned it sat on the self-contained side of the axis, since the trigger is in the line the other person just said. It doesn't — because **a listener's reaction is not a function of the line but of what the line means to that listener**, which needs their goals, the relationship and what happened before, none of it in the `state`; what it actually does is mirror. And the obvious fix — putting the listener's state into the state — we tested directly, and **it does nothing even at the upper bound**: it doesn't start reasoning, it just copies something else, and the shortcut it copies (repeat the listener's last emotion, 0.4145) is worse than always-neutral. 💭 The implication: let **your own code** drive the face from the state you track, rather than handing it back to the model. Conversely, **the "an AI avatar changes face every line" worry is not borne out here** — though gold itself changes every other line (it is a sitcom), so calming it down is your hysteresis, not the model's job. Finally, **context buys calibration rather than accuracy**: a second independent sample replicating the pattern (the previous entry saw ECE 0.239→0.121), with both accuracy effects too small to separate from zero. Limitations (a proxy oracle, one sitcom, neutral propping up the score) are in the suite.

Source: [`suites/expression-in-dialogue/`](suites/expression-in-dialogue/)

---

### Japanese expression selection: one sentence, two oracles, and a human ceiling

**What we did**: the earlier suites contrasted "the answer is in the text" with "the answer is in the performance" using two different corpora, which confounds annotation with the corpus itself. [WRIME](https://github.com/ids-cv/wrime) removes that: **the same Japanese post is labelled once by its own author and once each by three crowdworkers who see only the text**. Two questions in one request (`expressed` against the reader consensus, `felt` against the writer's self-report), 400 items, 3 repeats, 1,200 calls. Crucially it also yields a **human ceiling**: one reader against the other two is 0.722, and the reader consensus against the writer's own self-report is only **0.524**.

**Results**: `felt` against the reader consensus **0.594** (ECE 0.122); `expressed` against it 0.483; `felt` against the writer 0.448; `expressed` against the writer 0.381. As a fourth annotator it agrees with any single human **0.459**, where humans agree with each other **0.722**. Latency p50 256 ms, the same band as the English and Chinese suites.

**What this means**: **Japanese works but sits clearly below human level** — the most concrete measurement we have of the official "CJK is weaker" note, and the Chinese suite's 0.807 cannot be carried over to it. What matters more is the distance from the ceiling: 82% on the reader oracle and 86% on the writer oracle, so **both land at roughly four-fifths of what a person achieves**, which means the writer-oracle score is low mostly because **people can't do it either** (three humans reading the text manage 52.4%). That fills the gap the MELD suite left, where we claimed the answer lived in the performance but had no ceiling to prove it. **The most practical finding is the third**: same call, same state, same options — the question carrying "choose neutral when unsure" scored 0.483 while the one without it scored **0.594**, an 11-point gap, because neutral is only 2% of the oracle and our own clause pushed the model toward an answer that is almost never right. **An abstention option has to match how often your oracle actually uses it.** Limitations (SNS posts rather than dialogue, Plutchik's 8 is not an expression menu, our own single-label derivation) are in the suite.

Source: [`suites/expression-japanese/`](suites/expression-japanese/)

---

### What kind of utterance is this: the alternative when emotion can't be asked

**What we did**: the three expression suites converged on "what the speaker was feeling" being unanswerable from text (human ceiling 0.524). This suite tests the alternative shape we proposed ourselves — **and exists to falsify it**: don't ask about emotion, ask what kind of utterance this is (inform / question / directive / commissive) and let code map the act onto a gesture. 500 DailyDialog test utterances, two arms, 3 repeats, 3,000 calls.

**Results**: **the baseline is the point** — a rule that answers "question" on a trailing question mark and the majority class otherwise already scores 0.708, so overall accuracy is meaningless. The real test is the 355 items without a question mark: **0.756 with context and 0.701 without, against always-inform's 0.639**. The context effect is **+0.055, 95% CI [+0.024, +0.087]**. Per class: question 0.856, inform 0.856, **directive 0.680, commissive 0.477**. A 0.9 threshold covers 68.9% at 0.865.

**What this means**: the alternative **half survives**. It genuinely isn't punctuation (11.7 points clear of the baseline), and "what kind of utterance" is far more readable than "what was the speaker feeling". But we predicted the 0.8 band and got 0.70–0.76 — and **what it does best is question, which a regex already handles, while the weakest classes are exactly the requests and promises that would drive interesting gestures**. One clean gain: **this is the first of the four suites where context actually bought accuracy** (a CI cleanly excluding zero) — 💭 because a speech act is defined relative to the previous turn while an emotion is not. Limitation: DailyDialog publishes one label per utterance, so there is **no human ceiling** and we cannot say whether 0.756 is good. Implementation advice is collected in [`virtual-character-expressions.en.md`](virtual-character-expressions.en.md).

Source: [`suites/speech-act-classification/`](suites/speech-act-classification/)

---

### Proofreading with Jev: catching wrong characters

**What was done**: this repo was bitten by two kinds of typo itself — Simplified characters inside Traditional text, and real characters used in place of the right one (皮帝, 康燕, 金住). The first kind goes to a deterministic character-list check; the second can't be caught by any list, so we tested whether Jev can serve as a second opinion: one sentence as the `state`, asking "is there a wrong character?" Positives are real learner typos from the SIGHAN 2015 Chinese Spelling Check test set (originally Traditional; the open copy had been converted to Simplified, so we converted back and kept only pairs whose typo positions survived); negatives are the same test set's "clean" sentences and 152 correct sentences from this repo.

**Results**: at a 0.5 threshold it catches 67% of learner typos with only 2% false alarms on this repo's correct sentences (3 of 152, each checked by hand and typo-free); all three of our own real typos are caught (0.96, 0.95, 0.68). Scanning all 677 sentences in the repo at the same threshold flagged 16: 3 deliberately quoted old typos in correction records, 13 false alarms (about 1.9%), and no missed typo. Asking whether Simplified characters are mixed in is unreliable — a corrected sentence scored as more suspicious.

**What this means**: 💭 it holds up as a non-blocking review tool that asks a person to take a look, now shipped as `scripts/zh-check/proofread_jev.py`. The division of labour is the one this repo keeps recommending: the deterministic part (Simplified characters) goes to code, the feel-for-language narrow judgment (wrong characters) goes to Jev, and whatever it flags goes to a person. Limits: SIGHAN's typos are mostly sound-alikes, not quite the shape errors AI generation produces, of which we have only three; SIGHAN's "clean" set hides unlabelled typos, so its false-alarm rate is only an upper bound.

Source: [`suites/zh-proofreading/`](suites/zh-proofreading/)

---

### Catching self-justifying explanations: the dimension regexes can't see

**What was done**: 60 Traditional-Chinese paragraphs we wrote ourselves in five strata (self-justifying with or without a grammatical shape, legitimate explanations with or without one, plain paragraphs), labels frozen and pushed before any run. Three arms: the deterministic scanner from the maintainer's private tool babel-antiai, Jev with the one-sentence test alone ("delete it — can the reader still make the same decision? if so, delete it"), and Jev with one added sentence saying three kinds of legitimate explanation don't count. Three repeats each.

**Results**: of 15 self-justifying paragraphs with no lexical marker, the scanner caught 0 and the Jev arms 15 and 12; on 10 legitimate explanations that use a shape, the scanner false-alarmed on 7, criterion-only Jev on 4, Jev with exceptions on 0. Overall accuracy 0.48 / 0.85 / 0.93, Jev's AUC about 0.98. The three paragraphs lost once the exceptions were added were all explaining to experts what they already know.

**What this means**: 💭 checking text against a **defined** writing criterion is something Jev can do — including the kind a regex structurally can't see. Given only the criterion it treats every explanation as suspect; writing the exceptions out nearly removes the false alarms but excuses one kind of real self-justification, because background for newcomers and basics explained to experts look the same on the page and differ only in who the reader is. **Exceptions have to be written so they meet cues in the text; naming the category isn't enough.** Limits: one annotator who also wrote the items, 10 to 15 paragraphs per stratum, and the exception list and negatives come from the same list.

**Correction (same day)**: on review, the criterion's author judged all 15 of our invented "self-justifying with no lexical marker" paragraphs to be legitimate, so the conclusion above is withdrawn. Rescored with the author's labels: scanner accuracy 0.73, criterion-only Jev 0.60 (24 of 45 legitimate explanations flagged), Jev with exceptions 0.78; Jev's AUC is still 0.95 — real self-justification does score higher — but a 0.5 threshold drags in many legitimate explanations. 💭 What remains: **handed the one-sentence test literally, Jev's judgment doesn't match the test's own author**. The original question — can Jev catch the self-justification a regex can't — is unanswered: items written from the criterion's literal wording don't look like real AI-flavoured writing; the author points to deliberation with an LLM being woven into the finished article, which needs real writing to test.

Source: [`suites/self-justify-detection/`](suites/self-justify-detection/)

---

### Defending the author in a real draft: a pilot

**What was done**: after the previous suite was withdrawn, a real draft. Of 91 sentence-level changes between the AI-assisted draft and the submitted version of the maintainer's own paper, seven removed the same thing — managing how others see the author rather than telling the reader how to read the claim (the distinction the author confirmed). Those seven, seven similar sentences the author kept, and 20 unchanged sentences were put to Jev in two wordings, three times each.

**Results**: with the author's distinction as the question, all 20 ordinary sentences scored under 0.41, no false alarms; but the seven cuts and the seven kept look-alikes didn't separate (5 flagged in each, AUC 0.59). It seems to respond to shape — a "this is not X" clarification scores high whatever it does, while the author's most typical cut, "I've drawn the line clearly; readers can judge," scored 0.40. The original criterion wording false-alarmed on 9 ordinary sentences. The scanner hit nothing in this draft.

**What this means**: 💭 whether a sentence protects the author or guides the reader rests on judgment the author never writes down, and Jev can't draw that line yet; but it works as a first filter, narrowing 34 sentences to 10 for a person and catching 5 of the 7 cuts. Seven positives: direction only.

**Round 2 (same day)**: with the state changed to the whole section plus a one-line reader profile, and the question asked directly — "is this an unnecessary explanation for this reader?" — the cut-vs-kept AUC rose from 0.59 to **0.898**; the top four of all 34 sentences are ones the author cut, and the round-1 miss "I've drawn the line clearly" rises to second. 💭 Given enough context, asking directly beats splitting into sub-questions; the practical use is ranking for the author, not thresholding (scores sit in 0.25–0.51). But it's the best of eight dimensions; the pre-registered equal-weight combination is 0.674 — it counts only if it replicates on new drafts.

Source: [`suites/self-justify-real-draft/`](suites/self-justify-real-draft/)

---

### Checking a citation-audit ledger claim by claim

**What was done**: the citation-audit ledger of one of the maintainer's papers, 66 ok and 3 misread rows (all three: the claim carries more than its evidence). Jev was given only the claim sentence and the recorded quotes, via the existing audit-jev tool and a three-question set scoped to the citation number.

**Results**: both arms catch all three misreads, but by flagging nearly everything — the primary flags 57 of 66 ok rows; the existing tool's AUC is 0.56. Row by row, the ok rows Jev scores highest are ones whose quote really doesn't cover a detail of the claim (one records only a chapter title); the lowest are near word-for-word matches.

**What this means**: 💭 the ok verdicts were made against the full text and the ledger keeps one quote as a pointer, so to Jev a misread and an ok row with thin evidence look the same — the answer is in the source, not the state. Catching misreads needs the cited passage's full text. What it does measure, evidence coverage, is useful in itself: as a pre-closing coverage check so the ledger can be re-verified by someone else later. The existing audit-jev isn't recommended for routine use.

Source: [`suites/citation-claim-evidence/`](suites/citation-claim-evidence/)

---

**Untested, contributions welcome**: multimodal input (Jev currently only accepts text, per its own docs), trading card game (TCG) AI (no public test yet; the existing chess and poker evidence and design principles are in [`analysis/jev-games-tcg.md`](analysis/jev-games-tcg.md)), composite multi-dimensional scoring in real product settings, non-English languages other than Thai and Chinese intent classification, sarcasm/implied-intent detection spanning more than two conversational turns, a dedicated third-party benchmark for praise vs. sarcasm, and **using structured behavioral events (not raw mouse coordinates) to infer user hesitation/intent in real time and decide how to intervene** (the idea comes from one repo-less tweet — [@tsuyoshi_osiire](https://x.com/tsuyoshi_osiire); PostHog's own Replay Vision feature does something similar, but via multi-modal video understanding, not plain text — read up on exactly where that gap sits before taking this on).
