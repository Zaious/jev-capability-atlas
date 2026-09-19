🇹🇼 中文｜🇬🇧 English below

# 來源紀錄

- **原始跑分/資料集名稱**：一則爆紅推文宣稱的「Jev + Gemini embedding」廣告素材拆解 pipeline（40 秒拆解 724 則廣告、9 美分），加上同串底下 Grok 對技術細節的補充解釋，加上一個獨立團隊真實的內部工單佐證
- **原始連結**：
  - [Matthew Berman（@TheMattBerman）原推文](https://x.com/TheMattBerman/status/2100654891756589230) —— 效能宣稱的出處
  - Grok 在同一串底下對「Jev 不支援圖片輸入，怎麼拆解廣告」的技術解釋（同一推文串的回覆，查無穩定的個別回覆連結，原文由 repo 維護者逐字轉貼提供）
  - [Nishfleet/0509 內部工單 #3606](https://github.com/Nishfleet/0509/issues/3606)、[#3537](https://github.com/Nishfleet/0509/issues/3537)、[#3531](https://github.com/Nishfleet/0509/issues/3531) —— 一個獨立廣告追蹤系統團隊看到同一則推文後，自己規劃的 Jev 整合方案，公開可見
  - [stealads.ai](https://stealads.ai/) —— 查證用，確認官網無對應技術文件
- **整理者**：本 repo 維護者
- **整理方式**：讀完整串貼文原文（使用者逐字轉貼提供），查證 stealads.ai 官網有無技術文件、查證 Matthew Berman 個人 GitHub 帳號既有 repo 是否相關，用 GitHub 搜尋找到 `Nishfleet/0509` 的內部工單佐證

## 查證限制

X 平台內容同樣沒有工具能直接自動抓取核對（跟本 repo 處理 Theo／Diogo Almeida／libukai 幾則推文時遇到的限制一樣）——原文由 repo 維護者本人在對話中親自轉貼、逐字提供，不是我們自己爬到的，記錄在這裡供回頭查證。

---

# Source record (English)

- **Original benchmark/dataset**: a viral tweet's claimed "Jev + Gemini embedding" ad-creative breakdown pipeline (724 ads in 40 seconds for 9 cents), plus Grok's technical explanation in the same thread, plus a real internal engineering ticket from an independent team
- **Original links**:
  - [Matthew Berman's (@TheMattBerman) original tweet](https://x.com/TheMattBerman/status/2100654891756589230) — source of the performance claim
  - Grok's technical explanation, in the same thread, answering "Jev doesn't take image input, so how does it break down ads" (a reply in the same thread; no stable individual-reply permalink found; original text pasted in verbatim by this repo's maintainer)
  - [Nishfleet/0509 internal tickets #3606](https://github.com/Nishfleet/0509/issues/3606), [#3537](https://github.com/Nishfleet/0509/issues/3537), [#3531](https://github.com/Nishfleet/0509/issues/3531) — a publicly visible internal engineering plan from an independent ad-tracking team, built after seeing the same tweet
  - [stealads.ai](https://stealads.ai/) — checked for verification; confirmed no technical documentation on the site
- **Compiled by**: this repo's maintainer
- **Method**: read the full thread (pasted in verbatim by the maintainer), checked stealads.ai for technical documentation, checked Matthew Berman's own GitHub account for a related implementation, found `Nishfleet/0509`'s internal tickets via GitHub search as corroborating evidence

## Verification limitation

No tool currently available to us can fetch and independently verify X/Twitter content directly (the same limitation hit when handling Theo's, Diogo Almeida's, and libukai's tweets elsewhere in this repo). The source text here was pasted in verbatim by the repo's maintainer during conversation, not scraped by us — recorded here for traceability.
