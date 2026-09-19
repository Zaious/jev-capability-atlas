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
| Praise vs. sarcasm (dedicated public benchmark) | — | None found as of this writing — an open slot you could fill | — |
| [Citation support-checking](#citation-support-checking) | Self-contained | 9/12 supports, 0 contradicts, low confidence correctly tracked hard cases | 🔬 |
| [Sarcasm detection, same-clause/cross-turn](#sarcasm-detection) | Self-contained | 12/12, 10/10 correct, including a correctly-low-confidence case | 🔬 |
| [Pure-recall trivia vs. supplied context](#pure-recall-trivia-vs-supplied-context) | Not self-contained → self-contained | Confidently wrong on a common-knowledge question with no context; confidence and accuracy both recover once context is supplied | 🔬 |
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

**What this means**: the most intuitive live demonstration of the core axis in this collection — the two models agree where the answer is written in the text, and disagree only where it needs outside world knowledge (a person-to-place historical connection the article never states) — the real-production version of the same failure mode already documented in `suites/history-recall-context/`, except this time it's an ordinary user who hit it and correctly diagnosed it themselves. The 0.35s/item figure happens to exactly match ThaiExam's, an unplanned cross-validation. **Take honestly that this isn't a formal benchmark**: no ground truth, the comparison baseline is another LLM, and 15% disagreement isn't the same as a 15% error rate. Also the first Simplified-Chinese, real production-scale case in this collection. Full write-up: [`translations/libukai-hubei-news-classification-zh/`](translations/libukai-hubei-news-classification-zh/) (Chinese, with an English section below the divider).

Source: [libukai's post on X](https://x.com/libukai/status/2100984923926728920)

### The viral ad-breakdown tweet: can Jev actually read color and style from a Gemini embedding?

**What was done**: a viral tweet claimed Jev broke down 724 real ads (37 brands, 9 cents) in 40 seconds; since Jev only takes text, not images, the original poster added "gemini pipeline with embedding," and Grok filled in the details on the spot: Gemini vision produces OCR text plus a Gemini Embedding 2 3072-dimensional float vector, both fed as `state` to Jev, letting it read visual semantics directly. We checked whether that explanation holds up.

**Results**: Grok's inference has a real technical flaw — an embedding vector only carries semantics within its own trained vector space (via similarity operations, or fed to a model jointly trained on that same space); nothing indicates Jev was jointly trained on Gemini Embedding 2's space, so serializing floats into text gives Jev only digit tokens. `@alaamurad` in the same thread asked the right question ("why not just have Gemini return the output directly?") and got no answer. Independently, we found a real team (`Nishfleet/0509`) that planned its own integration after seeing the same tweet, skipping embeddings entirely in favor of "convert to text first, then let Jev judge" — and insisting on a hand-labeled calibration benchmark before shipping.

**What this means**: the performance numbers (724 ads/40s/9 cents) aren't particularly suspect, matching Jev's known profile; but the technical detail of "how Jev is made to understand visual elements" currently has no credible answer — Grok's explanation was generated on the spot under questioning, not stated by the original poster or any documentation, a textbook case of an AI confabulating a plausible-sounding explanation for a black box — the more specific it sounds, the more convincing and the less true. The independent team's real engineering record happens to confirm the principle we recently added to `AGENTS.md`: convert to text first, don't feed in an undecoded vector. Full write-up: [`translations/jev-ad-breakdown-embedding-claim-zh/`](translations/jev-ad-breakdown-embedding-claim-zh/) (Chinese, with an English section below the divider).

Source: [Matthew Berman's post](https://x.com/TheMattBerman/status/2100654891756589230), [Nishfleet/0509's internal tickets](https://github.com/Nishfleet/0509/issues/3606)

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

### ICU arrhythmia alarm classification: a viral tweet, tested against a public dataset

> ⚠️ This is a classification exercise on a public academic dataset, not clinical validation, and not recommended for any real patient-care decision — full disclaimer in the suite's README.

**What was done**: a viral Japanese tweet claimed Jev could judge acute vital-sign deterioration more reliably than hospital monitor alarms, with no code or data attached. We reconstructed a simplified, honest version of that claim on a recognized, authoritative public dataset — PhysioNet/CinC Challenge 2015 (750 ICU alarm recordings, 5 arrhythmia types including extreme bradycardia) — stratified-sampling 30 records. Feature extraction was deliberately kept naive (heart-rate median/IQR plus a crude noise flag, no signal-quality gating or morphology features), independently written using only MIT-licensed `wfdb`/`neurokit2`.

**Results**: the official score (a suppressed true alarm costs 5x) was **0.271** — worse than the do-nothing "treat every alarm as real" baseline (0.39), and far behind a published open-source baseline's naive ML model (0.65) and full pipeline (0.73-0.81). Broken down: **sensitivity was 0% on both life-critical categories, asystole and ventricular tachycardia**; bradycardia/tachycardia/fibrillation did comparatively better (33-67%).

**What this means**: the failure maps precisely onto what the feature set is missing, not random degradation — asystole's criterion is "no heartbeat for ≥4s," which a 30-second-window median heart rate averages into invisibility; V-tach's criterion is fundamentally about QRS morphology, not rate, and this feature set carries no morphological information at all. The three better-performing types are exactly the ones where the numeric value of heart rate itself is the diagnostic signal — again, this repo's core axis: when `state` lacks what a judgment needs, Jev can't conjure it. Confidence on the wrong answers stayed in the 0.14-0.51 range, with no "confidently wrong" pattern. **The conclusion isn't "Jev can't be used for physiological signal classification" — it's that the tweet's claim doesn't survive an honest reconstruction, and the reason is traceable specifically to naive feature extraction, not the model.** Full methodology, the NeillWhite baseline citation, and honestly stated limitations are in the suite itself.

Source: [`suites/icu-alarm-classification/`](suites/icu-alarm-classification/) (original claim: [@roiyaruRIZ's post](https://x.com/roiyaruRIZ); comparison baseline: [NeillWhite/icu-false-alarm-reduction](https://github.com/NeillWhite/icu-false-alarm-reduction))

---

**Untested, contributions welcome**: multimodal input (Jev currently only accepts text, per its own docs), composite multi-dimensional scoring in real product settings, non-English languages other than Thai, sarcasm/implied-intent detection spanning more than two conversational turns, a dedicated third-party benchmark for praise vs. sarcasm, and **using structured behavioral events (not raw mouse coordinates) to infer user hesitation/intent in real time and decide how to intervene** (the idea comes from one repo-less tweet — [@tsuyoshi_osiire](https://x.com/tsuyoshi_osiire); PostHog's own Replay Vision feature does something similar, but via multi-modal video understanding, not plain text — read up on exactly where that gap sits before taking this on).
