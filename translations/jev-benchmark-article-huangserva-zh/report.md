🇹🇼 中文｜🇬🇧 English below

# 拿到 Jev，然後呢？一篇剔掉虛火的真實落地清單，跟我們自己的三重交叉驗證

## 這組測什麼

Jev 發布不到一週，社群上充斥「快 200 倍」「永不出錯」這類宣稱。這篇文章做三件事：講清楚 Jev 是什麼、不是什麼；把真正跑通（有可存取的程式碼/展示/產品入口）的案例依用途分類；把水分講明白。作者自己也動手做了兩件事：先把 Jev 塞進自己每天用的工具，四次全部失敗；然後退一步做了兩輪正式測試——拿 Jev 自評 217 個 Jev 相關專案能不能用，再用 100 則中文新聞驗證信心值準不準。

## 方法論

案例分類部分：明確排除「模仿 Jev 的替代模型（不是 Jev 的應用）」跟「純觀點、教程、上架公告、沒有運行證據的構想」，只收有可存取證據的案例，依用途分成五類（agent 決策器、海量資料分類、信心值分流、即時反應展示、模擬/控制實驗），外加「已接入真實產品」這個額外分層。

自測部分：第一輪，把 60 個蒐集到的案例加上 GitHub 上另外找到的 167 個 Jev 專案，共 217 條的公開介紹餵給 Jev，讓它逐條判斷「今天能不能拿到、能不能用」，這輪同時是「海量文字分類」這個用法的實測。第二輪，造 100 條中文科技資訊，每條三道題、共 300 個判斷，事先人工標好答案，對照一個輕量大模型 Qwen 3.8 Flash，從上海端逐條串行呼叫，量測信心值跟實際正確率對不對得上，同時記錄真實延遲。

## 結果

**四次失敗，誠實記錄**：①幫 Claude Code 裝 context 壓縮外掛——裝不上，勉強跑起來的版本等同「無腦刪」，換一個對什麼都答 0 的假模型效果一樣；根因是外掛為了塞進 32K 上限，把內容全砍了，Jev 只看得到工具名跟長度。②幫 Codex 做模型路由省額度——反而多花 59%-184%，每步多等 1-2 秒；根因是中間代理把請求變重 2.5 倍，還弄丟了快取。③幫自己的稿子挑「AI 味」——快又便宜，但 62 句裡 22 句誤報，淨增價值約零。④判斷 40 個大影片哪些能刪——判 0 個能刪，純規則反而判得出 7 個；根因是看不到檔案內容，只能憑檔名猜。

**第一輪自評**：217 條裡，Jev 判定「現在可用、證據充分」的只有 15 個，其中 14 個是 pydantic-ai、LangChain、Vercel AI SDK 這類主流開發框架的 Jev 接入層，不是應用；唯一的應用是 jev-ultrafast。「已接入產品」那五個候選裡，Jev 比作者本人更保守，只認可 SPIRITT 跟 ReqLLM。

**第二輪校準與延遲**：300 個判斷裡，Jev 講「九成以上把握」的有 255 個，**全部答對**；把 80% 設成自動放行的門檻，可以放掉 89% 的請求、只錯 1 個。上海端實測中位數約 0.7 秒（比官方 0.07-0.5 秒慢），但最慢一次只要 1.5 秒；對照的 Qwen 3.8 Flash 中位數差不多，但最慢一次飆到 32 秒。準確率 94.7% 對 93.0%，花費同樣是 $0.003——官方宣稱的「便宜 40-400 倍」是跟前沿大模型比，對上輕量模型沒有優勢。

## 這代表什麼

**跟我們自己三條已收錄的條目，逐項對上**——這是這篇文章最有分量的地方：①官方 68% 準確率、參考答案是兩個模型平均，跟 `translations/typesafe-launch-evals-zh/` 查到的 67.8%、GPT-6 Astra + Claude Fable 5.1 平均完全一致；② jev-ultrafast 機票搜尋案例的 9.5→7.1 秒，跟 `capability-map.md` 收錄的官方數字（9.450→7.092 秒）逐位對上；③「context 壓縮外掛裝上去變無腦刪，根因是 state 只看得到工具名跟長度」，跟 `translations/jev-context-compaction-debate-zh/` 從 GitHub issue #26 挖出的根因（256 筆真實結果 0 筆保留信心超過 0.3，因為 state 只給長度佔位字串）是同一個發現——作者是自己動手裝外掛撞到的，不是看我們的文章寫的，兩條完全獨立的路徑收斂到同一個結論，比任何單一來源都更有說服力。

**我們自己動手驗證了其中一條，也對上了**：文中「Jev 真正贏的不是速度中位數，是沒有長尾」這個判斷，是少數不需要標準答案、成本低到可以直接自己重跑的發現——我們從自己的網路環境跑了 30 筆真實延遲量測（[`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/)），中位數 250.4ms（在官方區間內，比原文章上海量到的 0.7 秒更快），p95 只有 298.5ms，30 筆裡唯一的離群值（667.9ms）還是第一次呼叫，最合理的解釋是連線建立成本，不是隱藏的慢模式——獨立支持「沒有長尾」這個結論，雖然我們沒有同場對照 Qwen 這類輕量模型，只驗證了「Jev 本身穩」這一半。

**兩個我們完全沒討論過的新發現，值得吸收進我們自己的建議**：

1. **訂閱制殺死 Jev 的成本優勢**：Jev 的賣點是「比呼叫大模型便宜幾百倍」，但如果你本來就在用 Claude Code、Codex 這類訂閱制工具，一次額外的判斷邊際成本本來就接近零，插一層 Jev 進去只會多一層延遲、多一次出錯機會，完全沒有省到錢。這是我們核心那條軸（任務形狀）之外一個獨立的**成本情境**判準：先問「這次判斷的邊際成本本來是不是已經是零」，再決定要不要接 Jev。
2. **延遲穩定（沒有長尾）比中位數快更重要**：這點我們自己的延遲量測也支持，值得補進我們對「快」這個賣點的描述——不只是「平均起來快」，是「幾乎不會有那種讓人等到抓狂的慢查詢」，這對接進使用者可見的即時互動場景尤其重要。

**唯一的落差**：作者把 Matthew Berman 那則廣告拆解跟 GojiberryAI 都列進「已接入產品」，沒有像我們一樣深挖到 Grok 的 embedding 解釋站不住、或 Gojiberry 既有評分功能被獨立評測點名不透明——不算文章的錯，只是我們查得更深一層。

## 標籤

📚（第三方獨立文章，方法論紀律高，我們沒有重跑他的兩輪測試本身；但其中「延遲沒有長尾」這個具體發現，我們自己重跑了一組小規模量測，見上文與 [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/) 標 🔬）

---

# You got Jev, now what? A hype-free landing list, cross-checked three ways against our own findings (English)

## What this covers

Less than a week after Jev's launch, social media was full of "200x faster" and "never wrong" claims. This article does three things: explain plainly what Jev is and isn't; organize the cases that had actually shipped (accessible code/demo/product entry point) by use case; and separate signal from hype. The author also did two things hands-on: first tried wiring Jev into their own daily tools — four attempts, four failures — then stepped back and ran two formal tests: having Jev self-assess 217 Jev-related projects' real usability, then validating confidence calibration on 100 Chinese news items.

## Methodology

For the case survey: explicitly excludes "Jev-imitating alternative models (not applications of Jev)" and "pure opinion, tutorials, launch announcements, ideas with no running evidence" — only cases with accessible evidence are counted, organized into five use-case categories (agent decision engine, mass text classification, confidence-based routing, real-time reaction demos, simulation/control experiments), plus a separate "already integrated into real products" tier.

For the self-run tests: Round 1 fed Jev the public descriptions of 217 Jev-related projects (60 collected cases + 167 more found on GitHub), asking it to judge "can this actually be obtained and used today" for each — this round doubled as a real test of the "mass text classification" use case. Round 2 constructed 100 Chinese tech-news items, three questions each (300 judgments total), with pre-labeled ground truth, run serially from Shanghai against Jev and a lightweight LLM (Qwen 3.8 Flash) as a control, measuring whether confidence tracked actual accuracy and recording real latency.

## Results

**Four failures, honestly reported**: ① installing a context-compaction plugin for Claude Code — couldn't properly install it; the barely-working version amounted to "mindless deletion," indistinguishable from a fake model that always answers 0; root cause: to fit the 32K limit, the plugin stripped all content, leaving Jev only tool names and lengths. ② model routing for Codex to save quota — actually cost 59-184% more, with 1-2 extra seconds per step; root cause: the middleman proxy made requests 2.5x heavier and broke caching. ③ detecting "AI flavor" in the author's own drafts — fast and cheap, but 22 of 62 sentences were false positives, net added value near zero. ④ deciding which of 40 large videos could be deleted — judged zero deletable, while plain rules alone found 7; root cause: it can't see file content, only guess from filenames.

**Round 1 self-assessment**: of 217 items, Jev judged only 15 "usable today, with sufficient evidence" — 14 of those were framework-level Jev integrations (pydantic-ai, LangChain, Vercel AI SDK), not applications; the only application was jev-ultrafast. Of five candidates for "already integrated into products," Jev was more conservative than the author, only trusting SPIRITT and ReqLLM.

**Round 2 calibration and latency**: of 300 judgments, 255 came with "90%+ confidence," and **all 255 were correct**; setting an 80% auto-pass threshold would let 89% of requests through with only 1 error. Real Shanghai-measured median latency was about 0.7s (slower than the official 0.07-0.5s spec), but the worst case was only 1.5s; the control, Qwen 3.8 Flash, had a similar median but a worst case of 32 seconds. Accuracy was 94.7% vs. 93.0%, at the same $0.003 cost — the advertised "40-400x cheaper" claim holds against frontier models, not against lightweight ones.

## What this means

**Matches three entries already in this repo, item for item** — this is the article's strongest point: ① the official 68% accuracy figure, with reference labels averaged from two models, exactly matches what `translations/typesafe-launch-evals-zh/` found (67.8%, averaging GPT-6 Astra and Claude Fable 5.1); ② the jev-ultrafast flight-search case's 9.5→7.1s exactly matches the official figures in `capability-map.md` (9.450→7.092s); ③ "the compaction plugin turned into mindless deletion because state only shows tool names and lengths" is the same finding `translations/jev-context-compaction-debate-zh/` dug out of GitHub issue #26 (zero of 256 real results scored above 0.3 to keep, because state only showed a length placeholder) — the author hit this by actually installing the plugin themselves, not by reading our write-up. Two fully independent paths converging on the same conclusion is more persuasive than either alone.

**We independently verified one finding ourselves, and it also held up**: the article's claim that "Jev's real win isn't median speed, it's the absence of a long tail" is one of the few findings that needs no ground truth and costs little enough to just re-run directly — we ran our own 30-item real latency measurement from our own network environment ([`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/)), getting a 250.4ms median (within spec, faster than the article's 0.7s Shanghai median) and a p95 of just 298.5ms; the only outlier among 30 calls (667.9ms) was the very first one, most plausibly connection-setup overhead, not a hidden slow mode. This independently supports "no long tail," though we didn't run a side-by-side lightweight-LLM comparison, so we only verified the "Jev itself is stable" half.

**Two genuinely new findings worth folding into our own guidance**:

1. **Subscription pricing kills Jev's cost advantage**: Jev's pitch is "hundreds of times cheaper than calling an LLM," but if you're already on a flat-rate subscription tool (Claude Code, Codex), the marginal cost of one more judgment call is already near zero — adding a Jev layer only adds latency and a new failure surface, with no real savings. This is an independent **cost-context** test, separate from our core task-shape axis: ask whether the marginal cost of the judgment you're replacing is already zero before wiring Jev in at all.
2. **Latency stability (no long tail) matters more than median speed** — our own measurement supports this too, and it's worth folding into how we describe the "fast" selling point: not just "fast on average," but "rarely the kind of slow outlier that makes a user wait and wonder," which matters especially for anything user-facing and real-time.

**The one gap**: the article lists both Matthew Berman's ad-breakdown post and GojiberryAI under "already integrated into products" without digging as deep as we did into Grok's embedding explanation not holding up, or the independent review flagging Gojiberry's existing scoring feature as opaque. Not a flaw in the article — we just went one layer deeper.

## Tag

📚 (an independent third-party article with strong methodological discipline; we did not re-run its own two test rounds ourselves; but its specific "no long tail" latency finding was independently re-tested by us at small scale, see above and [`suites/jev-latency-distribution/`](../../suites/jev-latency-distribution/), tagged 🔬)
