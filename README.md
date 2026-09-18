🇹🇼 中文（本頁）｜🇬🇧 [English](README.en.md)

# Jev Capability Atlas

**獨立、非官方、非 TypeSafe 贊助的社群專案。** 用真實 API 呼叫的收據，畫出 [Jev](https://typesafe.ai)（TypeSafe 的 System One 模型）「校準決策」這個宣稱在哪裡站得住、在哪裡站不住的邊界地圖——給人看怎麼用，給 agent 帶進專案看哪裡能試著換上去，也給任何做過真實驗的人一個把結果貢獻進來的地方。

不是排行榜（市面上已經有 [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)、[thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts) 在做這件事，做得很紮實，我們引用它們、不重做）。這裡要回答的是更根本的問題：**什麼情況下它強，什麼情況下它弱，為什麼**。

## 30 秒版

Jev 很快、很便宜，但只能做「選一個選項/打個分/回答是非」這種窄判斷，不會寫文字解釋自己在想什麼。**它在「答案就寫在你餵給它的文字裡」的任務上很準**（分類、判斷兩段文字關不關聯、抓語意層的矛盾），**在「需要你沒給它的知識」的任務上會出包，而且往往包得很有自信**。最直接的例子：同一道歷史選擇題，不給背景資料時它以 0.90 的信心給錯答案，把背景段落餵給它以後，同一題以 0.97 的信心答對（見 [`suites/history-recall-context/`](suites/history-recall-context/)，真實 API 收據）。這個 repo 存在的目的，就是幫你分辨你手上的任務屬於哪一種，並且持續累積更多真實案例。

---

## 它不是狀態機，也不是瞎猜——但也不是「會思考」的推理模型

看到上面「只能做窄判斷、不解釋自己」，很容易腦補成「它就是個狀態機/查表機」或「它在瞎猜」——兩者都不對，錯的方向還不一樣。

**為什麼不是狀態機**：狀態機的核心是有限離散狀態+事先寫死的轉移規則。Jev 底層是真的訓練過的語言模型，做的是分布式語言理解，不是規則比對——證據見 [`suites/citation-support-check/`](suites/citation-support-check/) 的兩組對照案例：`paraphrase_support`（宣稱跟引文字面幾乎不重疊，但語意上真的支持，它判對了）、`reversed_meaning_high_overlap`（除了一個字幾乎逐字重疊，但那個字把意思整個反過來，它也判對了）。🔬 純規則/關鍵字系統做不到這兩件事。

但「狀態機」這個比喻有一件事講對了——不是它的內部運作，是它在系統裡該被放的**位置**。TypeSafe 自己的定位：「code needs a narrow decision it can inspect and act on」「99% machine-to-machine interactions」📖——它該被當成嵌進你自己程式邏輯裡的一個元件用，不是自主對話的夥伴。把它當「狀態機的一個節點」是對的架構直覺；把它的內部運作想像成狀態機是錯的。

**為什麼不是瞎猜**：`confidence` 不是另一個獨立的「自信心」機制，是從它已經給出的機率分布**算出來的統計量**。📖 這個數字值得信任是因為訓練目標本身就衝著它去：TypeSafe 把後訓練分三條路——RLHF（對話模型，目標是「人喜歡聽」）、RLVR（推理模型，目標是「推導對」）、**RLCD**（Jev 用這條，目標明講是「機率越高，答案正確的機會應該越大」）。📖 我們自己的測試裡多次看到這個數字隨案例難度真實起伏：反諷偵測跨句版的兩個刻意寫模糊的對照案例，一個信心掉到 0.19（接近丟銅板），另一個維持 1.00；🔬 純回憶史實題那組更直接——同一題，沒給背景時機率三選項幾乎打平（0.25/0.37/0.38），給了背景後集中到 0.98。🔬

但誠實的但書要講：calibration（校準）是**群體統計**性質，不是對單一答案的保證，TypeSafe 自己這樣寫。📖 我們找到的第三方跑分證實這會壞：DAIR Emotion 那組任務，Jev 平均信心 0.819，實際只對了 48%，還有 16% 的題目給「正確答案」的機率剛好是零。📚 **這才是「瞎猜」疑慮真正該落地的地方**——不是它到處在瞎猜，是它的信心機制在某些任務（類別本身重疊、糊在一起的那種）上會失準，而且失準的方向是「顯得比實際上更有把握」，這是最危險的失準方向。

**那它到底是什麼**：一個訓練過真正語言理解、但被限制成只能吐出型別化答案、且訓練目標鎖定「讓機率數字可信」的模型。跟狀態機的差別在於真正的語言理解；跟瞎猜的差別在於信心數字有實證支持（但不是無限可信，見上一段但書）；跟現在講的「推理模型」（o1/DeepSeek-R1 那類）的差別在於它不做展開式、多步驟、自我承接的推導——TypeSafe 把它放進第三個類別，不是簡化版推理模型，是不同的優化目標。三個否定句合起來才誠實，單挑一個標籤套上去都會失真。

### 具體案例：為什麼「瀏覽器自動化」測起來這麼強

第三方案例（`jev-ultrafast`，把 Jev 接進開源瀏覽器代理框架 Browser Use）：Google Flights 搜尋流程從 9.5 秒降到 7.1 秒（快 25%）；另一組對照 Playwright MCP 的 12 題基準測試，快 1.5 倍、便宜 1.6 倍、準確度相當；獨立跑的 Jev 迴圈本身約 1.8 秒、每任務 $0.0005、97% 成功率。📚

這不是「Jev 很會看網頁」——它現在只吃文字，不吃截圖，文件寫得很清楚。厲害的地方是這個整合精準命中上面兩條原則：

1. **把「看畫面」換成「讀給定文字」**：不用截圖，改用結構化的 DOM 快照文字當 `state`——原本需要視覺理解的任務，被轉譯成純文字、訊號自足的判斷，正好落進它的能力圈。
2. **把「一次一步」換成「一次批次」**：不是每走一步就問一次慢模型「該點哪裡」，是把畫面上所有候選元素的判斷一次平行問完（TypeSafe 自己的說法叫「speculative fan-out」）——這正是它的強項：大量、窄、平行的判斷。

換句話說，強的不是模型本身多會逛網頁，是有人把它放對了位置——這正是上面「元件定位」那句話的活教材，不是例外。

---

## 核心發現：一條軸

我們（用真實 API 呼叫，不是估的）加上讀到的第三方跑分，反覆驗證出同一條軸：

> **正確答案能不能完全從你餵給模型的 `state` 裡讀出來，還是需要外部知識/比較，而那些不在 `state` 裡？**

| 訊號自足（state 裡有） | 訊號不自足（需要外部知識） |
|---|---|
| ✅ 分類任務（AG News 91%、Banking77 87%——[jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)） | ⚠️ 純知識回憶題（歷史/常識考題，沒給背景段落——見 [`suites/history-recall-context/`](suites/history-recall-context/)） |
| ✅ 引用支持度判讀（claim+quote 都給齊——見 [`suites/citation-support-check/`](suites/citation-support-check/)） | ⚠️ 需要跟整個領域比較的評分（論文新穎性、专案重要性） |
| ✅ 反諷/諷刺偵測（觸發線索在給定文字裡，即使跨對話回合——見 [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)） | ⚠️ 類別本身就重疊、糊在一起的分類（DAIR Emotion 48%，而且信心值同時失準——[jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)） |

完整方法論、來源分級（🔬 我們自己測的 / 📚 第三方跑分 / 📖 TypeSafe 官方文件 / 💭 我們的綜合分析）、逐項數據，見完整評測報告：**[Jev Evaluation Report](https://claude.ai/code/artifact/286d1a05-f51e-4e18-aba2-234bc0ceb29b)**（中英雙語）。

---

## 我能怎麼用 Jev？（給人看）

1. **先讀 TypeSafe 官方的 [skill](https://github.com/typesafe-ai/skills)**，學怎麼呼叫 API、怎麼設計 Choice/Score/Noul 題目——那件事他們寫得很好，我們不重複。
2. **再讀這裡的 [`capability-map.md`](capability-map.md)**，對照你要做的任務屬於「訊號自足」還是「需要外部知識」，校準你該有的期待值。
3. **信心閾值自己在你的資料上驗**，不要照抄任何一份報告（包括這份）裡的數字——TypeSafe 自己的文件也這樣講。三段式起點：高信心→自動執行；中信心→先確認；低信心→升級給人或給完整推理能力的模型。
4. **遇到需要「知道什麼」而不是「判斷什麼」的任務，先做檢索、把資料放進 `state`**，不要指望它自己「記得」——見 [`suites/history-recall-context/`](suites/history-recall-context/) 那組活生生的反例。

## 給 Agent：哪邊能嘗試改用 Jev、怎麼回報結果

**直接讀 [`AGENTS.md`](AGENTS.md)**，不要從這頁散文推——那份文件分兩種情境：被叫去評估**別的專案**哪裡適合換 Jev（掃描判準+檢查清單），或被叫進**這個 repo 本身**跑測試/加測試（含跑既有 suite 的指令、新增 suite 的步驟、以及**回報結果的具體協定**——有沒有 push 權限分別該怎麼做、回報裡一定要包含什麼）。也有正式打包成 Claude Skill 的版本，見 [`skill/jev-fit-check/`](skill/jev-fit-check/SKILL.md)，可以用 `claude plugin install` 直接裝（僅涵蓋「評估別的專案」那部分）。

## 貢獻真實實驗結果

歡迎三種貢獻：①新的測試組 ②把國外跑分翻譯進來 ③純分析/心得。**收據優先，不收手打數字**——每組貢獻都要附真實 API 回應的原始 log。完整規則見 [`CONTRIBUTING.md`](CONTRIBUTING.md)。

## 目錄結構

```
README.md / README.en.md   本頁雙語（含機制說明，不是另開檔案）
AGENTS.md                  給 agent 讀的掃描判準
capability-map.md          那條軸的彙整表，持續更新
CONTRIBUTING.md            貢獻規則
skill/jev-fit-check/       打包成 Claude Skill 的 AGENTS.md
suites/                    每組實測（方法論＋協定＋真實 log＋報告）
translations/              國外跑分的翻譯貢獻
scripts/common/            共用的 API 呼叫樣板，不用各自重寫
```

## 授權

程式碼與原創內容 MIT。貢獻翻譯內容前**請先確認原始資料集的授權條款**，細節見 `CONTRIBUTING.md`——這不是形式，是真的法律風險。

本專案與 TypeSafe 無關，未受其委託或贊助。「Jev」「TypeSafe」為其各自所有者之商標，此處僅作指涉之用。
