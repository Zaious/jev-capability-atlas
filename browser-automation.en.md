🇹🇼 [中文](browser-automation.md)｜🇬🇧 English (this page)

# Wiring Jev into browser automation: an implementation guide

This page doesn't answer "is Jev a good fit for browser automation" — that evidence is already in [`capability-map.en.md`](capability-map.en.md#jev-browser-vs-playwright-mcp) and [`README.en.md`](README.en.md#a-worked-example-why-browser-automation-benchmarks-so-well); don't skip that and jump straight to the architecture. This page is for people or agents who've already seen that evidence and decided to wire it in: **how to actually connect your own system to Jev for browser control** — including the case where you already have a browser-heavy agent and want to try swapping Jev in for a piece of its decision logic.

Content here is organized from three real open-source projects' own documentation (see "Three real implementations to reference" below) — the architecture pattern and limits are direct quotes; the cross-project pattern synthesis is our own, see the tag at the end.

## Reference architecture: one call, three questions (the fan-out pattern)

Three independent projects converged on the same pattern without coordinating, which is worth treating as a starting point: **one Jev call per step, three questions over the same state**:

1. **Action Choice** — pick one from every clickable/typeable/selectable element on the current page, plus scroll/back/done.
2. **Goal-achieved Noul** — has the goal been met?
3. **Stuck Noul** — is this step stuck?

Beyond the element list, the state needs to include a short excerpt of the page's **visible text** — not just URLs and links, or the "goal achieved" question has no content to judge against (this echoes this repo's core axis: signal has to be self-contained for the judgment to be accurate). A `select` action adds one second-stage Choice for its option.

**Extract elements from the DOM directly, not the accessibility tree** — accessibility trees under-report input fields; `jkudish/jev-browser` switched to reading the DOM directly only after discovering it couldn't find DuckDuckGo's search box otherwise. This is a concrete, verifiable lesson learned, not a theoretical suggestion.

**Put stop conditions in your own code, not the model**: the agent chooses done, goal probability crosses a threshold (all three projects start at 0.85), stuck probability crosses a threshold, a step budget, or a time budget — whichever fires first stops the run. **These thresholds are starting points tuned on sites like Wikipedia and DuckDuckGo, not universal values** — recalibrate for your own site.

**Deliberately no low-confidence override**: probability split across several similar elements usually means "several are acceptable, there isn't one right answer" — not "the model doesn't know what to do." This is an easy detail to misuse: seeing spread-out confidence and reflexively adding an "escalate to a human below this threshold" guard can end up blocking perfectly normal cases. What's actually worth watching for is the goal/stuck probabilities staying stuck in a middling range without looking like a spread across reasonable options.

## The typing problem: Jev doesn't generate text, and here's a concrete fix and a concrete failure

[`README.en.md`](README.en.md#not-a-state-machine-not-blind-guessing--but-also-not-a-thinking-reasoning-model) already covers that Jev doesn't generate text, only typed decisions — here's what that constraint looks like actually implemented: when a task needs typed text (a search box, a form field), that string comes from a **separately configured small model**, unrelated to Jev itself. All three implementations use the same pattern, with similar provider-priority tables (based on which environment variable is set — `OPENAI_API_KEY` → a small GPT model, `ANTHROPIC_API_KEY` → Claude Haiku, `GEMINI_API_KEY` → Gemini Flash), and all support pointing at a local endpoint (Ollama, LM Studio, vLLM). Each call costs tens of tokens, small enough that it barely dents the overall fast/cheap profile.

**With no small model configured, this degrades to a keyword heuristic — and the cost of that degradation is quantified**: `jkudish/jev-browser` honestly documents that in this fallback mode, its generated search queries once buried the target article eight results pages deep. All three projects label this condition honestly in their trace as `via keyword-heuristic` rather than pretending it's normal operation — **when wiring your own system, either configure a real typing model to avoid this path, or make sure it's visible in your own logs; don't let it pass silently as a normal result.**

## Three real implementations to reference

### `jkudish/jev-browser` — currently the most complete reference implementation

MCP server, CLI, and an npm library, all in one package; 116 stars, actively maintained with CI. Most of the architecture detail in the two sections above comes from this project's README. Its honestly-stated limits: **up to 240 elements per step** (Jev's Choice supports up to 255 options; beyond the cap, the list truncates and the state says so); no password or file-upload fields; hover-revealed menus, keyboard actions, multi-field form sequencing, shadow DOM, and iframes are all out of scope; in its own words: "Jev is calibrated, not infallible. Treat the trace as evidence, not proof" — consistent with this repo's position throughout.

The same author also maintains a sibling project, [`jkudish/jev-mcp`](https://github.com/jkudish/jev-mcp), which extracts the same Choice/Noul judgment pattern into eight general-purpose tools unrelated to browsing (verify a claim, screen content, find/rerank by meaning, batch-classify, decide, compare passages, extract fields) — out of scope for this page, but if what you're wiring up isn't browser automation but some other judgment task, this may be a more direct starting point worth evaluating separately.

### `browser-use/jev-ultrafast` — an official integration into an existing agent framework

If you're already using [Browser Use](https://github.com/browser-use/browser-use), this is an official (not community) integration — no need to write your own loop. Benchmark numbers and honest caveats are in [`capability-map.en.md`](capability-map.en.md#jev-ultrafast-browser-use-official-integration), not repeated here; typing is likewise handled by a separate small model (`inception/mercury-2.5`, reasoning disabled).

### `MahmoudAdelbghany/jev-browser` — the source of the benchmark numbers, not an architecture reference

This project's value is its head-to-head Jev-vs-Playwright-MCP benchmark (see [`capability-map.en.md`](capability-map.en.md#jev-browser-vs-playwright-mcp)), including the important counter-finding that Jev isn't good at pure text extraction. The project itself is small (0 stars, pushed once), not a mature implementation worth copying architecturally.

**An important clarification to avoid confusion from the name collision**: this project and `jkudish/jev-browser` above are **two entirely independent, unrelated projects** that happened to pick the same name on the same day (2026-09-17). When referring to "jev-browser," always include the author's account name — don't cite the project name alone.

## A checklist for wiring this into your own system

1. First use the core axis in [`capability-map.en.md`](capability-map.en.md) to classify your task: **acting** (clicking, filling forms, navigating — a candidate) versus **pure reading** (just extracting page content — `MahmoudAdelbghany/jev-browser`'s own benchmark shows Jev is slower and more expensive here; don't misapply it).
2. Start from the fan-out architecture above instead of designing from scratch — three independent projects converging on the same pattern isn't a coincidence.
3. Configure a typing model up front instead of relying on the keyword-degradation path; if you can't yet, make sure that degraded state is visible in your own logs, not disguised as a normal result.
4. **Retune the goal/stuck probability thresholds on your own site instead of copying 0.85** — all three projects' starting values were tuned on structurally clean sites like Wikipedia and DuckDuckGo.
5. Follow the same verification flow [`AGENTS.en.md`](AGENTS.en.md#the-minimum-verification-flow-for-a-candidate-copy-our-own-process-dont-skip-it) already describes: run it once against real tasks, compare side by side against your existing approach, then decide whether to promote it — and contribute the result (good or bad) back per [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Tag

📚 (the architecture pattern, limits, and typing-model mechanism are direct quotes from three real projects' own documentation, linked in each section above; the cross-project pattern synthesis, the checklist, and the name-collision warning are our own 💭 synthesis)
