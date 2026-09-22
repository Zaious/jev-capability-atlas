🇹🇼 中文｜🇬🇧 [English](jev-patterns.en.md)

# Jev 的用法模式：不看別人做，想不到可以這樣用

這頁**按手法整理，不按領域**。能力地圖回答「它在哪裡站得住」，這頁回答「原來還可以這樣問」——很多任務要先換個問法，才看得出它其實是 Jev 的候選。

每個手法寫四樣：做法、為什麼不直覺、代表實作與證據、什麼時候會失敗。收錄門檻：**至少有一個公開、能跑的實作**，只有構想的不收（見 [`CONTRIBUTING.md`](CONTRIBUTING.md#收錄準則)）。證據標記照慣例：🔬 我們自己測的、📖 TypeSafe 官方示範、📚 第三方作者自述（我們沒有重跑）。一條「有實測數字」不等於在你的資料上也成立；只有示範、沒有數字的，也照實寫出來。

部分代表案例取自〈[Jev 應用圖譜：60 個案例](https://doc.laoyao.cn/j61zgy)〉（編號沿用 JEV-xx）與 [awesome-jev](https://github.com/yibie/awesome-jev)。整理日期 2026-09-23。

## 1. 把「生成」改成「在候選裡選」

**做法**：程式先把所有可能的答案找出來（例如用寬鬆的正規表示式撈出文件裡每一個地址或日期片段），Jev 只負責從中挑一個。

**為什麼不直覺**：抽取、排版這類看起來「要寫字」的任務，直覺會交給生成式模型。改成選擇題之後，答案一定出自原文，不可能編出來。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [預解析候選值](https://docs.typesafe.ai/cookbooks/pre_parsed_value_extraction_cookbook)（JEV-15）| 信件標頭有四個地址，問「收據要寄到哪一個」 | 📖 示範 |
| [日期要素抽取](https://docs.typesafe.ai/cookbooks/date_extraction_cookbook)（JEV-14）| 讓 Jev 挑年、月、日各是哪一段，由程式組成日期並檢查合不合法 | 📖 示範 |
| [原文保真排版](https://docs.typesafe.ai/cookbooks/autoformat)（JEV-06）| Jev 只判斷哪幾行該接在一起、每一段是什麼區塊，排版由程式做，原文一個字都不改 | 📖 示範（範例兩次往返、10,211 tokens、0.8 秒）|

**什麼時候會失敗**：正確答案如果不在候選裡，Jev 救不回來——找候選的那一步要寧可多撈、不能漏撈。

## 2. 一步一選的導航

**做法**：把搜尋或定位拆成一連串的選擇題：這一層該往哪個分支、這一頁該點哪個連結、這一段是不是答案所在。

**為什麼不直覺**：「在一棵幾千個節點的分類樹裡找位置」看起來需要一次看完全部，其實每一步只需要在十幾個選項裡選一個。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [層級分類](https://docs.typesafe.ai/cookbooks/hierarchical_classification)（JEV-16）| 在專利分類、商品分類、醫學主題詞這類多層標籤樹裡逐層往下選，保留前幾名分支同時往下走 | 📖 示範 |
| [neo4jev](https://github.com/jexp/neo4jev)（JEV-35）| 在 Neo4j 知識圖譜上，每一步從相鄰的關係裡選下一步，並判斷是否到達目標 | 📚 示範 |
| [長文件語意定位](https://docs.typesafe.ai/cookbooks/semantic_find)（JEV-05）| 條款切成帶行號的片段，逐段問「這段能不能回答問題」 | 📖 示範 |
| [瀏覽器自動化](browser-automation.md) | 每一步從畫面上的元素裡選一個動作 | 📚 多個實作，見該頁 |

**什麼時候會失敗**：錯誤會沿著路徑累積，早一步選錯，後面全錯；要保留幾條備選路徑，或允許退回上一層。

## 3. 塞進現有工具，當語意運算子

**做法**：把 Jev 包成 SQL 函數、grep、sort，或「對每個函式問一題」的命令列工具，讓原本只能比對字面的工具能依意思篩選和排序。

**為什麼不直覺**：大家想到 Jev 會想到「接進 agent」，比較少想到它可以是一個指令。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [sqlite3-jev](https://github.com/mattn/sqlite3-jev)（JEV-37）| SQLite 擴充，在 SQL 裡直接呼叫 Jev 分類每一列 | 📚 示範 |
| [every](https://github.com/sufianetaouil/every)（JEV-33）| 對程式碼裡的每一個函式問同一個是非題 | 📚 作者自己寫的 20 個函式：recall 10/10、AUROC 1.000（作者說「不是 benchmark」）；1,302 個函式 3.7 秒、0.018 美元 |
| [jgrep](https://github.com/keltokhy/jgrep) | 用「描述」當 pattern 的 grep | 📚 公開資料集上的垃圾簡訊過濾：precision 0.87、recall 0.95、F1 0.91 |
| [jsort](https://github.com/keltokhy/jsort) | 兩兩比較，再用 Bradley–Terry 模型排出順序 | 📚 分數差 1 時，Jev 約 73% 會選分數高的那個；差 3 時約 95% |

**什麼時候會失敗**：直接拿 Jev 的機率當排序依據要小心，見我們整理的 [ORDER BY 排序查證](translations/jev-orderby-bench-zh/)；要排序的話，jsort 那種兩兩比較比直接排機率更站得住。

## 4. 比對兩份東西「說的」跟「做的」一不一致

**做法**：把兩份應該一致的東西一起放進 `state`——commit 說明與程式碼差異、客服的承諾與執行紀錄、「已完成」的宣稱與實際的測試結果——問它們一不一致。

**為什麼不直覺**：很多錯誤不在任何一份文件裡，而在兩份之間。單看任一份都正常。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [jev-belay](https://github.com/valentynkit/jev-belay) | Claude Code 的 Stop hook：讀對話紀錄找證據，擋下沒有驗證就宣稱完成的回合 | 📚 100 次真實紀錄：AUROC 0.976（只看措辭是 0.777）；預設門檻下擋了 8 次、7 次擋對 |
| [jev-commit](https://github.com/valentynkit/jev-commit)（JEV-47）| pre-commit hook：commit 說明跟程式碼差異對不對得上 | 📚 示範 |
| [jev-resilience](https://github.com/Vicente-MD/jev-resilience)（JEV-44）| 回應是 HTTP 200，但內容其實是錯誤訊息或維護公告時，當成故障處理 | 📚 示範（只有離線的請求測試）|
| [progressgate](https://github.com/AshutoshVJTI/progressgate)（JEV-46）| 偵測 agent 反覆試已經被否定的假設、原地打轉 | 📚 示範 |
| [引用支持度判讀](suites/citation-support-check/) | 宣稱與引文放在一起，問引文支不支持宣稱 | 🔬 我們自己的測試 |

**什麼時候會失敗**：兩份東西都要真的放進 `state`；只給其中一份、另一份用摘要或長度代替，就是在看不到內容的情況下判斷。

## 5. 花大錢之前先問便宜的

**做法**：在呼叫大模型、叫醒 agent、升級到更貴的模型之前，先用一次 Jev 問「值不值得」。

**為什麼不直覺**：成本通常花在「不該發生的那次大模型呼叫」上，而不是判斷本身。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [wakegate](https://github.com/shitianfang/wakegate) | 睡著的 agent 被計時器或事件喚醒前，先問這次值不值得一整輪大模型 | 📚 21 個手寫情境；中位數 253 毫秒；11 次該叫醒的有 2 次是靠「不確定」區間才叫醒 |
| [jev-router](https://github.com/gargpratyush/jev-router)（JEV-48）| 依任務難度選最便宜夠用的模型 | 📚 示範 |
| [SDE cascade](https://docs.typesafe.ai/cookbooks/sde_cascade)（JEV-13）| 小模型先抽欄位，Jev 逐欄檢查，沒過的才交給強模型 | 📖 示範 |
| [第一關篩選](suites/stage1-triage-filter/) | 大模型 agent 深入處理之前，用兩題是非題先篩 | 🔬 我們自己的測試 |

**什麼時候會失敗**：閘門的門檻要用自己的資料調；wakegate 的例子裡，靠「不確定就叫醒」才沒有漏掉兩次該叫醒的情況。

## 6. 沒把握就退一步

**做法**：低信心時不硬給答案，而是退回比較粗的答案、交給人，或交給更強的模型。

**為什麼不直覺**：直覺是「沒把握就停下來」；但很多時候退一層的答案仍然有用。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [按信心退回上一層分類](https://docs.typesafe.ai/cookbooks/classification_using_confidence)（JEV-18）| SEC 文件的行業分類，沒把握時回報上一層的大類 | 📖 範例中，一組準確率 40% 的細分類，改回報上一層後是 70% |
| [第一關篩選](suites/stage1-triage-filter/) | 兩題是非題只守住兩個代價最高的極端，其他一律進有界的人工批次複查 | 🔬 我們自己的測試 |
| [信心門檻棄權](translations/jev-dspy-lab-zh/) | 低於門檻就不答，量出覆蓋率與準確率的取捨 | 📚 見該條目 |

**什麼時候會失敗**：校準是群體統計，不是單題保證；類別本身糊在一起時，它可能很有把握地錯（見 README 的 DAIR Emotion 例子）。

## 7. 一次多問，連「可能用得上」的問題一起問

**做法**：同一份 `state` 的問題一次送出，包括還不確定需不需要的；回來之後由程式決定用哪幾題的答案。

**為什麼不直覺**：多問幾題幾乎不增加等待時間（官方說法），所以「先問再說」比「需要時再問」便宜。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [Speculative fan-out](https://docs.typesafe.ai/patterns/fan-out) | 官方的模式說明 | 📖 |
| [同一份文件的多維判斷](https://docs.typesafe.ai/cookbooks/parallel_questions)（JEV-03）| 一次請求對同一份 GDPR 文件做多個判斷、分類、評分 | 📖 示範 |
| [jev-torneo-animales](https://github.com/hectorlcastro09/jev-torneo-animales) | 擂台賽：一次請求就問衛冕者對接下來 K 個挑戰者，衛冕者一輸就丟掉後面的答案 | 📚 作者自述 1,999 場約 16 秒 |
| [瀏覽器自動化](browser-automation.md) | 每一步同一次呼叫問三題：下一個動作、目標達成了沒、是不是卡住 | 📚 見該頁 |

**什麼時候會失敗**：每題是獨立評估的（官方說法），題目之間不會互相參照；要組合答案，得在程式裡做。

## 8. 當傳統機器學習的特徵

**做法**：Jev 不下最終判斷，而是對每筆資料回答一批問題，把機率當成特徵，交給 CatBoost 這類傳統模型去學。

**為什麼不直覺**：大家把 Jev 當「判斷者」，很少想到它可以是「特徵產生器」，讓自己的標註資料決定權重。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [Autoresearch 特徵發現](https://docs.typesafe.ai/cookbooks/autoresearch_feature_discovery)（JEV-17）| 反覆提出新問題當特徵，用模型的錯誤決定要不要留下這個問題 | 📖 示範 |
| [拆解判斷的代價](translations/jev-decomposition-tradeoff-zh/) | 一題直接判斷 vs 拆成十幾個維度再學權重 | 📚 見該條目 |

**什麼時候會失敗**：拆解不會自動比較準；那份第三方測試發現，拆解在困難的良性案例上誤判率暴增（見該條目）。

## 9. 重問幾次，看答案穩不穩

**做法**：同一題問好幾次，用答案一不一致當作額外的不確定訊號。

**為什麼不直覺**：大家只看單次的信心值；但答案會在重問之間變動，本身就是一個訊號。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [分類一致性](https://docs.typesafe.ai/cookbooks/consistency_choice_cookbook)（JEV-02）| 內容審核的邊界案例重複分類 | 📖 重問時選出同一答案的比例：Jev 90.8%，幾種大模型設定 87.5% 到 100% |
| [是非題一致性](https://docs.typesafe.ai/cookbooks/consistency_noul_cookbook)（JEV-01）| 車險理賠的多個事實判斷 | 📖 示範 |
| [純回憶史實題](suites/history-recall-context/) | 每題重問三次 | 🔬 有唯一答案的題三次完全一樣；沒有唯一答案的題三次之間會變動，甚至換選項 |

## 10. 媒體先轉成帶時間戳的文字，再逐句掃

**做法**：影片、聲音、長篇內容先轉成一句一句的文字（附時間戳），再對每一句問同一題。

**為什麼不直覺**：Jev 只收文字，看起來跟影音無關；但字幕和逐字稿本來就是現成的文字。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [jev-skip](https://github.com/valentynkit/jev-skip)（JEV-32）| 讀 YouTube 字幕，標出業配片段 | 📚 23 支影片：抓到 SponsorBlock 使用者標記的業配秒數 77%，每小時誤跳 34 秒，每支影片 0.0008 美元 |
| [判斷玩家在對哪個 NPC 說話](https://github.com/wondertwins/jev-benchmark) | 讀一句語音轉文字，對每個 NPC 問「是在跟你說話，還是只是提到你」 | 📚 F1 0.96；全小寫、沒標點、名字被聽錯的逐字稿上 0.93；比模糊比對名字的做法（64%）準很多（92%）|
| [jevmeter](https://github.com/ChetasLua/jevmeter)（JEV-52）| 影片逐句評分，疊在畫面上 | 📚 作者自己的評測集 99% |
| [jev-audio-beeper](https://github.com/santos-sanz/jev-audio-beeper)（JEV-53）| 西班牙語逐字稿逐詞判斷要不要消音 | 📚 示範 |
| [Jev 校稿](suites/zh-proofreading/) | 對 repo 裡的中文逐句問有沒有寫錯字 | 🔬 門檻 0.5：抓到 67% 的學生錯字，repo 正確句子誤報 2% |

## 11. 感知先交給別的工具，轉成符號或文字

**做法**：畫面、感測器、語音先由別的工具轉成結構化資料或文字（OCR、DOM、深度圖、手勢追蹤），Jev 只判斷轉出來的東西。

**為什麼不直覺**：直覺是「要看圖就找視覺模型」；但很多系統早就算好了那個訊號，只是沒有露出來。判斷準則見 [`AGENTS.md`](AGENTS.md) 的「候選訊號本來就不是文字」。

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [typesafe-computer-use](https://github.com/awlevin/typesafe-computer-use)（JEV-30）| macOS 螢幕先 OCR，再讓 Jev 選下一個動作 | 📚 同一張截圖：每次決策 0.0002 美元、0.13 到 0.38 秒；直接把截圖丟給 Claude Opus 5 是 0.032 美元、5.2 秒（量的是成本與速度，不是準確率）|
| [mobile-jev](https://github.com/droidrun/mobile-jev)（JEV-29）| 讀 Android 介面，選點擊或輸入 | 📚 示範 |
| [jev-drone](https://github.com/RomanSlack/jev-drone)（JEV-57）| 相機畫面先算成深度與分割的符號場景 | 📚 示範 |
| [瀏覽器自動化](browser-automation.md) | 讀 DOM，不看截圖 | 📚 見該頁 |

## 12. 小而意外的用途

| 代表 | 做了什麼 | 證據 |
|---|---|---|
| [unclutter](https://github.com/kitze/unclutter)（JEV-31）| 瀏覽器擴充：判斷網頁上哪些元素是廣告、推廣、訂閱彈窗，做成可重複使用的規則 | 📚 示範 |
| [hono-jev-router](https://github.com/yusukebe/hono-jev-router)（JEV-36）| 依請求的意思分派 HTTP 路由 | 📚 示範 |

## 看起來可以，其實不該這樣用

這些是我們自己查過或測過、結論是「不行」或「要非常小心」的：

- **讓 Jev 決定刪掉 agent 自己的執行紀錄**：那是不可逆的刪除決策，不是一個判斷題；見 [context 壓縮辯論](translations/jev-context-compaction-debate-zh/)。
- **預測還沒發生的人類行為**（這則訊息會不會被回覆、這個客戶會不會成交）：判斷當下答案還不存在；見 [`AGENTS.md`](AGENTS.md) 的「別碰的地方」。
- **多回合策略、從隱藏資訊推對手**：撲克和西洋棋都示範過失敗；見 [`analysis/jev-games-tcg.md`](analysis/jev-games-tcg.md)。
- **需要它自己記得的知識**：知不知道事前看不出來；需要的資料放進 `state`。
- **查簡體字**：字元清單比 Jev 準，而且零成本；見 [Jev 校稿](suites/zh-proofreading/)。

## 標籤

💭（手法的歸類是我們的判斷；每個代表的證據在表格裡個別標 🔬／📖／📚）
