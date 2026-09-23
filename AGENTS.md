🇹🇼 中文（本頁）｜🇬🇧 [English](AGENTS.en.md)

# AGENTS.md — 給 agent 讀

**開始前先讀 [`README.md`](README.md) 裡「它不是狀態機，也不是瞎猜」那節。** 不管你是模式 A 還是模式 B，你很可能之後要跟別人（使用者、團隊）描述 Jev 是什麼——**不要用「狀態機」或「瞎猜」這種簡化說法**，也不要反過來說它「會思考」，這兩種簡化都是錯的，那節講清楚為什麼。這不是選讀的背景知識，是會影響你怎麼下結論、怎麼措辭的東西。

先判斷你是哪一種情境：
- 被叫去看**別的專案**，評估哪裡適合換成 Jev → 讀「模式 A」
- 被叫進**這個 repo** 本身，要跑既有測試、加新測試、或回報結果 → 讀「模式 B」

---

## 模式 A：評估別的專案哪裡適合換 Jev

你被叫進來，是因為有人想知道現有專案裡有沒有地方適合把一顆慢/貴的 LLM 呼叫，換成 TypeSafe 的 Jev（快、便宜、但只能做窄範圍型別化判斷）。這份文件是判準與掃描清單，不是背景知識讀物——先讀完整的能力地圖（[`capability-map.md`](capability-map.md)，[English](capability-map.en.md)）再開始掃。

### 唯一的判準

> **這個判斷的正確答案，能不能完全從你已經準備好要餵給它的內容裡讀出來，不需要另外的世界知識或跟其他東西比較？**

能 → 候選。不能（需要外部知識庫、需要跟整個領域比較、需要純粹的事實回憶且沒有給支撐段落）→ 不是候選，別硬套，見第三方真實案例 [湖北新聞分類](translations/libukai-hubei-news-classification-zh/)（文章沒寫的背景關聯，它比大模型弱）。它不一定不知道——[`suites/history-recall-context/`](suites/history-recall-context/) 的冷門史實題它不給背景也答對了——但知不知道事前看不出來，所以一樣不算候選，除非你先把資料放進 `state`。

### 候選訊號本來就不是文字（畫面/聲音/感測器）時，先問這句

**系統內部有沒有已經算過這個訊號、只是沒有暴露出來？** 多數情況下答案是有——系統早就用某種內部演算法/資料結構算過那個訊號，只是沒有把它變成文字露出來。先查、先暴露這個既有計算，幾乎是免費的，保真度也天生比重新接一個模型去「感知」還高：

- [`browser-automation.md`](browser-automation.md) 裡的兩個真實整合都選讀瀏覽器本來就有的 DOM，不用截圖——不是視覺模型讀不懂畫面，是瀏覽器系統本來就已經把畫面狀態算成結構化資料了。
- [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/) 裡預設設定失敗，是因為 state 只給 Jev 看長度佔位字串——內容明明都在，只是沒有露出來，不是內容真的取不到。
- [`suites/icu-alarm-classification/`](suites/icu-alarm-classification/) 失敗的兩個類型，本質是我們自己粗糙地重新算一次波形特徵，算得比監測器內部本來就在跑的演算法還差。

**只有真的從來沒有任何既有系統計算過那個訊號**（例如相機對著真實世界判斷水果熟不熟、判斷一道牆有沒有結構性裂縫），才真的需要另外接一個感知/轉換模型——這種情況下感知模型是必要步驟，不是圖方便的補丁；先分清楚你的候選屬於哪一種，再決定要不要動手接。

真實例子幾乎都是「先轉成文字再交給 Jev」：[jev-drone](https://github.com/RomanSlack/jev-drone) 把機上相機畫面先算成深度加分割的符號場景，再讓 Jev 判斷；[GUI JEV](https://github.com/ZihuaEvan/GUI_JEV) 讓另一個視覺模型先描述截圖的每個格子，Jev 只在描述之間選；[jev-canvas](https://github.com/gaborishka/jev-canvas) 用 MediaPipe 追蹤手指、語音轉成文字後才問 Jev。Jev 官方目前只收文字 📖。也有直接吃像素、長得像 Jev 的開源變體，但目前都是專用或未經驗證，見 [`jev-variants.md`](jev-variants.md#能直接看圖的變體)。

### 官方硬限制：掃之前先知道

出自 [TypeSafe 官方 Models 頁](https://docs.typesafe.ai/models) 📖，掃到候選時先對一次，有些候選在這一步就出局：

- **只收文字**：state 必須是字串、JSON 物件或文字陣列，不收圖片、聲音、影片。
- **長度**：每次請求 64k tokens；state 加上最長的那一題最多 32k tokens。超過就要先切分或摘要，不能直接當候選。
- **不能微調**：所有帳號共用同一組權重，只能靠 state、instructions、criteria 調整。「拿我們的資料訓練一下就好」這條路不存在；需要微調的話，看 [`jev-variants.md`](jev-variants.md) 的開源變體。
- **語言**：英文最好，其他語言（含中日韓）官方說準確率較低，要用你自己的資料驗證。我們測的繁中意圖分類是 0.93 🔬（[`suites/laya-head-to-head/`](suites/laya-head-to-head/)），但那是單一任務，不代表你的任務。
- **價格與速率**：每百萬 input tokens 0.042 美元、output 不收費；速率上限官方註明會動態調整。

### state 就是送出去的東西

Jev 是雲端 API，沒有地端版本——**你放進 `state` 的每一個字都離開了這台機器**。掃描候選時，除了問「答案在不在 state 裡」，還要問「這些內容能不能送出去」。一個第三方實作把這件事做得很細，值得照抄它的分層（📚 [hermes-jev-skills](https://github.com/kerpopule/hermes-jev-skills)，整理見 [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)）：

- **能遮的先遮、能換 id 的先換**：信箱、電話、token、長十六進位一律遮蔽；檢索段落的來源 id、路徑與檔名換成 `P0`、`P1`……只送內容不送出處。
- **先解碼再篩，不然篩不到**：電子報頁尾會把收件人地址 percent-encode 在退訂連結、base64 在追蹤連結裡，純文字的遮蔽器兩個都看不到。任何「送出前掃一次敏感字」的機制，都要先把 quoted-printable、percent-encoding、HTML entity、base64 解開再掃。
- **整段不送，比遮蔽更可靠**：看起來像憑證的段落、看起來帶機密的那一輪，直接不送，不要指望遮蔽器抓得乾淨。
- **敏感路徑改送粗特徵**：長度、有沒有程式碼、有沒有風險字眼——這些足以做路由這類決策，而且原文完全沒有離開機器。
- **注意誰先動作**：如果判斷發生在 agent 行動之前（例如模型路由），那麼「叫 agent 不要送客戶資料」這條指示對它無效——那一輪的字在 agent 有機會判斷之前就已經送出去了。

### 掃描清單：找什麼樣的程式碼

依訊號強度排序，`grep` 得到的具體模式：

1. **現有的 LLM 呼叫，提示詞要求分類/評分/是非，輸出只被解析出一個標籤**——找 prompt 裡有「classify」「categorize」「rate 1-10」「which of the following」字樣，且回應之後被 regex 或 `if response ==` 這種方式抽出一個值，自由文字本身沒被使用。這是最強訊號：目前花一整顆模型的錢，只換回一個窄答案。
2. **手寫的 regex/關鍵字分類器，自己土法煉鋼算信心**——找函式名像 `classify_*`/`score_*`/`detect_*`/`triage_*`，註解或回傳值裡出現「confidence： high/medium/low」這種人工分級。這種地方通常已經在用啟發式湊信心值，換成真的校準過的機率是直接升級。
3. **因為成本/延遲設了人為上限的高頻小決策**——找註解裡寫「只查前 N 筆」「預算限制」這種話，旁邊接著一個分類/路由判斷。上限存在的原因往往是現有方案太貴太慢，不是任務本身不需要做。
4. **已經有分類/篩選，但字面比對/正則抓不到語意層的錯誤**——例如字面重疊比對抓不到「用詞相同但意思相反」的案例（見我們自己的引用查核與反諷測試）。

**掃完程式碼特徵，再對照 [`jev-patterns.md`](jev-patterns.md) 的手法**：有些候選要換個問法才看得出來——例如抽取改成「在候選裡選」、長文件定位改成「一步一選的導航」、「兩份東西一不一致」、「花大錢之前先問便宜的」。

### 別碰的地方

- **安全關鍵、後果不可逆的閘**（刪除操作、支付、發送、權限判斷）——這類邏輯該留在確定性程式碼，不該讓任何機率模型（不管多快）接手最終決定。這不是 Jev 的問題，是「不可逆動作不該交給任何機率輸出」的一般原則。
- **需要它自己解釋理由的地方**——它結構上做不到，見官方文件：不產生文字、不產生程式碼、不解釋推理過程。
- **需要跟整個領域/市場比較的評分**（新穎性、重要性、「這個好不好」）——除非你先做檢索、把要比較的對象也放進 state，不然文字本身沒有答案。
- **已經有一個跑得好的零成本確定性腳本在做同一件事**——沒有失敗案例就別加模型進去，這違反「同一種失敗兩次才建閘」的一般紀律，加模型也一樣適用反過來的版本：沒有問題就別加。
- **用 Jev 決定要不要刪掉 Agent 自己過去的執行紀錄（工具呼叫/結果）**——這不是「回答一個判斷」，是「做一個可能不可逆的刪除決策」，性質不同，真實案例見 [`translations/jev-context-compaction-debate-zh/`](translations/jev-context-compaction-debate-zh/)。至少要做到三件事才考慮：①打分用的 state 要包含輸出內容本身，不能只給長度佔位字串（否則是在看不到內容的情況下判斷，見 [issue #26](https://github.com/tamaratran/fast-jev-compaction/issues/26)：256 筆真實工具結果裡 0 筆保留信心值超過 0.3）②失敗的指令、還沒被取代的計算結果、任何「重新執行不保證拿到同一個答案」的輸出，先用規則保護起來，不要交給機率門檻（見 [issue #25](https://github.com/tamaratran/fast-jev-compaction/issues/25) 的「相關性≠可復原性」）③如果快取成本是考量，重寫的前綴要盡量逐字不變，不要每次請求都重新打分（見 [issue #1 sticky reduction](https://github.com/jerryfane/omp-jev-compaction/issues/1)）。**2026-09-23 補一筆更強的證據**：一個第三方實作把這件事完整量過，結論是把 Jev 拿掉——七個真實 session、104 題回憶考，Jev 挑回合寫出來的摘要 37.5%，輸給單純取尾段的 48.1%（逐題 4 勝 15 敗），出貨版改成不用 Jev。關鍵是它的失敗理由跟上面那三條都不一樣：**state 給齊了，Jev 的判斷也確實比「取最近的」好（逐題 11 勝 4 敗），輸的是「挑回合」這個問題形狀本身**——留下來的回合仍然只保留前 400 字元。教訓是：把任務改寫成 Jev 能答的形狀之後，還要再問一次「這個形狀本身能不能完成原本的工作」。見 [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)。
- **預測還沒發生的人類行為**（這則訊息會不會被打開/回覆/轉換、這個潛在客戶會不會成交）——判斷當下根本沒有正解可以核對，要等事後真實結果出現才有得驗證；掛一個信心分數上去不會讓預測本身變得可信，TypeSafe 自己都說校準要拿你自己的資料驗證過，這種任務連「驗證過」這件事在判斷當下都做不到，是「需要跟整個領域/市場比較」的一個更極端的版本——不是資料不在 state 裡，是**答案本身此刻還不存在**。真實案例：一則產品創辦人（非獨立第三方，本人就是要推銷的服務的創辦人）宣稱「40 秒預測 700 則外展訊息的成效」，宣稱的可驗證性本身就有結構性問題（[原推文](https://x.com/romanbuildsaas)）；同一間公司既有、非 Jev 版本的評分功能，已經被獨立評測點名「評分機制不透明，你看不到訊號權重」——掛上 Jev 的信心分數不會讓一個本來就不透明的預測變得可信。**一個容易犯、連我們自己都差點犯的變體**：把「預測結果」拆成「判斷跟結果直覺上相關的內容屬性」（例如用 hook 夠不夠力、格式對不對這類通識性文案判準，去代替「這篇會不會被目標平台的演算法優先推播」），屬性本身是自足、可判斷的沒錯，但**屬性跟你真正關心的結果之間有沒有關聯，是另一個完全沒被驗證過的假設**——通識性判準（好文案的共通原則）不等於目標系統真正的獎勵函數（例如 X 演算法實際加權的是回覆-被原作者回覆 150 倍、轉發 20 倍這類具體動作，不是「情緒張力夠不夠」），沒有人驗證過兩者相關，就不能拿一個代替另一個。跟 [`capability-map.md`](capability-map.md#拆解判斷的代價) 那條「拆解不會自動繼承正確性」是同一種錯誤的另一個面貌。

### 寫題目：必要條件跟偏好要分開寫

Jev 拿你給的選項去對你給的 `state` 評分，**它沒辦法知道你 state 裡哪一行才是有約束力的那一行**——所以一個你只當成加分項的屬性，會被它當成硬性篩選條件。一個在生產環境用 Jev 的廠商回報，他們最大的一次準確率跳升來自改寫一句話：原版把整份 brief（主題、語氣、格式、受眾）寫進去，44 支人工標註影片答對 16 支；改成「主題是條件，其餘明說是用來打破平手的偏好」之後是 33 支。同模型、同測試集、同程式路徑。

三種題型各自的寫法：

- **Choice**：先點名決定性的那個屬性，再點名只用來打破平手的。**沒有標的第二個屬性會被讀成必要條件**。
- **Score**：說明哪幾個等級被必要條件把關、哪幾個吸收偏好。兩者混在一起，中間那幾級就不代表任何東西。
- **Noul**：咬得最兇——一個藏著「而且還要……」的是非題其實是兩題，把必要條件先問，偏好分開問或乾脆不問。

**但書**：這條的一手來源是廠商自述的 X 貼文（n=44、沒有逐案拆解，我們無法直接查證，轉述來源見 [`translations/hermes-jev-skills-zh/`](translations/hermes-jev-skills-zh/)）。當成一個值得在自己資料上試並量測的預設，不是定律。同理，別用「調低信心門檻」去補救一個同時在回答兩件事的題目——門檻是對著一題校的。

### 驗證候選的最小流程（照抄我們自己的做法，不要跳過）

找到候選後，不要憑判準直接動手改，先驗證：

1. 從現有系統挑 10–20 筆**真實**歷史輸入/輸出（不是編的）。
2. 寫一個最小的 Choice/Score 呼叫，對這批真實資料**真的打 API**（需要 `TYPESAFE_API_KEY`，見 [`scripts/common/`](scripts/common/) 的樣板）。**送出前先把要送的 state 印出來校一次，並把實際送出的 state 存進結果**——Jev 不會提醒你輸入有錯：我們自己的歷史題把正確選項打錯一個字，它以 0.90 的信心選了錯的答案（[`suites/history-recall-context/`](suites/history-recall-context/)）。state 如果是從 OCR、爬蟲或使用者輸入組出來的，上游的清洗也是這一步的一部分。
3. 跟現有方案（regex/舊分類器/舊 LLM 呼叫）的結果並排比較，看分歧率跟信心分布——不是看單一好看的案例。要比延遲的話，第一次呼叫要排除：建立連線會讓它慢 2–3 倍（[`suites/jev-latency-distribution/`](suites/jev-latency-distribution/)）。
4. 只有在真實數據支持時才動手整合，而且**先當第二意見疊加，不要直接取代**——跟我們的 pilot 一樣，先跑幾輪確認再考慮扶正。放進延遲敏感的路徑時，服務啟動後先打一次暖機呼叫。
5. 把結果（不管好壞）貢獻回 [`suites/`](suites/)——這正是這個 repo 存在的理由。

**如果候選是瀏覽器自動化**（點擊、填表、導覽這類操作型任務），別從零設計架構——讀 [`browser-automation.md`](browser-automation.md)：三個真實開源實作收斂出的參考架構（一次呼叫問三題）、打字問題怎麼解、以及接自己系統前的檢查清單。

**如果候選是虛擬角色的表情或動作**（AI VTuber、VRChat、視覺小說演技、Live2D 角色），讀 [`virtual-character-expressions.md`](virtual-character-expressions.md)：先用那頁的決策表確認你的標準答案是哪一種。有兩個形狀我們量過、是死的——**「自己說話→自己的臉」**（標準答案是說話者自己的意圖，人類天花板只有 0.524，而且缺的訊號在你剛用 STT 丟掉的音訊裡）與**聆聽表情**（打不過「一律中性」，給它完美的角色情緒追蹤器也是 +0.000）。

**如果你想建議把 Jev 換成自架的開源替代品**（Laya 或其他變體），先讀 [`jev-variants.md`](jev-variants.md) 跟 [`suites/laya-head-to-head/`](suites/laya-head-to-head/)：目前的開源變體在「沒看過的新任務、直接問」上大多落後 Jev，贏的幾乎都在自己訓練過的分布上。提建議之前，先確認使用者手上有沒有標註資料、流程是不是固定的。

### API 機制去哪查

呼叫方式、Choice/Score/Noul 怎麼設計、confidence 怎麼用——去讀 TypeSafe 官方的 [skill](https://github.com/typesafe-ai/skills)，那裡寫得很完整，這裡不重複。

---

## 模式 B：在這個 repo 裡工作——跑測試、加測試、回報結果

### 環境設定

```bash
pip install "typesafe-sdk>=0.5.7" --extra-index-url https://pypi.typesafe.ai/
export TYPESAFE_API_KEY=<你的 key>          # 早鳥候補制,見 typesafe.ai
python scripts/common/jev_client.py         # 自檢:零成本,確認服務活著(故意用錯 key 打一發 401)
```

### 跑既有測試組

```bash
python suites/<slug>/run.py
```

每支 `run.py` 都會真的打 API，把回應存進 `suites/<slug>/runs/<日期>.json`，同時印出結果到終端機。**不要手動修改 `runs/` 裡的檔案**——那是收據，改了就不是收據了。

### 新增一組測試

1. `cp -r suites/TEMPLATE suites/<你的 slug>`
2. 照現有 suite（例如 `suites/history-recall-context/`）的樣板寫 `data/cases.json` + `run.py`（import `scripts/common/jev_client.py`，不要重寫存取邏輯）；`run.py` 要能用 `--dry-run` 只印出將送出的 state，收據裡也逐題存下實際送出的 state——歷史題的錯字就是因為這兩件事都沒做才漏掉的
3. 真的執行，產出 `runs/<日期>.json`
4. 填 `README.md`（對照 `suites/TEMPLATE/README.md` 的區塊）跟 `protocol.yaml`
5. README 裡有彙總數字（準確率、敏感度這類）的話，附一支從收據重算的腳本，加 `--check` 在數字對不上時 exit 1（照 [`suites/icu-alarm-classification/metrics.py`](suites/icu-alarm-classification/metrics.py)）——文字跟收據才不會悄悄分岔。
6. **回報結果前，對照 `CONTRIBUTING.md` 的 PR checklist 自己先檢查一次**——尤其是「每個數字都對應一筆真實 log」跟「標了 🔬/📚/📖/💭 之一」這兩條；最後跑一次 `python scripts/zh-check/check_zh.py`，確認沒有混進簡體字；有 API key 的話再跑 `python scripts/zh-check/proofread_jev.py`，把它列出的可疑句子逐句看過

### 回報結果——具體協定（這是重點，不要只說「我跑了，結果不錯」）

依你手上的權限分兩種做法：

**有 push/PR 權限的 agent**：
```bash
git checkout -b suite/<slug>
git add suites/<slug>/
git commit -m "suite: <slug> — <一句話結論,例如「反諷偵測跨句版 10/10」>"
git push -u origin suite/<slug>
gh pr create --title "suite: <slug>" --body "<貼 README.md 的結果摘要 + 標籤(🔬/📚/📖/💭)+ runs/ 檔名>"
```

**沒有 push 權限、只是被使用者臨時叫去跑一次的 agent**：不要只回報結論，把這些東西**逐項列出來**給使用者：
1. 產生了哪些檔案（完整路徑）
2. 測試組 `README.md`（外部來源條目則是 `report.md`）的內容全文，不是摘要
3. 每個案例的 `choice`/`confidence`/`probabilities`，不是只講對錯
4. 明講這是 🔬 全新測試、還是複測既有 suite、還是純分析
5. 一句話說使用者接下來可以怎麼做（自己開 PR、還是要你幫忙開）

**兩種情況都適用的底線**：回報結果**必須**附真實 `runs/*.json` 的內容或路徑，不能只憑印象講「大概八成準」。這條規則對 agent 跟對人類貢獻者是同一條——見 `CONTRIBUTING.md`。
