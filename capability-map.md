🇹🇼 中文｜🇬🇧 English below

# 能力地圖 / Capability Map

這份表格是活的——每收一組新貢獻就更新一行。判準軸見 [README](README.md)。標籤:🔬 我們/貢獻者自己測的、📚 第三方跑分、📖 TypeSafe 官方文件。

This table is living — updated with every new contribution. Axis explained in [README](README.md). Tags: 🔬 our/contributor's own test, 📚 third-party benchmark, 📖 TypeSafe's own docs.

| 任務 / Task | 軸上位置 / Axis position | 結果 / Result | 標籤 | 來源 / Source |
|---|---|---|---|---|
| AG News 主題分類 / topic classification | 訊號自足 / self-contained | 91.0% acc | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| Banking77 意圖分類 / intent classification | 訊號自足 / self-contained | 87.0% acc | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| DAIR Emotion 情緒分類 / emotion classification | 類別重疊(邊界案例)/ overlapping categories (edge case) | 48.0% acc, 信心 0.819 但常錯 / conf 0.819 despite frequent errors | 📚 | [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) |
| ThaiExam 混合科目 / mixed-subject exam | 混合(部分自足部分不) / mixed | 70.7% acc,111 個模型中段班 / mid-pack of 111 | 📚 | [thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) |
| 引用支持度判讀 / citation support-checking | 訊號自足 / self-contained | 9/12 支持、0 反駁,低信心正確對應難例 / 9/12 supports, 0 contradicts, low confidence correctly tracked hard cases | 🔬 | [`suites/citation-support-check/`](suites/citation-support-check/) |
| 反諷偵測·同句 / sarcasm, same-clause | 訊號自足 / self-contained | 12/12 對 / correct | 🔬 | [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/) |
| 反諷偵測·跨句 / sarcasm, cross-turn | 訊號自足 / self-contained | 10/10 對 / correct | 🔬 | [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/) |
| 純回憶史實題(無背景) / pure-recall trivia (no context) | 不自足 / not self-contained | 高信心答錯常識題;冷門題低信心 / confidently wrong on a common-knowledge question; low confidence on an obscure one | 🔬 | [`suites/history-recall-context/`](suites/history-recall-context/) |
| 同題有給背景段落 / same question, with context supplied | 訊號自足 / self-contained | 答對,信心 0.97 / correct, conf 0.97 | 🔬 | [`suites/history-recall-context/`](suites/history-recall-context/) |
| 瀏覽器元素選擇路由 / browser element-selection routing | 訊號自足(DOM 快照給齊+批次平行問)/ self-contained (DOM snapshot given, batched in parallel) | 比 Playwright MCP 快 1.5x、便宜 1.6x / 1.5x faster, 1.6x cheaper——機制解析見 README「為什麼瀏覽器自動化這麼強」/ mechanism explained in README's "why browser automation benchmarks so well" | 📚 | [jev-browser](https://github.com/MahmoudAdelbghany/jev-browser) |
| 稱讚 vs 諷刺(公開專門跑分) / praise vs. sarcasm (published dedicated benchmark) | — | 目前查無 / none found as of this writing | — | 這正是你可以貢獻的空白 / this is an open slot you could fill |

**還沒有人測過、歡迎貢獻的方向**:多模態(Jev 目前只吃文字,官方文件如此記載)、多維度複合評分在真實產品場景的表現、非英語語系(除泰文外)的表現、跨句以上(三輪+)脈絡的反諷/隱含意圖偵測。
