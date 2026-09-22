🇹🇼 中文｜🇬🇧 [English](jev-variants.en.md)

# Jev 的變體與擴展

Jev 發布後兩週內，冒出一整批「長得像 Jev」的東西：開源權重的決策模型、把 Qwen 微調成 Jev 問法的模型、不訓練直接讀本地 LLM 機率的相容伺服器，還有在 Jev 之上擴充出新操作的函式庫。這頁把它們分類整理，並標出每一個「跟 Jev 比過」的數字是怎麼來的。

**目前只有 Laya 經過我們同輸入實測**（🔬，見 [`suites/laya-head-to-head/`](suites/laya-head-to-head/)），其他全部是作者自述（📚），我們沒有驗證。完整的應用清單請看 [awesome-jev](https://github.com/yibie/awesome-jev) 的 Calibration & Research 分類，這頁只收「本身就是 Jev 的替代品或延伸」的項目。Jev、BERT、Laya 在技術上差在哪裡，見 [README 的專章](README.md#jevbertlaya差在哪裡)。

## 看任何一個變體之前，先問四個問題

這四個問題都是 Laya 對照實測裡真的踩到的：

1. **它是通用還是專用？** 在評測資料的同一個分布上訓練過，就是專用。專用模型在自己的主場贏 Jev 不稀奇（Laya 專用版高 3 個百分點），拿到沒看過的任務就是另一回事（Laya 通用版低於「不看輸入」的基準線）。
2. **表上 Jev 那一欄是誰量的？** 同一批輸入、同一套評分實際打過 Jev API，才算對照；引用別人發表的數字，樣本、提示、定義都可能不同（Laya 引用的 Jev ECE 0.144，我們用它自己的定義量到 0.041）。
3. **信心值是出廠的，還是事後調過溫度？** 調溫度用的資料如果跟測試資料重疊，校準數字會好看得不真實。
4. **state 和選項放得下嗎？** 很多變體每題各讀一次 state，上限 512 到 1024 tokens，超過就靜默截斷；選項多時每個選項會被砍短。Jev 的 state 加最長一題可到 32k tokens 📖。

## 一、從頭訓練決策輸出層的「Jev 形」模型

編碼器或小型模型加一層自己訓練的決策輸出層，一次前向就給出所有選項的機率。優點是小、快、可以自架；共同弱點是底座的知識與理解力有限。

| 名稱 | 做法 | 能直接換掉 Jev SDK 嗎 | 跟 Jev 的比較 | 標記 |
|---|---|---|---|---|
| [Laya](https://github.com/NandhaKishorM/laya) | ModernBERT-large（共 421M）／mmBERT-base（共 322M）＋決策輸出層；Apache 2.0 | 不行，自有 API，形狀接近 | 我們同輸入實測：通用版在 typed-decisions 上 0.35–0.36（Jev 0.736）、繁中意圖分類 0.61（Jev 0.93）；專用版在自己的訓練分布上 0.766 小贏 Jev，但校準誤差是 Jev 的五倍 | 🔬 |
| [von](https://github.com/wfzyx/von) | 395M 雙向 ModernBERT 的「OptionMarker」；Apache 2.0 | 自稱相容 `/v1/systemone` | 它自己的 49 任務表上 Jev 96.6%、von 72.0%；只在 ViZDoom 即時遊戲的擊殺數贏 Jev | 📚 |
| [open-jev-deberta-v3-large](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large) | DeBERTa-v3-large（0.4B），用 Banking77、SST-5、BoolQ 訓練；Apache 2.0 | 否 | 沒有比；作者說跟 Jev 的數字不能比。分布內 85.4%、分布外 69.0%，只支援英文 | 📚 |
| [nanodiff-350m-typed-decisions](https://huggingface.co/pngwn/nanodiff-350m-typed-decisions) | 350M 遮罩擴散語言模型（LLaDA 作法），在自己合成的 typed-decisions 資料上訓練；MIT | 否 | 沒有比；只在自己的合成資料上評估（ECE 0.036、準確率約 0.67）。**目前找得到唯一的擴散模型路線** | 📚 |
| [CUA-S1-FORMS](https://huggingface.co/cua-ai/cua-s1-forms) ＋ [jevlike](https://github.com/vinnylarouge/jevlike)、[jevbetter](https://github.com/olanotolu/jevbetter)、[jevlike-esp32](https://github.com/david-cermak/jevlike-esp32) | 極小的專用評分器（CUA-S1-FORMS 約 70 萬參數、2.8MB）；jevlike 是訓練函式庫，jevbetter 換了更好的編碼器，jevlike-esp32 放進微控制器 | 否 | CUA-S1-FORMS 在自己的表單評測上 99.7% 對 Jev 83.6%——專用模型在主場，而且訓練詞彙外的欄位會高信心答錯（見 [`browser-automation.md`](browser-automation.md)） | 📚 |

## 二、把開源 LLM 微調成決策模型

拿 Qwen 這類生成式模型當底座，加上決策輸出層或 adapter 微調。底座比編碼器大很多，理解力和知識比較接近 Jev，代價是要 GPU。

| 名稱 | 做法 | 能直接換掉 Jev SDK 嗎 | 跟 Jev 的比較 | 標記 |
|---|---|---|---|---|
| [decider](https://github.com/Mapika/decider) | Qwen3.5 的 0.8B／2B／35B-A3B 微調；最多 255 個選項、32k tokens；Apache 2.0 | 可以：官方 SDK 把 `TYPESAFE_BASE_URL` 指到它的伺服器即可 | [JevBench](https://benchmarkheaven.com/jev-models) 公開題（易／中／難）：Jev 1.000／0.986／0.730，decider-2b v10 1.000／0.972／0.676；另一套 Bespoke 公開題 decider 小幅領先（0.774 對 0.760）。**這是清單裡唯一自述在某套公開題上贏過 Jev 的通用模型**，我們沒有驗證 | 📚 |
| [kev](https://github.com/jaredpalmer/kev) | Qwen3.5 的 0.8B／4B／9B 加 adapter，依外部推測的 Jev 架構設計，可在 MacBook 上訓練；Apache 2.0 | 可以：本地 `/v1/systemone` | 在沒訓練過的資料上，Kev-9B 比 Jev 低 3.5 點（0.822 對 0.857，開發集）；作者明說不知道 Jev 用什麼資料訓練，不是對照實驗 | 📚 |
| [AgentJev-0.6B](https://github.com/malevrigns/agent-jev) | Qwen3-0.6B 拿掉生成文字的輸出層，換成逐一評分候選項的輸出層（選項順序不影響結果）；在 typed-decisions 訓練集上微調，屬於專用；上下文 2,048 tokens，超過就報錯、不會靜默截斷；同一題的選項共用 state 的計算；GitHub 標 Apache 2.0 | 不行：自有 HTTP 端點 `POST /api/evaluate`，是非題叫 Boolean 不叫 Noul | typed-decisions 測試集 79.25%；**在同一批題目上自己重跑的** Laya 專用版 77.00%（差距 +2.25，95% 信賴區間 +0.65 至 +3.90）。表上 Jev 的 72.7% 抄自資料集說明頁，不是它自己量的（我們實測 Jev 73.6%）。校準誤差 0.169（10 區間），約是我們量到的 Jev 0.041 的四倍。作者明寫「不能推廣為全面超過 Jev」；沒有任何沒看過題目的成績 | 📚 |
| [NanoJev](https://github.com/TianyuCodings/NanoJev) | Qwen3-0.6B 加決策輸出層，用 ViZDoom、迷宮、貪食蛇等遊戲資料訓練；MIT，附訓練流程、權重與資料集 | 否 | 遊戲任務上贏 Jev——但它就是在這些遊戲上訓練的，屬於專用 | 📚 |
| [Qwen2.5-1B-RLCD](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding) | 用 RLCD 訓練的 Qwen2.5-1B 展示頁 | 否 | 沒有比 | 📚 |

## 三、不訓練：直接讀本地 LLM 的機率

不改權重，把每個選項對應到模型輸出的機率（例如讀選項字母的 logits），在選項上做 softmax。好處是任何現成模型都能用、沒有訓練成本；限制是機率沒有經過 Jev 那種校準訓練，多半要自己調溫度。

| 名稱 | 做法 | 能直接換掉 Jev SDK 嗎 | 跟 Jev 的比較 | 標記 |
|---|---|---|---|---|
| [jevmlx](https://github.com/bnsd55/jevmlx) | Apple Silicon 上的 MLX，預設 Qwen2.5 3B／7B（4-bit）；也能接 Ollama、vLLM（但只看得到前幾名的 logprobs）；MIT | 提供 `/v1/systemone` 端點 | 排行榜上本地模型只在 20 題公開範例上量過 | 📚 |
| [jev-local](https://github.com/us/jev-local) | 預設 Qwen3.5-9B，輕量版 Qwen2.5-3B | 可以：`/v1/systemone` | 跟 Jev 公開輸出比了 5 題 | 📚 |
| [LitJev](https://github.com/zhengxuyu/litjev) | 任何 Qwen，預設 Qwen3.8-27B（一張 H100）；可把個別題目轉給底座的慢思考；Apache 2.0 | 可以：`/v1/systemone` | 沒有同輸入對照 | 📚 |
| [open-alternative-jev](https://github.com/ikermoel/open-alternative-jev) | 任何開源 LLM（Hugging Face＋vLLM），state 讀一次、所有題目一次前向；Apache 2.0 | 否 | 明說不是 Jev 的復刻、不跟 Jev 比；原始信心約高估 5 個百分點 | 📚 |
| [mini-jev](https://github.com/r-ms/mini-jev) | 預先登記的研究：凍結的 Qwen3-4B，讀選項字母的 logits 而不是生成 JSON；MIT | 否 | 沒有跟 Jev 比；結論是讀字母跟生成 JSON 準確率一樣（0.907 對 0.909）——這是整個第三類為什麼行得通的最乾淨證據 | 📚 |
| [openjev](https://github.com/zhihz/openjev) | 凍結的 Qwen3-4B，本機跑，**支援中英文** | 否 | 明說沒有任何勝過 Jev 的證據 | 📚 |
| [Jev 形公開 API](https://x.com/ekzhang1/status/2100651678110515383) | 用 Qwen3.6-35B-A3B 撐的公開 API，讓人試用 Jev 的問法 | 形狀相同 | 沒有比；只是一則推文，我們沒有確認服務是否還在 | 📚 |

## 四、擴展：在 Jev 之上長出新操作

這一類不是替代品，是**仍然呼叫 Jev**，但把它的是非題或選擇題組合成新的操作。

- [jsort](https://github.com/keltokhy/jsort)：用兩兩比較加 Bradley–Terry 模型，把文字依一個自然語言標準排序。
- [jlink](https://github.com/keltokhy/jlink)：紀錄配對，比對規則用自然語言寫，每一對給一個機率，有 Python、CLI、Stata、R 介面。
- [jselect](https://github.com/keltokhy/jselect)：在 token 預算內挑出附出處的證據給下游 AI。
- [jgrep](https://github.com/keltokhy/jgrep)：用「描述」當 pattern 的 grep。
- [DocJev](https://github.com/jerryjliu/docjev)（LlamaIndex）：文件分類與切分。

其他數百個應用見 awesome-jev；本 repo 查證過的整合案例見 [`capability-map.md`](capability-map.md)。

## 能直接看圖的變體

Jev 官方目前只收文字，圖片、聲音、影片都不收（官方寫的是「not supported (yet)」）📖。宣稱能直接吃像素的變體目前有這幾個，全部是作者自述，我們沒有測過：

| 名稱 | 做法 | 範圍 | 標記 |
|---|---|---|---|
| [PlayJev](https://github.com/OmniJev/PlayJev) | Qwen3.5-0.8B-Base 微調成視覺語言模型，一次讀一張 448px 的遊戲畫面，輸出這款遊戲可用動作的機率，低信心的步驟交給搜尋程式；Apache 2.0 | 專用：只在它訓練過的十款瀏覽器遊戲上（220 萬張畫面）| 📚 |
| [decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) | decider 的視覺語言版，一張圖加上同樣的題目格式直接做判斷；有 Hugging Face 團隊做的線上試用頁 | 通用題目格式，但作者寫明它還停在舊的 v5 權重、正在重新訓練 | 📚 |
| [LitJev](https://github.com/zhengxuyu/litjev) | 不訓練，讀 Qwen 模型的輸出機率；接上 vision 版的 Qwen 就能對截圖做判斷 | 取決於你接的 Qwen 模型 | 📚 |
| [jevlike](https://github.com/vinnylarouge/jevlike) | 小型選項評分頭的訓練函式庫；同一個評分頭也能拿圖塊當輸入（附 Doom 操作的示範影片）| 研究用的起點 | 📚 |

更常見、也更穩的做法其實不是讓模型看圖，而是**先把畫面轉成文字或結構化資料，再交給 Jev**：[jev-drone](https://github.com/RomanSlack/jev-drone) 把機上相機畫面算成深度加分割的符號場景，README 直接寫「Jev is not a vision model」；[GUI JEV](https://github.com/ZihuaEvan/GUI_JEV) 讓另一個視覺模型先描述截圖的每個格子，Jev 只在描述之間選；[jev-canvas](https://github.com/gaborishka/jev-canvas) 用 MediaPipe 追蹤手指、語音轉成文字後才問 Jev。這跟 [`browser-automation.md`](browser-automation.md) 選讀 DOM、不用截圖是同一個思路，判斷準則見 [`AGENTS.md`](AGENTS.md) 的「候選訊號本來就不是文字」那節。

## 評這個家族用的資料集

- [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)：四個工作流程、400 案測試集，我們的 Laya 對照用它。標準答案出自一個未公開的出題老師模型，衡量的是一致程度不是對錯。
- [JevBench](https://benchmarkheaven.com/jev-models)：decider 引用的公開題庫，有 Jev 1.13.0 的分數。
- [pngwn/typed-decisions-v2](https://huggingface.co/datasets/pngwn/typed-decisions-v2)、[n4ze3m/typed-decisions-synth](https://huggingface.co/datasets/n4ze3m/typed-decisions-synth)：合成資料。

## 目前的整體判斷

💭 就我們能看到的數字，**在「沒看過的新任務、直接問」這個 Jev 的主場上，開源變體大多仍落後 Jev**；贏的情況幾乎都是在自己訓練過的分布上（專用），或贏在速度、自架、成本、資料不外送。唯一自述在一套公開題上小幅領先的通用模型是 decider，我們沒有驗證。要換之前，先確認你的任務是不是固定的、手上有沒有標註資料——這兩個條件成立，變體才開始划算。

歡迎用 [`suites/laya-head-to-head/`](suites/laya-head-to-head/) 的格式補上其他變體的同輸入對照：`common.py` 和 `score.py` 已經處理好資料集與評分，加一方通常只要寫一支 `run_<模型>.py`。

**名單整理日期：2026-09-22（2026-09-23 補 AgentJev-0.6B）。** 這個領域每天在變，星數與版本以各 repo 當下為準。
