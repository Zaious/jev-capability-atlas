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
| [TypeSafe 首發評測：Vercel 獨立驗證與方法論批評](#typesafe-首發評測vercel-獨立驗證與方法論批評) | — | 67.8% acc／$0.0004／0.4 秒，但參考答案是兩個 LLM 平均、非人工標註 | 📚 |
| [工具呼叫風險分級（jev-benchmark）](#工具呼叫風險分級jev-benchmark) | 訊號自足 | 91.7% acc，答錯時信心值誠實下修，無「自信答錯」案例 | 📚 |
| [信心門檻棄權（jev-dspy-lab）](#信心門檻棄權jev-dspy-lab) | 訊號自足 | 信心門檻 0.7：覆蓋率 95.8%、準確率 91.3%、ECE 0.0583 | 📚 |
| [用 Jev 砍 Agent 自己的執行紀錄：一場公開辯論](#用-jev-砍-agent-自己的執行紀錄一場公開辯論) | — | 排序對、門檻沒對齊；真實複現 0/256 結果評分超過 0.3 | 📚 |
| [拿 Jev 的機率做 SQL ORDER BY 排序，站不站得住腳](#拿-jev-的機率做-sql-order-by-排序站不站得住腳) | 混合（簡單過關、困難不過） | 20 Newsgroups 六項判準全過；Amazon ESCI 四項不過 | 📚 |
| [用 Jev 幫 LlamaIndex 做重排序](#用-jev-幫-llamaindex-做重排序) | 訊號自足（段落級窄相關性） | nDCG@5 兩個資料集都顯著進步（+0.056／+0.086） | 📚 |
| [拆解判斷的代價](#拆解判斷的代價) | — | 三任務準確率↑，但困難良性案例誤判率暴增 25 倍 | 📚 |
| [生產環境的內容審核（mastra-jev-moderation）](#生產環境的內容審核mastra-jev-moderation) | 訊號自足 | 9/9 惡意訊息擋下、49 則真實訊息 0 誤判 | 📚 |
| [真實生產環境的簡體中文分類：新聞判讀「是否含湖北元素」](#真實生產環境的簡體中文分類新聞判讀是否含湖北元素) | 混合（大部分自足、分歧集中在不自足） | 跟 Flash Lite 約 85% 一致，分歧多為需要外部知識的人名案例 | 📚 |
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

### TypeSafe 首發評測：Vercel 獨立驗證與方法論批評

**做了什麼**：TypeSafe 自己在發表 Jev 時公布的「workflow evals」——九個模型對四個工作流（客服、agent trace 可觀測性、資安事件、發票處理）打分；獨立部落客 Anthony Maio 對這組評測的方法論做了批評；同時 Vercel 的 CEO Guillermo Rauch 與工程師 Pranit Kumar 在 X 上貼出把自家 `fx` 工具的指令安全審查器從 GPT-5.6 Luna 換成 Jev 後的獨立生產環境結果。三條線被 dev.to 一篇文章整理在一起、逐條質疑。

**結果**：Jev 在九個模型裡整體 67.8% 準確率、$0.0004/題、0.4 秒/題——準確率跟最強的 GPT-5.6 Sol（74.1%）差 6.3 分，但成本差 209 倍、延遲差 58 倍。拆到工作流層級，差距從 2.3 分（客服）到 17.3 分（發票處理）不等。Vercel 回報「快 5-18 倍、更準確」，但沒有附公開資料集或案例數。

**這代表什麼**：**這組評測的參考答案是 GPT-6 Astra 與 Claude Fable 5.1 兩個模型回答的平均值，不是人工標註**——量的是「跟這兩個前沿模型的共識有多接近」，不是「跟人類判斷有多接近」；兩個前沿模型共同的盲點，答對的模型反而會被扣分。Maio 引用 TypeSafe 官方原話——「我們的數字不是實證出來的。型別匹配是有保證的」——這跟本 repo「不是瞎猜」那節做的型別保證≠正確性保證的區分幾乎一模一樣，連廠商自己都這樣講。Maio 還指出一個本 repo 原本沒講到的層次：「個別校準過的判斷，串進 threshold/weight/分支之後，不會自動組成一個校準過的工作流」——這是 README「實務建議」那節複合評分建議的一條重要但書。完整整理見 [`translations/typesafe-launch-evals-zh/`](translations/typesafe-launch-evals-zh/)。

來源：[Jev Beat GPT Luna by 1 Point（dev.to）](https://dev.to/gabrielanhaia/jev-beat-gpt-luna-by-1-point-gpt-6-and-claude-wrote-the-answer-key-314k)、[Jev: The Language Model That Won't Talk（Anthony Maio）](https://anthonymaio.substack.com/p/jev-the-language-model-that-wont)

### 工具呼叫風險分級（jev-benchmark）

**做了什麼**：60 個工具呼叫案例，人工標註風險等級（readonly/destructive/privileged/exfiltration 四級），依難度分 clear／ambiguous／adversarial 三組，用 Jev 逐題分類並記錄信心值分布。

**結果**：整體 91.7% 準確率（55/60）。關鍵不是準確率，是信心值的行為：「每一個答錯的案例都伴隨著保守的信心值；模型從來沒有在答錯的時候給出 1.000」。

**這代表什麼**：這是目前收集到的資料裡，信心值行為最漂亮的一個反例——跟 jev-benchmarks 的 DAIR Emotion 案例（平均信心 0.819、實際準確率只有 48%）恰好相反，這裡展示的是校準機制正常運作的樣子。差別可能在於任務性質：工具呼叫風險分級是答案幾乎完全寫在呼叫內容本身裡的自足型任務，跟 DAIR Emotion 那種類別本身就會混淆的任務不同——支持本 repo 那條核心軸：訊號自足程度不只影響準確率，也影響信心值可不可信。完整整理見 [`translations/jev-benchmark-toolcall-risk-zh/`](translations/jev-benchmark-toolcall-risk-zh/)。

來源：[themsquared/jev-benchmark](https://github.com/themsquared/jev-benchmark)

### 信心門檻棄權（jev-dspy-lab）

**做了什麼**：用 DSPy 框架量測「信心門檻棄權」（confidence-gated abstention）行為的基礎設施，repo 附了一組用 `jev-latest` 真實跑出來的記錄——24 題客服工單分派，信心門檻設在 0.7。

**結果**：覆蓋率 95.8%（僅約 1 題被棄權），願意回答的題目中準確率 91.3%，Brier score 0.1546，ECE 0.0583。

**這代表什麼**：這是本 repo 收集到的第一個示範「棄權機制」而非單純對錯的案例——把 README「實務建議」提到的「低信心升級給人」這條路徑，量成了具體的覆蓋率／準確率數字。但樣本數只有 24 題（棄權僅 1 題），規模小到任何一題都會大幅影響數字，這條的價值在於**示範一套可以套用在任何任務上的量測方法**，不是可以直接引用的跑分結果。完整整理見 [`translations/jev-dspy-lab-zh/`](translations/jev-dspy-lab-zh/)。

來源：[jmanhype/jev-dspy-lab](https://github.com/jmanhype/jev-dspy-lab)

### 用 Jev 砍 Agent 自己的執行紀錄：一場公開辯論

**做了什麼**：跟以上所有條目都不同的用法——不是「給 Jev 一段內容問一題」，是「讓 Jev 決定 Agent 自己的工具呼叫紀錄哪些可以整條刪掉」。`fast-jev-compaction`（真實開源專案，3,482 星）取代 Claude Code 內建的摘要式壓縮，改成對每筆工具呼叫問 Jev 兩題：這筆呼叫該不該留、它的結果該不該逐字留。開發者 Tamara Tran 發布後，TypeSafe 共同創辦人 Diogo Almeida（`@CompleteSkeptic`）回覆表示認同；獨立開發者 Theo（t3.gg）公開反駁「這是一個從根本上不理解壓縮原理的糟糕策略」，點出快取經濟學（cache write 比 read 貴很多，中途刪歷史會讓後面全部用最貴的價格重寫）跟前沿模型推理 payload 遺失兩個風險。

**結果**：比雙方推特發言更有份量的，是這個專案自己 issue tracker 裡其他使用者拿真實對話重播出來的數字——[issue #26](https://github.com/tamaratran/fast-jev-compaction/issues/26)：8 個真實 session、256 筆工具結果，預設設定下 **0 筆的保留信心值超過 0.3**，因為 state 只給 Jev 看長度佔位字串，從沒讓它看過內容本身；[issue #56](https://github.com/tamaratran/fast-jev-compaction/issues/56)：合成重現顯示修 bug 所需的錯誤訊息被判定可刪，但**排序完全正確**，問題出在兩題分數落在不同量尺、同一門檻沒法比較；[issue #52](https://github.com/tamaratran/fast-jev-compaction/issues/52)：改問法後，同一組資料從全部砍光變成合理留下 40%；[issue #25](https://github.com/tamaratran/fast-jev-compaction/issues/25)：發現「相關性≠可復原性」——刪掉的舊估值重新計算只會得到今天的新值，但下游模型選擇拒答而不是編造，是一個誠實的正面訊號。針對快取批評，另一個 fork 實作了「sticky reduction」，真實測量：有幫助（省一到兩成），但還沒打平理論上的損益兩平點。

**這代表什麼**：兩造的推特發言都只對一半，issue tracker 給出的答案更細——訊號不自足（看不到內容）判斷就會失準，這跟本 repo 核心那條軸完全對得上；信心值的相對排序有真實訊號，出錯的是門檻校準這種工程串接問題，不是模型在瞎猜；而「刪除決策」本身還有一種本 repo 目前沒收錄過的新風險：有些內容一旦刪掉，重新執行不保證能復原原本的答案。完整整理（含對轉貼內容的兩處更正）見 [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/)；對應到 [`AGENTS.md`](AGENTS.md) 新增的具體警語。

來源：[tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction)、[Theo 的反駁串](https://x.com/theo/status/2100762304862384257)、[jerryfane/omp-jev-compaction](https://github.com/jerryfane/omp-jev-compaction/issues/1)

### 拿 Jev 的機率做 SQL ORDER BY 排序，站不站得住腳

**做了什麼**：三個 DuckDB 擴充套件跟一個 Postgres 擴充套件都讓你寫 `ORDER BY jev_prob(...)`，但沒有一個附上「這個順序可信嗎」的量測。這份獨立跑分補上——判準門檻跑之前就定死（pre-registered gate），用 20 Newsgroups（人工標註、跟本專案無關）測校準跟排序，再用 Amazon ESCI 真人分級商品相關性做困難探針，額外測了批次大小對數字的影響。

**結果**：簡單任務（20 Newsgroups，主題分類）六項判準全過；困難任務（ESCI，商品相關性分級）六項裡四項不過（`jev_bool` ECE 從 0.045 惡化到 0.242，逆序率從 0.143 惡化到 0.254）。另外測出：把 40 列塞進同一個 state 一次問，直接讓排序判準不過關（逆序率從 0.038 惡化到 0.171），一列一列問則過關——不是文字寫法的問題，是位置效應，批次裡越後面的列分數被拉得越靠近 0.5。

**這代表什麼**：簡單任務的好結果是能力的上限，不是下限——這跟本 repo 核心那條軸完全吻合：主題分類答案幾乎寫在文字裡，商品相關性要比對查詢的哪個面向、比對到什麼程度，落在「不自足」那一側。批次大小這個發現，跟 `translations/jev-context-compaction-debate-zh/` 的批次/內容可見度問題是同一種現象的另一面：Jev 的品質不只取決於問題設計，也取決於一次請求裡放了什麼、放了多少——而且垮的方式很安靜，排序不會報錯，只是排得不對。完整整理見 [`translations/jev-orderby-bench-zh/`](translations/jev-orderby-bench-zh/)。

來源：[yodablocks/jev-orderby-bench](https://github.com/yodablocks/jev-orderby-bench)

### 用 Jev 幫 LlamaIndex 做重排序

**做了什麼**：LlamaIndex 的 Jev 重排序器，一段一段問「這段跟查詢的相關程度」（0-3 分），跟純向量檢索（MiniLM）在 BEIR 標準評測集 `nfcorpus`／`SciFact` 上對照，附信賴區間。

**結果**：`nfcorpus`：MiniLM 0.340 → MiniLM+Jev 0.396 的 nDCG@5，進步 +0.056（95% 信賴區間 0.042–0.072，不含零），每查詢約 $0.0003；`SciFact`：0.629 → 0.715，進步 +0.086（95% 信賴區間 0.059–0.113）。

**這代表什麼**：跟上面 `jev-orderby-bench` 放在一起看特別清楚——那組的困難探針是「商品符不符合查詢的哪些面向」，不自足；這裡的重排序題目是「這一段文字跟這個查詢的相關程度」，答案完全在給定的 state 裡，自足。兩組合起來，比單看任何一組都更精確地畫出這條軸在「排序/檢索」領域的邊界：段落級窄相關性判斷能贏，商品/多面向分級相關性判斷會輸。一段一問、不批次處理的設計，也剛好避開了 `jev-orderby-bench` 測出的批次效應。完整整理見 [`translations/llama-index-jev-zh/`](translations/llama-index-jev-zh/)。

來源：[WiktorB2004/llama-index-jev](https://github.com/WiktorB2004/llama-index-jev)

### 拆解判斷的代價

**做了什麼**：我們一路建議「把判斷拆成原子化問題」，這份跑分直接測這個建議——四組分類任務，對照「一題問到底」跟「拆成 12-14 個窄問題、本地擬合權重」，除了準確率跟成本，還測了一組刻意找出來的「困難良性案例」（看起來像攻擊、其實無害的安全文件）的誤判率。

**結果**：拆解版本三個任務準確率較高（日文 NLI +7.03 個百分點最乾淨），但在困難良性案例上，誤判率從單題的 1.5% 惡化到拆解版本的 37.2%，**約 25 倍**——原因是拆出來的子問題（「是否混淆編碼」之類）對惡意文字跟合法安全文件給出同樣高的分數，分不清意圖。成本也貴 1.6-2.3 倍。

**這代表什麼**：拆解這個建議沒有錯，但「拆解一定比較準」這句話錯了——對不對取決於單題判斷是不是真的弱。原作者的優先順序值得直接搬進 [`README.md`](README.md#我能怎麼用-jev給人看)：先試免費基準線、單題夠強就停、只在真的弱的地方拆解、拆解結果只能當第二意見不能單獨扛安全把關。多分類問題也別一題問到底——記帳分類那組 12 選項單題只有 0.3998，是全部任務裡最差的結果。完整整理見 [`translations/jev-decomposition-tradeoff-zh/`](translations/jev-decomposition-tradeoff-zh/)。

來源：[Jev judge call vs dimension scores（agentjournal.dev）](https://agentjournal.dev/blog/llm-judge-vs-feature-extraction/)

### 生產環境的內容審核（mastra-jev-moderation）

**做了什麼**：Mastra agent 框架內建的審核處理器靠解析大模型的自由文字判斷該不該擋，遇到模型答不出能解析的格式時只能放行；這個專案拿 Jev 換掉這一段（一題是非、一題分類，型別化輸出、沒有文字要解析），跟內建版本（`gpt-oss-120b`）在同一批真實生產資料上對照。

**結果**：58 筆真實客服訊息（9 筆惡意＋49 筆真實問題）：Jev 版本 9/9 惡意訊息全擋下、49 則真實問題 0 誤判、中位數延遲 0.39-0.44 秒；內建版本 8-9/9、同樣 0 誤判、延遲 1.97 秒、價格約 4 倍。

**這代表什麼**：型別化輸出讓「答不出能解析的格式」這整類失效模式從架構上直接消失，不是判斷力比較強——這是我們在 README「不是瞎猜」那節「型別保證≠正確性保證」區分的另一面：這裡型別保證解決的是一種特定失效模式，不是保證永遠判斷正確。**要誠實看待樣本數**：58 筆、0/49 誤判，作者自己講「你的資料不是我們的資料，自己量」，別把這組數字當成普適結論。完整整理見 [`translations/mastra-jev-moderation-zh/`](translations/mastra-jev-moderation-zh/)。

來源：[CodeAlive-AI/mastra-jev-moderation](https://github.com/CodeAlive-AI/mastra-jev-moderation)

### 真實生產環境的簡體中文分類：新聞判讀「是否含湖北元素」

**做了什麼**：一個跑了一年的真實個人專案，每天把《人民日報》新聞分類「是否包含湖北相關元素」，原本用 Gemini Flash Lite，Jev 上線 OpenRouter 當天用同一組提示詞做了對照測試——累積近 24,000 筆真實資料，抽 1,000 筆當測試集（500 包含／500 不包含）。

**結果**：速度從 Flash Lite 的 3 秒/篇縮到 Jev 的 0.35 秒/篇，快將近 10 倍；成本約 5,000 筆花 $1；跟 Flash Lite 判斷約 85% 一致，分歧多出在文章提到「曾在湖北任職過的官員」人名時——Flash Lite 靠較大的世界知識庫認得出關聯，Jev 判定不包含。

**這代表什麼**：這是目前收錄裡最直覺易懂的一次核心軸現場示範——答案寫在文字裡的情況兩邊判斷一致，需要外部世界知識（人名跟地點的歷史關聯，文章本身沒寫）的情況才分歧，跟 `suites/history-recall-context/` 是同一種失效模式的真實生產版本，只是這次是一個素人在真實應用裡自己撞到、自己歸因對的。0.35 秒/篇這個數字剛好跟 ThaiExam 完全一樣，是一次意外的交叉驗證。**要誠實看待這不是正式跑分**：沒有絕對正解、比較基準是另一個 LLM、15% 不一致不等於 15% 錯誤率。也是目前收錄裡第一個簡體中文、真實生產規模的案例。完整整理見 [`translations/libukai-hubei-news-classification-zh/`](translations/libukai-hubei-news-classification-zh/)。

來源：[libukai 在 X 上的貼文](https://x.com/libukai/status/2100984923926728920)

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
