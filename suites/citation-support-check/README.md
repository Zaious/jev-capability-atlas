🇹🇼 中文｜🇬🇧 English below

# 引用支持度判讀

## 這組測什麼

給一句宣稱（claim）跟一段逐字引文（quote），問 Jev 一題 Choice：引文支持、反駁，還是沒有回應這句宣稱？五個合成案例，涵蓋清楚反駁、完全無關、字面淺但語意深的難例，以及最關鍵的兩組對照：**改述後字面重疊很低但語意支持**、**字面重疊很高但意思被關鍵字反轉**。

## 為什麼測這個

這組動機來自一個真實觀察：很多引用查核工具只做「宣稱與引文的內容詞字面交集」——零交集才示警。這種字面比對抓不到兩種錯誤：①改述後用詞不同但確實支持（會被字面比對誤判成無關）②幾乎整句抄字典但關鍵一詞被反轉，例如「增加」寫成「減少」的相反（會被字面比對誤判成強力支持）。這兩種情況正好對應能力地圖「訊號自足」那一側——答案完全在 claim+quote 這兩段文字裡，不需要外部知識，是 Jev 該強的地方。

## 方法論

5 題，單一標註者出題兼判標準答案，英文，合成資料（不是真實論文——這組方法論曾經對一篇真實、未發表的學術書稿驗證過 16 組真實引用，結果與方法論一致，詳見 repo README 連結的完整評測報告；這裡改用可公開重現的合成資料，不需要存取任何未發表著作）。

## 結果

見 `runs/2026-09-19.json`。**5/5 全對**，包括兩組關鍵對照案例：
- `paraphrase_support`——字面重疊低（intervention/program、drop/decreased 幾乎不重疊），Jev 正確判成 supports，信心 1.00
- `reversed_meaning_high_overlap`——除了一個詞（increased vs decreased）幾乎逐字重疊，Jev 正確抓到反轉，判成 contradicts，信心 1.00

`subtle_thin_support` 是唯一低信心案例（0.45）——claim 講的是杜威「經驗連續性」這個具體機制，quote 只講「不是所有經驗都有教育性」，同主題但沒有真正建立 claim 講的那個具體主張，這種細膩區分正是字面比對做不到、但也是**人類讀者也該多看一眼**的案例，低信心送審是我們期待的行為，不是失敗。

## 限制

N=5，單一標註者，英文，合成資料。5 題全對讓這組看起來太順，實務上引用查核會遇到更多像 `subtle_thin_support` 那樣的灰色地帶——這正是我們最想邀請貢獻的方向：更大量、更真實（且可公開分享）的難例語料。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。合成方法論曾與真實論文資料對照驗證，見完整評測報告（連結於根目錄 README）。

---

# Citation support-checking (English)

## What this tests

Given a claim and a verbatim quote, ask Jev a single Choice question: does the quote support, contradict, or fail to address the claim? Five synthetic cases covering a clean contradiction, complete irrelevance, a subtle-but-thin case, and — the two most important — a paraphrase with low literal overlap that genuinely supports, and a near-total literal overlap whose meaning is flipped by one word.

## Why this task

This grew out of a real observation: many citation-checking tools only compute literal content-word overlap between claim and quote, flagging only zero-overlap cases. That misses two failure modes: (1) a paraphrase using different words that genuinely supports the claim (a literal-overlap check would wrongly flag it as unrelated), and (2) a near-verbatim match where one key word flips the meaning, e.g. "increased" written where the source says "decreased" (a literal-overlap check would wrongly treat it as strongly supporting). Both cases sit squarely on the capability map's "self-contained" side — the answer lives entirely in the claim+quote text, no outside knowledge needed — exactly where Jev should be strong.

## Methodology

5 items, single annotator wrote and labeled everything, English, synthetic data (not a real paper — this exact methodology was separately validated against 16 real citations from an actual, unpublished academic manuscript with consistent results; see the full evaluation report linked from the repo README. This suite uses reproducible synthetic data instead, so it can be re-run without access to any unpublished work).

## Results

See `runs/2026-09-19.json`. **5/5 correct**, including both key contrast cases:
- `paraphrase_support` — low literal overlap (intervention/program, drop/decreased barely overlap), correctly judged `supports` at 1.00 confidence
- `reversed_meaning_high_overlap` — near-verbatim overlap except for one word (increased vs. decreased), correctly caught as `contradicts` at 1.00 confidence

`subtle_thin_support` was the only low-confidence case (0.45) — the claim is about Dewey's specific continuity mechanism, the quote only says "not all experience is educative," same topic but doesn't itself establish the specific claim being made. That fine distinction is exactly what literal overlap can't catch, and also exactly the kind of case a human reader should look twice at — low confidence flagging it for review is the behavior we want, not a failure.

## Limitations

N=5, single annotator, English, synthetic. A clean 5/5 makes this look easier than real citation-checking usually is — real work runs into far more `subtle_thin_support`-style gray areas. This is exactly where we'd most welcome contributions: larger, more realistic (and publicly shareable) hard-case corpora.

## Tag

🔬 Our own test, real API calls, see `runs/`. The methodology was cross-validated against real manuscript data — see the full evaluation report linked from the root README.
