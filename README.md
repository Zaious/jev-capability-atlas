🇹🇼 中文(本頁)｜🇬🇧 [English](README.en.md)

# Jev Capability Atlas

**獨立、非官方、非 TypeSafe 贊助的社群專案。** 用真實 API 呼叫的收據,畫出 [Jev](https://typesafe.ai)(TypeSafe 的 System One 模型)「校準決策」這個宣稱在哪裡站得住、在哪裡站不住的邊界地圖——給人看怎麼用,給 agent 帶進專案看哪裡能試著換上去,也給任何做過真實驗的人一個把結果貢獻進來的地方。

不是排行榜(市面上已經有 [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)、[thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) 在做這件事,做得很紮實,我們引用它們、不重做)。這裡要回答的是更根本的問題:**什麼情況下它強,什麼情況下它弱,為什麼**。

## 30 秒版

Jev 很快、很便宜,但只能做「選一個選項/打個分/回答是非」這種窄判斷,不會寫文字解釋自己在想什麼。**它在「答案就寫在你餵給它的文字裡」的任務上很準**(分類、判斷兩段文字關不關聯、抓語意層的矛盾),**在「需要你沒給它的知識」的任務上會出包,而且往往包得很有自信**。最直接的例子:同一道歷史選擇題,不給背景資料時它以 0.90 的信心給錯答案,把背景段落餵給它以後,同一題以 0.97 的信心答對(見 [`suites/history-recall-context/`](suites/history-recall-context/),真實 API 收據)。這個 repo 存在的目的,就是幫你分辨你手上的任務屬於哪一種,並且持續累積更多真實案例。

> ⚠️ **看到「只能做窄判斷、不解釋自己」,不要腦補成「它就是個狀態機/查表機」或「它在瞎猜」——兩者都不對。** 差異講清楚見 **[`MECHANISM.md`](MECHANISM.md)**,這頁是必讀,不是選讀,尤其如果你要把這個 repo 的結論轉述給別人。

---

## 核心發現:一條軸

我們(用真實 API 呼叫,不是估的)加上讀到的第三方跑分,反覆驗證出同一條軸:

> **正確答案能不能完全從你餵給模型的 `state` 裡讀出來,還是需要外部知識/比較,而那些不在 `state` 裡?**

| 訊號自足(state 裡有) | 訊號不自足(需要外部知識) |
|---|---|
| ✅ 分類任務(AG News 91%、Banking77 87%——[jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) | ⚠️ 純知識回憶題(歷史/常識考題,沒給背景段落——見 [`suites/history-recall-context/`](suites/history-recall-context/)) |
| ✅ 引用支持度判讀(claim+quote 都給齊——見 [`suites/citation-support-check/`](suites/citation-support-check/)) | ⚠️ 需要跟整個領域比較的評分(論文新穎性、专案重要性) |
| ✅ 反諷/諷刺偵測(觸發線索在給定文字裡,即使跨對話回合——見 [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)) | ⚠️ 類別本身就重疊、糊在一起的分類(DAIR Emotion 48%,而且信心值同時失準——[jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)) |

完整方法論、來源分級(🔬 我們自己測的 / 📚 第三方跑分 / 📖 TypeSafe 官方文件 / 💭 我們的綜合分析)、逐項數據,見完整評測報告:**[Jev Evaluation Report](https://claude.ai/code/artifact/286d1a05-f51e-4e18-aba2-234bc0ceb29b)**(中英雙語)。

---

## 我能怎麼用 Jev?(給人看)

1. **先讀 TypeSafe 官方的 [skill](https://github.com/typesafe-ai/skills)**,學怎麼呼叫 API、怎麼設計 Choice/Score/Noul 題目——那件事他們寫得很好,我們不重複。
2. **再讀這裡的 [`capability-map.md`](capability-map.md)**,對照你要做的任務屬於「訊號自足」還是「需要外部知識」,校準你該有的期待值。
3. **信心閾值自己在你的資料上驗**,不要照抄任何一份報告(包括這份)裡的數字——TypeSafe 自己的文件也這樣講。三段式起點:高信心→自動執行;中信心→先確認;低信心→升級給人或給完整推理能力的模型。
4. **遇到需要「知道什麼」而不是「判斷什麼」的任務,先做檢索、把資料放進 `state`**,不要指望它自己「記得」——見 [`suites/history-recall-context/`](suites/history-recall-context/) 那組活生生的反例。

## 給 Agent:哪邊能嘗試改用 Jev、怎麼回報結果

**直接讀 [`AGENTS.md`](AGENTS.md)**,不要從這頁散文推——那份文件分兩種情境:被叫去評估**別的專案**哪裡適合換 Jev(掃描判準+檢查清單),或被叫進**這個 repo 本身**跑測試/加測試(含跑既有 suite 的指令、新增 suite 的步驟、以及**回報結果的具體協定**——有沒有 push 權限分別該怎麼做、回報裡一定要包含什麼)。也有正式打包成 Claude Skill 的版本,見 [`skill/jev-fit-check/`](skill/jev-fit-check/SKILL.md),可以用 `claude plugin install` 直接裝(僅涵蓋「評估別的專案」那部分)。

## 貢獻真實實驗結果

歡迎三種貢獻:①新的測試組 ②把國外跑分翻譯進來 ③純分析/心得。**收據優先,不收手打數字**——每組貢獻都要附真實 API 回應的原始 log。完整規則見 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 目錄結構

```
README.md / README.en.md   本頁雙語
MECHANISM.md                必讀:它不是狀態機、不是瞎猜、也不是推理模型
AGENTS.md                  給 agent 讀的掃描判準
capability-map.md          那條軸的彙整表,持續更新
CONTRIBUTING.md            貢獻規則
skill/jev-fit-check/       打包成 Claude Skill 的 AGENTS.md
suites/                    每組實測(方法論+協定+真實 log+報告)
translations/              國外跑分的翻譯貢獻
scripts/common/            共用的 API 呼叫樣板,不用各自重寫
```

## 授權

程式碼與原創內容 MIT。貢獻翻譯內容前**請先確認原始資料集的授權條款**,細節見 CONTRIBUTING.md ——這不是形式,是真的法律風險。

本專案與 TypeSafe 無關,未受其委託或贊助。「Jev」「TypeSafe」為其各自所有者之商標,此處僅作指涉之用。
