🇹🇼 [中文](jev-variants.md)｜🇬🇧 English

# Jev variants and extensions

Within two weeks of Jev's launch, a whole crop of Jev-shaped things appeared: open-weight decision models, Qwen fine-tuned to answer Jev-style questions, compatible servers that read a local LLM's probabilities without any training, and libraries that build new operations on top of Jev. This page sorts them and marks where each "compared with Jev" number came from.

**Only Laya has been measured by us on identical inputs** (🔬, see [`suites/laya-head-to-head/`](suites/laya-head-to-head/)); everything else is self-reported by its authors (📚) and unverified by us. For the full application list see the Calibration & Research category of [awesome-jev](https://github.com/yibie/awesome-jev); this page only covers projects that are themselves a Jev replacement or extension. For how Jev, BERT and Laya differ technically, see [the README chapter](README.en.md#jev-bert-laya-what-actually-differs).

## Four questions before trusting any variant

Each of these came up for real in the Laya head-to-head:

1. **Generalist or specialist?** If it was trained on the same distribution as the evaluation data, it's a specialist. A specialist beating Jev on home turf is unremarkable (Laya's specialist: +3 points); an unseen task is a different story (Laya's generalist: below an input-blind baseline).
2. **Who measured the Jev column?** It's only a comparison if the same inputs and the same scoring were actually run through the Jev API. Quoted numbers can differ in sample, prompt and definition (Laya quotes Jev's ECE as 0.144; under Laya's own definition we measured 0.041).
3. **Are the confidences shipped as-is, or temperature-fitted afterwards?** If the fitting data overlaps the test data, calibration looks better than it is.
4. **Do the state and options fit?** Many variants re-read the state once per question with a 512–1,024-token budget and silently truncate beyond it; with many options, each option gets cut short. Jev allows 32k tokens for the state plus the longest question 📖.

## 1. Jev-shaped models with a decision head trained from scratch

An encoder or small model plus a decision head of their own, giving probabilities for every option in one forward pass. Small, fast and self-hostable; the shared weakness is the limited knowledge and comprehension of the base model.

| Name | Approach | Drop-in for the Jev SDK? | Compared with Jev | Tag |
|---|---|---|---|---|
| [Laya](https://github.com/NandhaKishorM/laya) | ModernBERT-large (421M total) / mmBERT-base (322M total) + decision head; Apache 2.0 | No — its own API, similar shape | Measured by us on identical inputs: general checkpoints 0.35–0.36 on typed-decisions (Jev 0.736), 0.61 on Traditional-Chinese intent (Jev 0.93); the specialist edges Jev at 0.766 on its own training distribution, with five times Jev's calibration error | 🔬 |
| [von](https://github.com/wfzyx/von) | 395M bidirectional ModernBERT "OptionMarker"; Apache 2.0 | Claims `/v1/systemone` compatibility | Its own 49-task table: Jev 96.6%, von 72.0%; von wins only on ViZDoom real-time kill counts | 📚 |
| [open-jev-deberta-v3-large](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large) | DeBERTa-v3-large (0.4B) trained on Banking77, SST-5 and BoolQ; Apache 2.0 | No | No comparison; the authors say its numbers aren't comparable to Jev's. 85.4% in-domain, 69.0% out-of-distribution, English only | 📚 |
| [nanodiff-350m-typed-decisions](https://huggingface.co/pngwn/nanodiff-350m-typed-decisions) | 350M masked-diffusion LM (LLaDA recipe) trained on its own synthetic typed-decisions data; MIT | No | No comparison; evaluated only on its own synthetic data (ECE 0.036, accuracy ~0.67). **The only diffusion-route example we found** | 📚 |
| [CUA-S1-FORMS](https://huggingface.co/cua-ai/cua-s1-forms) + [jevlike](https://github.com/vinnylarouge/jevlike), [jevbetter](https://github.com/olanotolu/jevbetter), [jevlike-esp32](https://github.com/david-cermak/jevlike-esp32) | Tiny specialist scorers (CUA-S1-FORMS: ~706K parameters, 2.8MB); jevlike is the training library, jevbetter swaps in a better encoder, jevlike-esp32 puts one on a microcontroller | No | CUA-S1-FORMS: 99.7% vs Jev's 83.6% on its own form eval — a specialist at home, and confidently wrong on field labels outside its training vocabulary (see [`browser-automation.en.md`](browser-automation.en.md)) | 📚 |

## 2. Open LLMs fine-tuned into decision models

A generative model like Qwen as the base, fine-tuned with a decision head or adapter. The base is much larger than an encoder, so comprehension and knowledge sit closer to Jev's; the cost is needing a GPU.

| Name | Approach | Drop-in for the Jev SDK? | Compared with Jev | Tag |
|---|---|---|---|---|
| [decider](https://github.com/Mapika/decider) | Qwen3.5 0.8B / 2B / 35B-A3B fine-tunes; up to 255 options and 32k tokens; Apache 2.0 | Yes — point the official SDK's `TYPESAFE_BASE_URL` at its server | [JevBench](https://benchmarkheaven.com/jev-models) public items (easy / standard / hard): Jev 1.000 / 0.986 / 0.730, decider-2b v10 1.000 / 0.972 / 0.676; on a separate Bespoke public suite decider leads slightly (0.774 vs 0.760). **The only general model here that self-reports beating Jev on a public suite**; unverified by us | 📚 |
| [kev](https://github.com/jaredpalmer/kev) | Qwen3.5 0.8B / 4B / 9B with adapters, designed after an outside reverse-engineering of Jev's architecture, trainable on a MacBook; Apache 2.0 | Yes — local `/v1/systemone` | On data it wasn't trained on, Kev-9B trails Jev by 3.5 points (0.822 vs 0.857, dev set); the author says outright that Jev's training data is unknown, so this isn't a controlled comparison | 📚 |
| [AgentJev-0.6B](https://github.com/malevrigns/agent-jev) | Qwen3-0.6B with the text-generation head removed and a candidate-scoring head added (option order doesn't matter); fine-tuned on the typed-decisions train split, so a specialist; 2,048-token context that refuses over-length input instead of silently truncating; options of one question share the state computation; Apache 2.0 on GitHub | No — its own HTTP endpoint `POST /api/evaluate`, and yes/no questions are called Boolean, not Noul | 79.25% on the typed-decisions test split vs the Laya specialist at 77.00% **re-run by the author on the same items** (+2.25 points, 95% CI +0.65 to +3.90). The 72.7% Jev row is copied from the dataset card, not measured (we measured Jev at 73.6%). Calibration error 0.169 (10 bins), about four times the 0.041 we measured for Jev. The author states it "can't be generalized into beating Jev overall"; there's no score on unseen tasks | 📚 |
| [NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B + decision heads, trained on ViZDoom, maze and Snake game data; MIT, with training pipeline, weights and dataset | No | Beats Jev on the game tasks — which it was trained on, so it's a specialist | 📚 |
| [Qwen2.5-1B-RLCD](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding) | Demo of an RLCD-trained Qwen2.5-1B | No | No comparison | 📚 |

## 3. No training: reading a local LLM's probabilities

No weight changes: map each option to the model's output probability (e.g. the logits of the option's letter) and softmax over the options. Any off-the-shelf model works and there's no training cost; the catch is that these probabilities never went through Jev-style calibration training, so you'll usually need to fit a temperature yourself.

| Name | Approach | Drop-in for the Jev SDK? | Compared with Jev | Tag |
|---|---|---|---|---|
| [jevmlx](https://github.com/bnsd55/jevmlx) | MLX on Apple Silicon, Qwen2.5 3B / 7B (4-bit) by default; can also use Ollama or vLLM (seeing only top-k logprobs); MIT | Exposes a `/v1/systemone` endpoint | Leaderboard's local rows measured on only 20 public examples | 📚 |
| [jev-local](https://github.com/us/jev-local) | Qwen3.5-9B by default, Qwen2.5-3B light build | Yes — `/v1/systemone` | Compared with published Jev outputs on 5 questions | 📚 |
| [LitJev](https://github.com/zhengxuyu/litjev) | Any Qwen, Qwen3.8-27B by default (one H100); can hand individual questions to the base model's slow thinking; Apache 2.0 | Yes — `/v1/systemone` | No identical-input comparison | 📚 |
| [open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | Any open LLM (Hugging Face + vLLM), state read once, all questions in one forward pass; Apache 2.0 | No | Says outright it isn't a Jev reproduction and doesn't compare with Jev; raw confidence runs about 5 points too high | 📚 |
| [mini-jev](https://github.com/r-ms/mini-jev) | Pre-registered study: frozen Qwen3-4B, reading option-letter logits instead of generating JSON; MIT | No | No Jev comparison; finds reading letters matches JSON generation in accuracy (0.907 vs 0.909) — the cleanest evidence for why this whole category works | 📚 |
| [openjev](https://github.com/zhihz/openjev) | Frozen Qwen3-4B, runs locally, **supports English and Chinese** | No | Says outright there's no evidence it beats Jev | 📚 |
| [Jev-shaped public API](https://x.com/ekzhang1/status/2100651678110515383) | Public API backed by Qwen3.6-35B-A3B so anyone can try the Jev question style | Same shape | No comparison; it's a single post and we haven't checked whether the service is still up | 📚 |

## 4. Extensions: new operations built on Jev

These aren't replacements — they **still call Jev**, composing its yes/no and choice answers into new operations.

- [jsort](https://github.com/keltokhy/jsort): ranks text along a plain-English criterion via pairwise comparisons and a Bradley–Terry model.
- [jlink](https://github.com/keltokhy/jlink): record linkage with the match rule written in plain English, a probability per pair, and Python, CLI, Stata and R interfaces.
- [jselect](https://github.com/keltokhy/jselect): selects source-linked evidence for a downstream AI within a token budget.
- [jgrep](https://github.com/keltokhy/jgrep): grep where the pattern is a description.
- [DocJev](https://github.com/jerryjliu/docjev) (LlamaIndex): document classification and splitting.

Hundreds of other applications are in awesome-jev; the integrations this repo has checked are in [`capability-map.en.md`](capability-map.en.md).

## Variants that read images directly

Jev itself currently accepts text only — no images, audio or video (the docs say "not supported (yet)") 📖. These variants claim to take pixels directly; all are self-reported and untested by us:

| Name | Approach | Scope | Tag |
|---|---|---|---|
| [PlayJev](https://github.com/OmniJev/PlayJev) | Qwen3.5-0.8B-Base fine-tuned into a vision-language model: one 448px game frame in, a probability over that game's available moves out, with low-confidence steps handed to a search program; Apache 2.0 | Specialist: only the ten browser games it was trained on (2.2M frames) | 📚 |
| [decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) | The vision-language variant of decider: an image plus the same question format, answered directly; there's an in-browser demo built by the Hugging Face team | General question format, but the author notes it's still on the older v5 weights and being retrained | 📚 |
| [LitJev](https://github.com/zhengxuyu/litjev) | No training; reads a Qwen model's output probabilities, so a vision Qwen checkpoint makes screenshot decisions possible | Depends on the Qwen model you plug in | 📚 |
| [jevlike](https://github.com/vinnylarouge/jevlike) | Training library for small option scorers; the same scoring head can take image patches as input (with a Doom demo video) | A research starting point | 📚 |

The more common, and steadier, approach isn't having a model look at the image at all — it's **turning the scene into text or structured data first, then handing that to Jev**: [jev-drone](https://github.com/RomanSlack/jev-drone) turns the onboard camera feed into a symbolic depth-plus-segmentation scene, and its README says outright "Jev is not a vision model"; [GUI JEV](https://github.com/ZihuaEvan/GUI_JEV) has a separate vision model describe each tile of a screenshot, with Jev only choosing among the descriptions; [jev-canvas](https://github.com/gaborishka/jev-canvas) tracks a finger with MediaPipe and transcribes speech before asking Jev. It's the same idea as [`browser-automation.en.md`](browser-automation.en.md) reading the DOM instead of a screenshot; the decision rule is in the "candidate signal isn't text" section of [`AGENTS.en.md`](AGENTS.en.md).

## Datasets used to evaluate this family

- [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions): four workflows, a 400-case test split; our Laya head-to-head uses it. Gold comes from an undisclosed teacher model, so it measures agreement, not correctness.
- [JevBench](https://benchmarkheaven.com/jev-models): the public item bank decider cites, with Jev 1.13.0 scores.
- [pngwn/typed-decisions-v2](https://huggingface.co/datasets/pngwn/typed-decisions-v2), [n4ze3m/typed-decisions-synth](https://huggingface.co/datasets/n4ze3m/typed-decisions-synth): synthetic data.

## Overall judgment so far

💭 From the numbers we can see, **on Jev's home turf — new tasks you ask directly, without training — the open variants mostly still trail Jev**; nearly every win is on a distribution the variant was trained on (a specialist), or is a win on speed, self-hosting, cost, or keeping data in-house. The one general model that self-reports a small lead on a public suite is decider, unverified by us. Before switching, check whether your task is fixed and whether you have labelled data — variants start to pay off only when both hold.

Identical-input comparisons of other variants are welcome in the format of [`suites/laya-head-to-head/`](suites/laya-head-to-head/): `common.py` and `score.py` already handle the datasets and scoring, so adding another side is usually one `run_<model>.py`.

**List compiled 2026-09-22 (AgentJev-0.6B added 2026-09-23).** This space changes daily; stars and versions are whatever each repo shows now.
