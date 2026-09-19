🇹🇼 中文（本頁）｜🇬🇧 [English](capability-map.en.md)

# 能力地圖 / Capability Map

這份文件是活的——每收一組新貢獻就更新一次。判準軸見 [README](README.md)。標籤：🔬 我們/貢獻者自己測的、📚 第三方跑分、📖 TypeSafe 官方文件。

分兩區：**公開資料集**是別人發布的結果，我們沒有自己重跑，只翻譯整理（見 [`translations/`](translations/)）；**我們自己驗證過的**是這個 repo 走完整套收據流程（見 [`CONTRIBUTING.md`](CONTRIBUTING.md)）親自打 API 測出來的，兩者的可信基礎不一樣，分開放才不會混。

## 索引表

| 條目 | 軸上位置 | 一句話結果 | 標籤 |
|---|---|---|---|
| [ThaiExam](#thaiexam567-題泰國標準化考題vs-110-個其他模型) | 混合 | 70.7% acc，111 個模型中段班，速度/成本同組最強 | 📚 |
| [jev-benchmarks：AG News](#jev-benchmarksag-newsbanking77dair-emotion) | 訊號自足 | 91.0% acc，明顯贏過專門小型分類器 | 📚 |
| [jev-benchmarks：Banking77](#jev-benchmarksag-newsbanking77dair-emotion) | 訊號自足 | 87.0% acc，同上，且延遲也贏 | 📚 |
| [jev-benchmarks：DAIR Emotion](#jev-benchmarksag-newsbanking77dair-emotion) | 類別重疊（邊界案例） | 48.0% acc 打平，但信心值失準 | 📚 |
| [jev-browser vs Playwright MCP](#jev-browservs-playwright-mcp) | 混合（操作強，純讀取不強） | 混合驅動快 1.5x／便宜 1.6x；但純文字擷取任務反而更慢更貴 | 📚 |
| [jev-ultrafast（Browser Use 官方）](#jev-ultrafastbrowser-use-官方整合) | 訊號自足 | 單一任務中位數快 25%，瀏覽器協定呼叫少 91% | 📚 |
| 稱讚 vs 諷刺（公開專門跑分） | — | 目前查無，這是你可以貢獻的空白 | — |
| [引用支持度判讀](#引用支持度判讀) | 訊號自足 | 9/12 支持、0 反駁，低信心正確對應難例 | 🔬 |
| [反諷偵測·同句／跨句](#反諷偵測) | 訊號自足 | 12/12、10/10 全對，含正確示範低信心 | 🔬 |
| [純回憶史實題 vs 給定背景](#純回憶史實題-vs-給定背景) | 不自足 → 自足 | 無背景時高信心答錯常識題；給了背景後信心與正確率同時回升 | 🔬 |

---

## 公開資料集（第三方跑分，📚）

以下都不是我們自己跑的，是讀完原始 repo/文章/README 之後整理的。每條都附一手來源連結，數字對不上就是我們寫錯，不是原作者的錯。

### ThaiExam：567 題泰國標準化考題，vs 110 個其他模型

**做了什麼**：拿 Jev（`jev-1.13.0`）跟 110 個其他語言模型，對同樣 567 題真實泰國標準化考題（混合科目）打分。

**結果**：**70.7% 準確率**，**0.35 秒/題**，**$0.000029/題**——在整組比較裡速度最快、第二便宜，信心值與實際準確率貼合（期望校準誤差 7.5 個百分點）。

**這代表什麼**：「111 個模型中段班」不是隨口一句話，是可預期的結果——這份考卷混合科目，題目裡混著「答案能自足式從題幹讀出來的閱讀理解題」跟「需要 state 之外的知識回憶/推導的純考古題」，照這個 repo 的核心那條軸，這種題型組合本來就會產出中等、混合的分數。真正該看的是**速度快 1.4 個數量級、成本低幾個數量級的情況下，準確率仍然不是墊底**——支持拿它當高流量前置篩選層，不是取代一個完整推理模型。

來源：[thaiexam-jev-charts](https://github.com/vehas/thaiexam-jev-charts)

### jev-benchmarks：AG News/Banking77/DAIR Emotion

**做了什麼**：拿 Jev 對照一個專門的本地零樣本分類器 `GLiNER2.5`，測三組分類資料集（各 100 例，類別平衡抽樣）。方法論釘住模型版本、確定性抽樣、配對式 bootstrap 信賴區間——不是隨手跑一次就發表。

**結果**：

| 資料集 | Jev | GLiNER | 信賴區間 |
|---|---|---|---|
| AG News（4 類新聞主題） | **91.0%** | 70.0% | `[+0.130, +0.290]`，Jev 明顯領先 |
| Banking77（72 類銀行意圖） | **87.0%** | 61.0% | `[+0.220, +0.300]`，Jev 明顯領先，延遲（246ms）也略快過 GLiNER 本地 CPU 推論（296ms） |
| DAIR Emotion（6 類情緒） | 48.0% | 44.0% | **含零**，統計上分不出高下 |

**這代表什麼**：準確率的勝負取決於類別本身區隔清不清楚——新聞主題、銀行意圖相對乾淨，情緒天生會重疊。DAIR Emotion 真正的發現不是 48% 這個數字，是**信心值同時失準**：Jev 平均信心 0.819（GLiNER 只有老實的 0.438），16% 的題目給「正解」的機率剛好是零。準確率打平時才看得出這個風險——單看準確率會漏掉它。

來源：[jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks)

### jev-browser vs Playwright MCP

**做了什麼**：一個獨立開發者做的 Jev 驅動瀏覽器 MCP 伺服器，跟 `@playwright/mcp`（無障礙快照工具）對照，12 個任務（10 個本地確定性任務+2 個真實 Wikipedia 任務），三種組合各跑一次：純 Jev 自主迴圈（零 LLM）、Claude+Playwright MCP、Claude+jev-browser MCP。**驗證是程式化的，不是 LLM 當裁判**——每個本地任務結束時會產生一組隨機碼，只有真的完成任務才會顯露，跑分程式直接比對隨機碼，不會有裁判偏誤。

**結果**：

| 組合 | 成功率 | 平均耗時/任務 | 平均花費/任務 |
|---|---|---|---|
| 純 Jev（零 LLM） | 32/33（97%，n=3） | 1.8 秒（p50） | ~$0.0005 |
| Claude + Playwright MCP | 12/12（100%） | 18.4 秒 | $0.31 |
| Claude + jev-browser MCP | 12/12（100%） | 12.2 秒 | $0.20 |

**Claude+jev-browser 對 Claude+Playwright：快 1.5 倍、便宜 1.6 倍，準確率打平（12/12 對 12/12）**。贏最多的任務是要重複讀取變大頁面狀態的那種（延遲載入清單快 4.1 倍）。

**誠實的反例，這正是你要的細節**：這組跑分自己就抓到 Jev **不擅長**的地方——l02（Wikipedia 資訊框擷取，純文字閱讀、沒有操作動作）這一項，Jev 反而比 Claude 自己慢（0.7 倍）、貴（0.3 倍，即更貴）。原作者自己的結論：「這不是 Jev 的地盤——把『讀了回答』的任務留給 LLM，把『對頁面採取行動』的任務給 Jev」。這跟我們在 README 講的那條軸完全吻合：瀏覽器自動化強是因為「候選元素都在給定的 DOM 快照裡、訊號自足」，一旦任務變成「閱讀理解一大段文字」，訊號自足的優勢就不見了。

作者自己的但書：兩個 Claude 組合只跑 n=1（時間/成本預算限制），純 Jev 組合 n=3；12 題是煙霧測試規模，不是 WebVoyager 那種完整基準；「Jev 公開的準確率跑分跟前沿模型比是中段班，混合設計本來就假設會有升級（escalation）並把它算進成本」——這句跟 ThaiExam 的中段班發現互相印證。

來源：[jev-browser](https://github.com/MahmoudAdelbghany/jev-browser)（[README](https://github.com/MahmoudAdelbghany/jev-browser/blob/main/README.md)、[完整跑分](https://github.com/MahmoudAdelbghany/jev-browser/blob/main/RESULTS.md)）

### jev-ultrafast（Browser Use 官方整合）

**做了什麼**：Browser Use 這個開源瀏覽器代理專案官方做的整合（不是社群獨立專案，5,700+ 星），把 Jev 接進代理迴圈。跟 jev-browser 是**兩個獨立專案**，不要混為一談。設計上 Jev 只負責選操作（CLICK/TYPE_TEXT/SELECT/SCROLL/WAIT/DONE...）跟選目標元素，一次平行請求同時問「做什麼」跟「對哪個元素做」；真的需要打字時，交給另一個獨立的小型文字生成模型（`inception/mercury-2.5`，經 OpenRouter，關掉推理模式）產生實際鍵入的字——這再次印證 Jev 本身不生成文字這件事，連官方整合都得外掛一個小模型處理打字。

**結果**（官方 repo 自己給的數字，六次交替測試、兩個版本都 3/3 通過）：Google Flights 搜尋（Zürich→London 單程經濟艙）中位數耗時從 **9.450 秒降到 7.092 秒（快 25%）**，瀏覽器協定呼叫中位數從 **1,092 次降到 101 次（少 91%）**。另外兩個任務：開啟指定 Wikipedia 條目 2.798 秒、本地飯店搜尋+篩選 1.896 秒。

**誠實的但書，官方自己寫的**：「這是同一個任務、同一個瀏覽器設定檔的三次重複，不是通用的可靠性基準」；DOM 讀取器目前不支援 shadow DOM、iframe、canvas、檔案上傳、彈出分頁、巢狀捲動——這些明確排除在這個 MVP 之外。

來源：[jev-ultrafast](https://github.com/browser-use/jev-ultrafast)（[README](https://github.com/browser-use/jev-ultrafast/blob/main/README.md)）、[LavX News 報導](https://news.lavx.hu/article/jev-ultrafast-cuts-browser-agent-time-by-25-with-typesafe-action-space)

### 稱讚 vs 諷刺（公開專門跑分）

目前查無任何人發布過專門測 Jev 反諷/諷刺偵測的公開跑分——我們自己在 [`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/) 測過（見下區），但那是我們自己的小型測試，不是獨立第三方跑分。這正是你可以貢獻的空白：找到或自己發布一份，翻譯整理進 [`translations/`](translations/)。

---

## 我們自己驗證過的（🔬，經 CONTRIBUTING 收據流程）

以下每一條都真的打過 API，原始 log 在對應 `suites/<slug>/runs/` 底下，完整方法論見各自的 `README.md`。這裡只放摘要。

### 引用支持度判讀

**做了什麼**：給一句宣稱跟一段逐字引文，問 Jev 一題 Choice：支持、反駁，還是沒有回應這句宣稱？5 個合成案例，涵蓋清楚反駁、完全無關、字面淺但語意深的難例，以及兩組關鍵對照（改述後字面重疊低但語意支持／字面重疊高但關鍵詞反轉）。

**結果**：5/5 全對，包括兩組對照案例都在信心 1.00 判對；唯一低信心案例（0.45）是真的語意細膩的難題，低信心送審是我們期待的行為。這個方法論也對一篇真實、未發表的學術書稿驗證過 16 組真實引用，結果一致（見完整評測報告連結，README 首頁）。

來源：[`suites/citation-support-check/`](suites/citation-support-check/)

### 反諷偵測

**做了什麼**：兩輪對照——同句版（反諷訊號跟正面詞在同一句）、跨句版（負面脈絡跟純粹正面稱讚拆到不同對話回合，移除同句內的字面矛盾）。各含刻意設計成「聽起來像諷刺但其實真心」的陷阱案例；跨句版另加兩個刻意寫模糊、不計分的對照案例。

**結果**：同句 12/12、跨句（計分題）10/10 全對，大多信心 0.80 以上。兩個模糊對照案例分岔：一個信心誠實偏低（0.19），另一個信心滿檔（1.00，事後檢視其實不算真的模糊）。**我們原先預測反諷偵測會是弱項（推論自 RLCD/RLVR 架構區分），跑完發現預測錯了**——只要反諷觸發線索完整存在於給定的 state 裡，單次平行判讀就抓得到。

來源：[`suites/sarcasm-vs-sincere-praise/`](suites/sarcasm-vs-sincere-praise/)

### 純回憶史實題 vs 給定背景

**做了什麼**：三道中文歷史選擇題——①常見史實、無背景段落 ②冷門史實、無背景段落 ③跟②同一題，但附上背景段落。目的是隔離「裸記憶」跟「給定文字內的閱讀理解」這兩種不同能力。

**結果**：案例①在沒給任何背景時，以 0.90 的信心給錯了一般認為的常識題；案例②冷門題信心誠實地趴在接近打平（機率三選項 0.25/0.37/0.38）；案例③同一道冷門題附上背景段落後，機率集中到 0.98 且答對。**高信心答錯常識題，是這整個 repo 裡最重要的一筆反例**——沒有上下文時，Jev 只能靠不透明的預訓練記憶，風險結構跟問任何 LLM 一句沒給資料的冷知識題一樣。

來源：[`suites/history-recall-context/`](suites/history-recall-context/)

---

**還沒有人測過、歡迎貢獻的方向**：多模態（Jev 目前只吃文字，官方文件如此記載）、多維度複合評分在真實產品場景的表現、非英語語系（除泰文外）的表現、跨句以上（三輪＋）脈絡的反諷/隱含意圖偵測、稱讚 vs 諷刺的獨立第三方跑分。
