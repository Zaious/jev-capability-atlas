🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：[kerpopule/hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) 的 `evals/` 與 `docs/`——把 agent 的內部小決策（模型路由、技能挑選、記憶重排、對話壓縮、信箱分類、電腦與瀏覽器操作）交給 Jev 的一套實作，以及作者自己跑的五份 scorecard
- **原始連結**：
  - repo：[kerpopule/hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)（MIT，2026-09-18 建立；查證當下 CHANGELOG 最新為 0.19.0、2026-09-21）
  - 壓縮與交接：[`evals/compaction/results/SCORECARD-2026-09-20.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/compaction/results/SCORECARD-2026-09-20.md)
  - 技能挑選第二階段：[`evals/skill-pick/SCORECARD-2026-09-22.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/skill-pick/SCORECARD-2026-09-22.md)
  - 動作選擇的第二題：[`evals/choose-match/SCORECARD-2026-09-21.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-21.md)
  - 風險與差距門檻：[`evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md)
  - 計畫品質：[`evals/plan-quality/SCORECARD-2026-09-22-prompt-keys.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/plan-quality/SCORECARD-2026-09-22-prompt-keys.md)
  - 寫問題的方法：[`docs/writing-a-jev-question.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/docs/writing-a-jev-question.md)
- **整理者**：本 repo 維護者
- **整理方式**：用 GitHub API 抓下 README、五份 scorecard 與 `docs/writing-a-jev-question.md` 的原始 Markdown 逐份讀完，表格數字逐格抄寫。技能目錄的數量與版本以 repo 的檔案樹和 CHANGELOG 為準。查證日期 2026-09-23
- **轉載範圍**：未轉載原文全文或整段翻譯。本條是我們自己撰寫的摘要與查證：引用具體數字與方法論事實，並附原始連結；直接引述僅限標明出處的短句。原作者若認為超出合理引用範圍，請開 issue，我們會修改或移除。本條文字依 repo 的 MIT 授權釋出，被引用內容的權利仍屬原作者，見 [`NOTICE`](../../NOTICE)。

## 查證限制

- **我們沒有重跑它的任何一份評測。** 所有數字都出自作者自己發布的 scorecard 檔案。它們附了可重跑的腳本（`evals/compaction/run_eval.py`、`scripts/calibrate_skill_stage2.py`、`scripts/calibrate_choose_match.py`、`scripts/calibrate_choose_stakes.py`、`scripts/measure_plan_quality.py`），但重跑需要作者的 session 資料或一個真實的技能目錄，我們兩樣都沒有。
- **壓縮那份的原始素材不在 repo 裡**——作者寫明逐字稿、考卷與摘要都不放上來。也就是說那份的數字可以重算、但不能被外部複現。
- **「必要條件 vs 偏好」那條的一手來源我們查不到**：它出自 X 貼文（[@dsqjaffa](https://x.com/dsqjaffa)，2026-09-21），是賣產品的廠商自述，n=44、沒有逐案拆解，而我們沒有工具可以抓 X。我們只能查證到「hermes-jev-skills 的文件這樣轉述」，不能查證原始貼文本身。作者自己也標了同樣的警告。
- repo 授權是 MIT，我們仍只引用、不搬運它的程式碼。

---

# Source record (English)

- **Original**: the `evals/` and `docs/` directories of [kerpopule/hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) — an implementation that hands an agent's small internal decisions (model routing, skill selection, memory reranking, transcript compaction, mailbox sorting, computer and browser use) to Jev, plus five scorecards the author ran
- **Original links**:
  - repo: [kerpopule/hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills) (MIT, created 2026-09-18; CHANGELOG's latest at time of checking was 0.19.0, 2026-09-21)
  - compaction and handoffs: [`evals/compaction/results/SCORECARD-2026-09-20.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/compaction/results/SCORECARD-2026-09-20.md)
  - skill selection stage 2: [`evals/skill-pick/SCORECARD-2026-09-22.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/skill-pick/SCORECARD-2026-09-22.md)
  - the second question on action choice: [`evals/choose-match/SCORECARD-2026-09-21.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-21.md)
  - stakes and margin gates: [`evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/choose-match/SCORECARD-2026-09-22-stakes-and-margin.md)
  - plan quality: [`evals/plan-quality/SCORECARD-2026-09-22-prompt-keys.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/evals/plan-quality/SCORECARD-2026-09-22-prompt-keys.md)
  - writing questions: [`docs/writing-a-jev-question.md`](https://github.com/kerpopule/hermes-jev-skills/blob/main/docs/writing-a-jev-question.md)
- **Compiled by**: this repo's maintainer
- **Method**: pulled the raw Markdown of the README, the five scorecards and `docs/writing-a-jev-question.md` through the GitHub API and read each in full, transcribing the tables cell by cell. Skill counts and versions come from the repo's file tree and CHANGELOG. Checked 2026-09-23
- **Reproduction scope**: no full text or paragraph-level translation is reproduced here. This entry is our own summary and verification: it cites specific figures and methodological facts with links to the originals, and any direct quotation is limited to short, attributed phrases. If the original author considers this beyond fair quotation, please open an issue and we'll revise or remove it. Our text is released under the repo's MIT license; rights in the quoted material stay with its authors — see [`NOTICE`](../../NOTICE).

## Verification limitations

- **We re-ran none of these evaluations.** Every figure comes from the author's own published scorecards. They ship reproduction scripts (`evals/compaction/run_eval.py`, `scripts/calibrate_skill_stage2.py`, `scripts/calibrate_choose_match.py`, `scripts/calibrate_choose_stakes.py`, `scripts/measure_plan_quality.py`), but re-running needs either the author's session data or a real skill catalog, and we have neither.
- **The compaction evaluation's raw material is not in the repo** — the author states that transcripts, exams and capsules stay off it. Its numbers can be recomputed but not independently reproduced.
- **We could not reach the primary source for the "requirement vs preference" finding**: it comes from an X post ([@dsqjaffa](https://x.com/dsqjaffa), 2026-09-21), self-reported by a vendor selling the product, n=44 with no per-case breakdown, and we have no tool that can fetch X. We can verify only that hermes-jev-skills' documentation reports it this way, not the post itself. The author flags the same caveat.
- The repo is MIT-licensed; we still only cite it and copy neither its code nor its data.
