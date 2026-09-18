🇹🇼 中文｜🇬🇧 English below

# 稱讚 vs 真心諷刺

## 這組測什麼

兩輪對照：①同句版——反諷訊號跟正面詞在同一句 ②跨句版——負面脈絡在一個回合、字面純粹不帶保留的正面稱讚在另一個獨立回合。各含刻意設計成「聽起來像諷刺但其實真心」的陷阱案例。跨句版另加兩個刻意寫模糊、不計分的對照案例，只看信心行為。

## 為什麼測這個

反諷偵測在 NLP 文獻裡公認是難題，我們原先（用第二節 RLCD/RLVR 架構區分做推論）也預測這對 Jev 會是弱項，接近能力地圖上「需要外部知識」那一側。這組就是去驗證這個預測對不對。

## 方法論

24 題（12+12，其中 2 題不計分），單一標註者出題兼判標準答案，英文句子。字面版刻意用「正面詞緊接負面事件」的固定修辭套路；跨句版刻意把兩者拆到不同回合，移除同句內的字面矛盾，測試是否還需要「真正的」跨句語用推理才能抓到。

## 結果

見 `runs/2026-09-19.json`。同句 **12/12**、跨句（計分題）**10/10**，信心大多在 0.80 以上。兩個模糊對照案例分岔：一個信心誠實偏低（0.19），另一個信心滿檔（1.00）——事後檢視，後者其實不算真的模糊（見 report 下方討論）。

## 這組推翻了我們自己的預測

跑之前我們以為反諷偵測會難；跑完發現不難——即使拆到跨句，只要反諷觸發線索**完整存在於給定的 state 裡**，單次平行判讀就抓得到，不需要真正意義上的多步驟推導。這不代表反諷偵測整體不難，只代表「訊號都在給定文字裡」這種形式的反諷不難；需要 state 以外世界知識才能判斷的反諷（例如要知道某個宣稱是不是事實才知道是不是反話），我們沒測過，可能是完全不同的難度。

## 限制

N=24，單一標註者，只有英文，只有「訊號都給齊」這種形式的反諷。AMB2 案例的「模糊」判準本身可能是我們出題的瑕疵，不是模型過度自信的證據——見 report 內對這點的討論，歡迎有不同意見的人提出反例。

## 標籤

🔬 我們自己測的，真實 API 呼叫，見 `runs/`。

---

# Sarcasm vs. sincere praise (English)

## What this tests

Two rounds: ① same-clause — the ironic trigger and the positive words share one sentence; ② cross-turn — the negative context sits in one turn, a lexically pure, unqualified positive statement sits in a separate turn. Each round includes deliberate "trap" cases designed to look sarcastic but are actually sincere. The cross-turn round adds two deliberately ambiguous, unscored control cases to observe confidence behavior alone.

## Why this task

Sarcasm/irony detection is a well-known hard problem in the NLP literature, and we initially predicted (reasoning from the RLCD/RLVR architecture distinction) that it would be a weak spot for Jev, landing on the capability map's "needs outside knowledge" side. This suite tests whether that prediction holds.

## Methodology

24 items (12+12, 2 unscored), single annotator wrote and labeled everything, English only. The same-clause set deliberately uses the "positive word immediately followed by a stated negative event" rhetorical pattern; the cross-turn set deliberately splits these across turns to remove the same-clause lexical contradiction and test whether genuine cross-turn pragmatic inference is still needed.

## Results

See `runs/2026-09-19.json`. Same-clause **12/12**; cross-turn (scored items) **10/10**; confidence mostly above 0.80. The two ambiguous controls diverged: one landed honestly low (0.19), the other maxed out (1.00) — on reflection, the latter probably wasn't genuinely ambiguous to begin with (discussed below).

## This suite overturned our own prediction

Going in, we expected sarcasm detection to be hard; it wasn't — even split across turns, as long as the ironic trigger is **fully present in the given state**, a single parallel judgment catches it, with no genuine multi-step derivation required. This doesn't mean sarcasm detection in general isn't hard — only that this *shape* of sarcasm, with all the signal handed over, isn't. Sarcasm requiring knowledge outside the state (e.g. needing to know whether a claim is actually true to know if a remark is ironic about it) is untested and could be a genuinely different difficulty class.

## Limitations

N=24, single annotator, English only, and only the "all signal given" shape of sarcasm. The AMB2 case's "ambiguous" label may itself have been a flaw in our test design rather than evidence of overconfidence — discussed further below; counter-examples welcome from anyone who disagrees.

## Tag

🔬 Our own test, real API calls, see `runs/`.
