🇹🇼 [中文](jev-patterns.md)｜🇬🇧 English

# Jev usage patterns: ways to use it you wouldn't think of without seeing them

This page is **organized by technique, not by domain**. The capability map answers "where does it hold up?"; this page answers "you can ask it like *that*?" — many tasks only show up as Jev candidates once you rephrase them.

Each technique gets four things: the approach, why it isn't obvious, representative implementations with their evidence, and when it fails. Inclusion bar: **at least one public, runnable implementation** — ideas alone don't qualify (see [`CONTRIBUTING.md`](CONTRIBUTING.md#inclusion-rules)). Evidence tags as usual: 🔬 our own tests, 📖 TypeSafe's official examples, 📚 third-party self-reports (not re-run by us). A measured number doesn't mean it holds on your data; demos without numbers are labelled as such.

Some representatives come from "[Jev application map: 60 cases](https://doc.laoyao.cn/j61zgy)" (its JEV-xx numbering is kept) and [awesome-jev](https://github.com/yibie/awesome-jev). Compiled 2026-09-23.

## 1. Turn "generate" into "choose among candidates"

**Approach**: code finds every possible answer first (e.g. a deliberately loose regex pulling every address or date fragment from a document), and Jev only picks one.

**Why it isn't obvious**: extraction and formatting look like "writing" tasks, so the instinct is a generative model. Recast as a choice, the answer always comes from the source text and can't be invented.

| Representative | What it does | Evidence |
|---|---|---|
| [Pre-parsed value extraction](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook) (JEV-15) | Four addresses in an email's headers; asks which one the receipt should go to | 📖 demo |
| [Date extraction](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook) (JEV-14) | Jev picks which fragments are the year, month and day; code assembles the date and checks it's valid | 📖 demo |
| [Faithful auto-formatting](https://docs.typesafe.ai/cookbooks/autoformat) (JEV-06) | Jev only decides which lines join and what kind of block each is; code does the formatting and never changes a word | 📖 demo (the example: two round trips, 10,211 tokens, 0.8 s) |

**When it fails**: if the right answer isn't among the candidates, Jev can't recover it — the candidate step must err toward over-collecting.

## 2. Navigate one choice at a time

**Approach**: break search or localization into a chain of choices: which branch at this level, which link on this page, is this passage the one that answers.

**Why it isn't obvious**: "find a spot in a taxonomy of thousands of nodes" looks like it needs to see everything at once; each step actually only needs a choice among a dozen options.

| Representative | What it does | Evidence |
|---|---|---|
| [Hierarchical classification](https://docs.typesafe.ai/cookbooks/hierarchical_classification) (JEV-16) | Walks down multi-level label trees (patent classes, product taxonomies, medical subject headings) level by level, keeping the top few branches alive | 📖 demo |
| [neo4jev](https://github.com/jexp/neo4jev) (JEV-35) | On a Neo4j knowledge graph, picks the next step among neighbouring relationships and judges whether the target is reached | 📚 demo |
| [Semantic find in long documents](https://docs.typesafe.ai/cookbooks/semantic_find) (JEV-05) | Splits clauses into line-numbered fragments and asks of each "can this answer the question?" | 📖 demo |
| [Browser automation](browser-automation.en.md) | Picks one action per step from the elements on screen | 📚 several implementations, see that page |

**When it fails**: errors compound along the path — one wrong early step and everything after is wrong; keep a few alternative paths or allow backing up a level.

## 3. Drop it into existing tools as a semantic operator

**Approach**: wrap Jev as a SQL function, a grep, a sort, or a CLI that asks one question of every function, so tools that only match literally can filter and rank by meaning.

**Why it isn't obvious**: people think "plug Jev into an agent"; fewer think of it as a command.

| Representative | What it does | Evidence |
|---|---|---|
| [sqlite3-jev](https://github.com/mattn/sqlite3-jev) (JEV-37) | A SQLite extension that calls Jev from SQL to classify each row | 📚 demo |
| [every](https://github.com/sufianetaouil/every) (JEV-33) | Asks the same yes/no question of every function in a codebase | 📚 on 20 functions the author wrote: recall 10/10, AUROC 1.000 (the author: "not a benchmark"); 1,302 functions in 3.7 s for $0.018 |
| [jgrep](https://github.com/keltokhy/jgrep) | grep where the pattern is a description | 📚 spam-text filtering on public labelled data: precision 0.87, recall 0.95, F1 0.91 |
| [jsort](https://github.com/keltokhy/jsort) | Pairwise comparisons, ordered with a Bradley–Terry model | 📚 a score gap of 1 means Jev picks the higher one about 73% of the time; a gap of 3, about 95% |

**When it fails**: ranking directly by Jev's probabilities needs care — see our write-up of the [ORDER BY verification](translations/jev-orderby-bench-zh/); for ranking, pairwise comparison like jsort holds up better than sorting raw probabilities.

## 4. Check whether two things agree — what was said vs what was done

**Approach**: put two things that should agree into the `state` together — a commit message and its diff, a support agent's promise and the execution log, a "done" claim and the actual test results — and ask whether they match.

**Why it isn't obvious**: many errors live in neither document but between them; each looks fine on its own.

| Representative | What it does | Evidence |
|---|---|---|
| [jev-belay](https://github.com/valentynkit/jev-belay) | A Claude Code Stop hook that reads the transcript for evidence and blocks turns that claim "done" without verification | 📚 100 labelled real stops: AUROC 0.976 (0.777 judging the wording alone); at the shipped threshold it blocked 8, 7 of them rightly |
| [jev-commit](https://github.com/valentynkit/jev-commit) (JEV-47) | A pre-commit hook: does the commit message match the diff? | 📚 demo |
| [jev-resilience](https://github.com/Vicente-MD/jev-resilience) (JEV-44) | Treats an HTTP 200 whose body is actually an error or a maintenance notice as a failure | 📚 demo (offline request tests only) |
| [progressgate](https://github.com/AshutoshVJTI/progressgate) (JEV-46) | Detects an agent looping on assumptions it already disproved | 📚 demo |
| [Citation support check](suites/citation-support-check/) | Puts a claim and its quote together and asks whether the quote supports it | 🔬 our own test |

**When it fails**: both things must actually be in the `state`; give one and a summary or a length placeholder for the other, and it's judging without seeing the content.

## 5. Ask the cheap question before spending on the expensive one

**Approach**: before calling a large model, waking an agent, or escalating to a pricier model, spend one Jev call asking whether it's worth it.

**Why it isn't obvious**: the cost usually sits in the large-model call that shouldn't have happened, not in the judgment itself.

| Representative | What it does | Evidence |
|---|---|---|
| [wakegate](https://github.com/shitianfang/wakegate) | Before a sleeping agent is woken by a timer or an event, asks whether it's worth a full LLM turn | 📚 21 hand-written scenarios; 253 ms median; 2 of the 11 correct wakes came only from the "unsure" band |
| [jev-router](https://github.com/gargpratyush/jev-router) (JEV-48) | Picks the cheapest model good enough for the task | 📚 demo |
| [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade) (JEV-13) | A small model extracts fields, Jev checks each one, and only failures go to a stronger model | 📖 demo |
| [Stage-one filter](suites/stage1-triage-filter/) | Two yes/no questions screen items before a large-model agent handles them in depth | 🔬 our own test |

**When it fails**: tune the gate's threshold on your own data; in wakegate's case, "wake when unsure" is what rescued two wakes that were needed.

## 6. When unsure, step back instead of stopping

**Approach**: at low confidence, don't force an answer — fall back to a coarser one, hand it to a person, or escalate to a stronger model.

**Why it isn't obvious**: the instinct is "unsure means stop"; often the answer one level up is still useful.

| Representative | What it does | Evidence |
|---|---|---|
| [Falling back a level by confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence) (JEV-18) | Industry classification of SEC filings; when unsure, report the broader parent class | 📖 in the example, a group of fine-grained labels at 40% accuracy becomes 70% reported one level up |
| [Stage-one filter](suites/stage1-triage-filter/) | Two yes/no questions guard only the two costliest extremes; everything else goes to a bounded human batch review | 🔬 our own test |
| [Confidence-threshold abstention](translations/jev-dspy-lab-zh/) | Abstains below a threshold and measures the coverage/accuracy trade-off | 📚 see that entry |

**When it fails**: calibration is a population property, not a per-item guarantee; where classes genuinely blur together it can be confidently wrong (see the README's DAIR Emotion example).

## 7. Ask many questions at once, including ones you may not need

**Approach**: send every question about one `state` in a single request, including ones you're not sure you'll use; code decides afterwards which answers to act on.

**Why it isn't obvious**: extra questions barely add latency (TypeSafe's own statement), so "ask now, decide later" is cheaper than "ask when needed."

| Representative | What it does | Evidence |
|---|---|---|
| [Speculative fan-out](https://docs.typesafe.ai/patterns/fan-out) | The official pattern write-up | 📖 |
| [Many judgments over one document](https://docs.typesafe.ai/cookbooks/parallel_questions) (JEV-03) | One request runs several judgments, classifications and scores over the same GDPR text | 📖 demo |
| [jev-torneo-animales](https://github.com/hectorlcastro09/jev-torneo-animales) | Winner-stays-on: one request asks "champion vs each of the next K challengers"; once the champion falls, the rest are thrown away | 📚 the author reports 1,999 fights in about 16 s over 64 API calls |
| [Browser automation](browser-automation.en.md) | Each step asks three questions in one call: next action, goal reached, stuck | 📚 see that page |

**When it fails**: each question is evaluated in isolation (TypeSafe's own statement) and can't refer to the others; combining answers is code's job.

## 8. Use it as features for a classical model

**Approach**: instead of making the final call, Jev answers a batch of questions per record, and the probabilities become features for a classical model like CatBoost.

**Why it isn't obvious**: people treat Jev as the judge, rarely as a feature generator whose weights your own labels decide.

| Representative | What it does | Evidence |
|---|---|---|
| [Autoresearch feature discovery](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery) (JEV-17) | Keeps proposing new questions as features and uses the model's errors to decide which to keep | 📖 demo |
| [The cost of decomposing a judgment](translations/jev-decomposition-tradeoff-zh/) | One direct question vs a dozen-plus dimensions with learned weights | 📚 see that entry |

**When it fails**: decomposition isn't automatically more accurate; that third-party test found false positives on hard benign cases shooting up (see the entry).

## 9. Re-ask and see whether the answer holds

**Approach**: ask the same question several times and treat disagreement as an extra uncertainty signal.

**Why it isn't obvious**: people read only the single confidence value; an answer that moves between repeats is itself a signal.

| Representative | What it does | Evidence |
|---|---|---|
| [Classification consistency](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook) (JEV-02) | Repeatedly classifies borderline moderation cases | 📖 share of repeats returning the same label: Jev 90.8%, several LLM settings 87.5% to 100% |
| [Yes/no consistency](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook) (JEV-01) | Several factual judgments on a car-insurance claim | 📖 demo |
| [Pure-recall trivia](suites/history-recall-context/) | Each item asked three times | 🔬 single-answer items identical across repeats; the no-single-answer item drifted and even switched options |

## 10. Turn media into timestamped text, then sweep sentence by sentence

**Approach**: turn video, audio or long content into sentence-level text (with timestamps), then ask the same question of every sentence.

**Why it isn't obvious**: Jev only reads text, so it seems irrelevant to audio and video — but captions and transcripts are ready-made text.

| Representative | What it does | Evidence |
|---|---|---|
| [jev-skip](https://github.com/valentynkit/jev-skip) (JEV-32) | Reads YouTube captions and marks sponsor segments | 📚 23 videos: catches 77% of the sponsor seconds SponsorBlock users marked, 34 s of false skips per hour, $0.0008 per video |
| [Who is the player talking to?](https://github.com/wondertwins/jev-benchmark) | Reads one speech-to-text utterance and asks each NPC "spoken to, or merely mentioned?" | 📚 F1 0.96; 0.93 on lowercase, unpunctuated transcripts with misheard names; exact-set accuracy 92% vs 64% for fuzzy name matching |
| [jevmeter](https://github.com/ChetasLua/jevmeter) (JEV-52) | Scores a video sentence by sentence and overlays it on the picture | 📚 99% on the author's own eval set |
| [jev-audio-beeper](https://github.com/santos-sanz/jev-audio-beeper) (JEV-53) | Decides word by word in a Spanish transcript what to bleep | 📚 demo |
| [Proofreading with Jev](suites/zh-proofreading/) | Asks of every Chinese sentence in this repo whether it has a wrong character | 🔬 at 0.5: 67% of learner typos caught, 2% false alarms on the repo's correct sentences |

## 11. Let another tool do the perceiving; judge its symbols or text

**Approach**: screens, sensors and speech are first turned into structured data or text by another tool (OCR, the DOM, depth maps, hand tracking), and Jev only judges what comes out.

**Why it isn't obvious**: the instinct is "images need a vision model"; but many systems already compute the signal and just don't expose it. The decision rule is in [`AGENTS.en.md`](AGENTS.en.md), "when the candidate signal isn't text".

| Representative | What it does | Evidence |
|---|---|---|
| [typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use) (JEV-30) | OCRs the macOS screen, then Jev picks the next action | 📚 on the same screenshot: $0.0002 and 0.13 to 0.38 s per decision vs $0.032 and 5.2 s for Claude Opus 5 on the bare screenshot (cost and speed, not accuracy) |
| [mobile-jev](https://github.com/droidrun/mobile-jev) (JEV-29) | Reads the Android UI and picks a tap or text input | 📚 demo |
| [jev-drone](https://github.com/RomanSlack/jev-drone) (JEV-57) | Turns the camera feed into a symbolic depth-and-segmentation scene first | 📚 demo |
| [Browser automation](browser-automation.en.md) | Reads the DOM instead of a screenshot | 📚 see that page |

## 12. Treat evaluation itself as a decision task

**Approach**: judging how well an agent run went is itself a judgment: is the answer grounded, were the tools used appropriately, does it pass? Put the trace, the final answer and the retrieved evidence in the `state` and score it with a few atomic questions, instead of having a large model write a critique that you then parse into a score.

**Why it isn't obvious**: people hand evaluation to "a smarter model" and assume a judge has to explain itself; but the evidence is already in the trace, and a judge runs tens of thousands of times a day, where slow and expensive directly limits how much you dare to evaluate.

| Representative | What it does | Evidence |
|---|---|---|
| [LangChain's Jev-as-a-Judge](translations/langchain-jev-as-judge-zh/) | Freezes five agent runs and has Jev and three LLM judges score the same inputs 100 times each, keeping "agrees with the human" separate from "agrees with itself" | 📚 matched the human on all five pass/fail items, 92–913× lower variance, $0.00035 per call; but five items, one reviewer, and the control group's sampling was never turned off (all three caveats in that entry) |
| [jev-belay](https://github.com/valentynkit/jev-belay) | The same idea, blocking turns that claim "done" without verification | 📚 AUROC 0.976 over 100 labelled real stops |

**When it fails**: a stable judge isn't a correct one — a consistently wrong evaluator produces bad feedback cheaply, at scale (LangChain says so themselves). Align it against human labels before you ship it, and keep spot-checking afterwards.

## 13. Small, unexpected uses

| Representative | What it does | Evidence |
|---|---|---|
| [unclutter](https://github.com/kitze/unclutter) (JEV-31) | A browser extension that judges which page elements are ads, promotions or newsletter pop-ups, saved as reusable rules | 📚 demo |
| [hono-jev-router](https://github.com/yusukebe/hono-jev-router) (JEV-36) | Routes HTTP requests by what they mean | 📚 demo |

## Looks possible, but don't

We've checked or tested these, and the answer is "no" or "only with great care":

- **Letting Jev decide to delete an agent's own execution history**: that's an irreversible deletion, not a judgment; see the [context-compaction debate](translations/jev-context-compaction-debate-zh/).
- **Predicting human behaviour that hasn't happened** (will this message get a reply, will this lead convert): the answer doesn't exist yet at decision time; see "Where not to touch" in [`AGENTS.en.md`](AGENTS.en.md).
- **Multi-turn strategy and inferring an opponent's hidden information**: poker and chess both show it failing; see [`analysis/jev-games-tcg.md`](analysis/jev-games-tcg.md).
- **Knowledge it has to remember on its own**: you can't tell in advance whether it knows; put the needed facts in the `state`.
- **Detecting Simplified Chinese characters**: a character list is more accurate and free; see [Proofreading with Jev](suites/zh-proofreading/).

## Tag

💭 (grouping the techniques is our judgment; each representative's evidence is tagged 🔬 / 📖 / 📚 in the tables)
