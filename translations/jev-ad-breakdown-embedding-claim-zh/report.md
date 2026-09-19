🇹🇼 中文｜🇬🇧 English below

# 廣告素材拆解爆紅推文：Jev 讀得懂 Gemini Embedding 裡的顏色風格嗎？

## 這組在查什麼

一則爆紅推文（Matthew Berman）宣稱 Jev 在 40 秒內拆解 724 則真實廣告（37 個品牌），逐則判斷 hook、格式、優惠、CTA、認知階段、登陸頁是否對得上廣告承諾，花費共 9 美分。因為 Jev 官方文件明講只吃文字不吃圖片，同串底下有人追問「不支援圖片，怎麼拆解廣告的」，原 po 只回了一句「gemini pipeline with embedding」，細節由 Grok 補完：Gemini 多模態視覺模型先跑一次廣告素材，產生 OCR 文字/描述，另外也產生 Gemini Embedding 2 的 3072 維浮點數向量，兩者一起當 `state` 餵給 Jev，讓 Jev「不用自己跑視覺」就能判斷格式/風格這類視覺相關的維度。這組要查的是：這個解釋站不站得住。

## 方法論

逐句核對貼文原文跟 Grok 每一則回覆的技術主張；查證 stealads.ai 官網有沒有對應技術文件；查證 Matthew Berman 個人 GitHub 帳號的既有 repo 是否相關；用 GitHub 搜尋找有沒有其他人針對同一則推文做過獨立實作或技術規劃，找到 `Nishfleet/0509`（一個廣告追蹤系統）公開的內部工單，完整記錄了他們看到這則推文後自己規劃的 Jev 整合方案。

## 結果

**Grok 的核心主張**：「Gemini Embedding 2 訓練時把顏色、風格、佈局、構圖、意象都壓進這組數字裡，相似的視覺在向量空間裡會彼此靠近」——這句話本身沒錯，是 embedding 的標準性質。但下一步推論——「Jev 拿到這組數字（序列化成文字 state）就能讀出視覺語意」——查無任何支持這個推論的技術依據。同一串裡 `@alaamurad` 已經提出對應質疑：「如果 Gemini 就能做視覺判讀，幹嘛不讓 Gemini 直接吐結果」，這則質疑在串裡沒有被回答，討論就停在這裡。

`Nishfleet/0509` 的內部工單（#3606/#3537/#3531，2026-09-17/18 記錄，看到同一則推文後幾小時內立案）完全沒有提到 embedding 這個環節——他們規劃的整合方式是：既有的廣告擷取流程先把廣告素材轉成結構化文字欄位（格式/優惠/hook/CTA 等），這些文字欄位才是餵給 Jev 的 `state`，問 Choice/Score/Boolean 型別化問題；而且明確要求「上線前先拿 200 則真實廣告＋200 則真實提及做人工標註校準跑分，校準沒測過什麼都不准上線」。

## 這代表什麼

**Grok 的解釋有一個真實、可以指名道姓的技術破綻**：embedding 向量的語意只在它自己被訓練出來的向量空間裡有意義——要嘛拿去算相似度/最近鄰，要嘛餵給一個跟這個向量空間**聯合訓練過**的模型（例如 LLaVA/GPT-4V 那類有專門投影層，把視覺 embedding 直接接進語言模型隱藏層的架構）。Jev 是讀文字 token 的模型，沒有任何跡象顯示它跟 Gemini Embedding 2 的向量空間聯合訓練過。把一串浮點數序列化成文字塞進 `state`，Jev 讀到的是一串數字符號，不會因為「訓練時顏色風格被壓進這些數字裡」就自動解得出語意——這是把「embedding 在向量空間裡語意豐富」跟「把 embedding 序列化成文字讀出來語意豐富」混為一談，是一個常見到有名字的技術誤區。

**這則解釋的出處本身就是個警訊**：不是原 po 或任何技術文件講的，是 Grok 被追問之後現場生成的——這正是「AI 面對一個黑盒子，給出聽起來很懂但其實編造」的典型失效模式，講得越具體（「3072 維」「output 長這樣：`[0.023, -0.15, 0.41, ...]`」）越容易讓人誤以為是查證過的事實，其實只是聽起來精確的幻覺。

**巧合但有力的佐證，來自完全獨立的第三方**：`Nishfleet/0509` 這個團隊看到同一則推文後，自己規劃出的整合方案完全繞開了 embedding，直接採用「先轉文字、再讓 Jev 判斷」這個我們自己也在 `AGENTS.md` 補過的原則——不是因為他們讀過我們的檢查清單，是因為這本來就是唯一技術上說得通的做法，兩邊獨立收斂到同一個答案，反而比任何單一來源更有說服力。這個團隊還明確堅持「先校準、沒測過不准上線」的紀律，跟本 repo 的收據優先精神完全一致。

**結論**：724 則廣告、40 秒、9 美分這個效能數字本身沒有理由懷疑（量級跟 Jev 已知的速度/成本表現吻合），但「怎麼讓 Jev 看懂視覺元素」這個技術細節目前沒有可信的答案——貼文本身沒講清楚，Grok 的補充解釋技術上站不住，而真正合理的架構（先轉文字）也還沒有被原作者證實是他真正在用的方法。

## 標籤

📚（推文本身的效能宣稱是第三方 📚；Grok 的技術解釋經查證認定站不住，屬於我們自己的 💭 技術分析；Nishfleet 的內部工單是另一個獨立第三方的 📚 佐證，三者合起來標一個 📚，細節見上文拆解）

---

# The viral ad-breakdown tweet: can Jev actually read color and style from a Gemini embedding? (English)

## What this checks

A viral tweet (Matthew Berman) claimed Jev broke down 724 real ads from 37 brands in 40 seconds, judging hook, format, offer, CTA, awareness stage, and landing-page-promise-match for each, at a total cost of 9 cents. Since Jev's own docs state plainly that it only takes text, not images, someone in the thread asked how it could possibly break down ads. The original poster replied only "gemini pipeline with embedding," and Grok filled in the details: a multimodal Gemini pass over each ad creative produces OCR text/descriptions, plus a Gemini Embedding 2 3072-dimensional float vector; both get fed as `state` to Jev, letting it judge visual dimensions like format and style "without running vision itself." This checks whether that explanation holds up.

## Methodology

Checked every technical claim in the thread and in Grok's replies against what's actually known about how embeddings and language models work; checked stealads.ai for technical documentation; checked Matthew Berman's own GitHub account for a related implementation; searched GitHub for anyone independently implementing or planning the same idea after seeing the tweet, and found `Nishfleet/0509` (an ad-tracking system)'s public internal tickets, which fully document their own Jev integration plan after seeing the same tweet.

## Results

**Grok's core claim**: "training packs colors, style, layout, composition and imagery into the numbers so similar visuals sit close in space" — true on its own, a standard property of embeddings. But the next step of the inference — "Jev, given these numbers serialized as text state, can read visual semantics out of them" — has no technical basis we could find. `@alaamurad` in the same thread raised exactly this objection: "why not just have Gemini return the output directly?" That question went unanswered; the thread ends there.

`Nishfleet/0509`'s internal tickets (#3606/#3537/#3531, dated 2026-09-17/18, filed within hours of the same tweet) never mention embeddings at all. Their planned integration: an existing ad-capture pipeline first converts creatives into structured text fields (format/offer/hook/CTA, etc.), and those text fields — not embeddings — are what gets fed to Jev as `state`, asking typed Choice/Score/Boolean questions; they explicitly require "a hand-labeled calibration benchmark on 200 real ads + 200 real mentions before anything ships — nothing ships on Jev until measured."

## What this means

**Grok's explanation has a real, nameable technical flaw**: an embedding vector's semantics only exist within the vector space it was trained in — usable via similarity/nearest-neighbor operations, or fed to a model **jointly trained** on that same vector space (the way LLaVA/GPT-4V-class architectures have a dedicated projection layer feeding visual embeddings directly into the language model's hidden state). Jev is a text-token-reading model, with no indication it was jointly trained on Gemini Embedding 2's vector space. Serializing a float array into text and dropping it into `state` gives Jev a string of digit tokens — it doesn't automatically decode into semantics just because "color and style got packed into those numbers during training." This conflates "an embedding is semantically rich within its vector space" with "an embedding is semantically rich when read as text by an unrelated model" — a common, well-known confusion.

**The source of this explanation is itself a red flag**: it wasn't stated by the original poster or any technical documentation — it was generated by Grok on the spot in response to follow-up questions. This is exactly the failure mode of an AI confabulating a plausible-sounding explanation for a black box it doesn't actually have access to — and the more specific it sounds ("3072 dimensions," "output looks like `[0.023, -0.15, 0.41, ...]`"), the more likely it is to be mistaken for verified fact when it's really just a precise-sounding hallucination.

**A coincidental but strong piece of corroborating evidence, from a fully independent third party**: `Nishfleet/0509`'s team, after seeing the same tweet, independently planned an integration that skips embeddings entirely and goes straight to "convert to text first, then let Jev judge" — the same principle we recently added to our own `AGENTS.md`. Not because they read our checklist, but because that's simply the only technically coherent approach — two independent parties converging on the same answer is more persuasive than either alone. This same team also insists on "calibrate first, nothing ships until measured" discipline, matching this repo's receipts-first ethos exactly.

**Conclusion**: there's no particular reason to doubt the headline performance numbers (724 ads, 40 seconds, 9 cents — the order of magnitude matches Jev's known speed/cost profile), but the technical detail of "how Jev is made to understand visual elements" currently has no credible answer — the original post never explained it, Grok's supplementary explanation doesn't hold up technically, and the actually coherent architecture (convert to text first) hasn't been confirmed as what the original author is really doing.

## Tag

📚 (the tweet's own performance claim is third-party 📚; Grok's technical explanation, on verification, doesn't hold up — that's our own 💭 technical analysis; Nishfleet's internal tickets are independent third-party 📚 corroboration; the whole entry is tagged 📚, with the breakdown above making clear which part is which)
