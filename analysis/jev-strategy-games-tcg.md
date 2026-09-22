🇹🇼 中文｜🇬🇧 English below

# Jev 用在策略遊戲與集換式卡牌（TCG）：現有證據與設計原則

整理日期：2026-09-22

## 這篇分析在講什麼

**集換式卡牌（TCG）目前沒有任何公開的 Jev 實測**；最接近的證據來自西洋棋和撲克，兩者講的是同一件事：**決定成敗的不是模型，而是你事先幫它算好了多少事實。** 只給原始盤面，Jev 下棋跟亂走一樣；由程式先算好每一步的後果，它能下到約 950 Elo。撲克裡，一個只會比較「勝率 vs 底池賠率」的簡單規則機器人，打贏了 Jev。放到 TCG 上：凡是程式算得出來的——合法動作、每個動作的結果、傷害、斬殺線、資源——都要先算好放進 `state`，Jev 只負責在這些事實之間做選擇；多回合規劃、讀對手的隱藏資訊，不要單獨交給它。

## 依據哪些既有條目/證據

中英文都搜過（2026-09-22），找不到任何「Jev＋TCG」的專案或討論。以下是最接近的第三方實測，都是作者自述、我們沒有重跑：

- 西洋棋：[wondertwins/jev-benchmark](https://github.com/wondertwins/jev-benchmark)
- 撲克：[backnotprop〈Jev is the fish at the poker table〉](https://backnotprop.com/blog/jev-poker/)（2026-09-17）、[dperezcabrera/jev-poker](https://github.com/dperezcabrera/jev-poker)
- 寶可夢紅版：[valentynkit/jev-plays-pokemon-red](https://github.com/valentynkit/jev-plays-pokemon-red)
- 其他遊戲專案（井字棋與四子棋對照、星海爭霸、Doom、2048）與直接讀遊戲畫面的變體，見 [awesome-jev](https://github.com/yibie/awesome-jev) 的 Game & Simulation 分類與 [`jev-variants.md`](../jev-variants.md)
- 本 repo 的核心判準（答案能不能從給它的內容讀出來）見 [`README.md`](../README.md)

## 分析/論述

### 西洋棋：事實比模型重要 📚

wondertwins/jev-benchmark 用 30 個中盤局面、25 題一步殺，以 Stockfish 19 當標準答案，合法性、盤面與計分都交給程式，Jev 只在 20 到 40 個合法走法裡挑一個。原文的結論：「No better than random from a raw board. Beats random by ~65% with code-supplied facts and ~78% with one-ply tactical facts. Finds mate-in-one 24% of the time. With tactical facts it plays at roughly 950 Elo on a Stockfish-anchored ladder: checkmates every bot up to ~650, loses to depth-1 Stockfish (~1166).」

這裡的「程式算好的事實」是 python-chess 先算的東西：雙方棋子、子力、哪些子被攻擊、有沒有保護、每一個合法走法走完之後那顆子會不會被吃。「一步戰術事實」再加上交換後的淨子力、會不會造成或被將殺、新產生的威脅——全部只看一步、沒有搜尋。作者的說法是 Jev 的工作從「讀這張字母格子然後下棋」縮成「已知這個主教會被吃，哪一步合理？」。同一個 repo 也發現，直接在 ASCII 棋盤上問「白方是不是被將軍」這類是非題，結果只比永遠猜多數答案好一點點——**它讀不出盤面幾何，要程式先算**。速度：40 個選項時中位數 0.2 秒；每一步約 2,100 input tokens。

### 撲克：簡單的算術規則打贏了 Jev 📚

**跟求解器比**（backnotprop）：作者用 TexasSolver 解了一個翻牌局面（單挑、100 個大盲深、可剝削度 0.59%），試了五種問法、30 個局面：「Across 30 random spots it matched the solver's top action 63% of the time.」簡單的局面沒問題（「Jev calls at 94%, the solver calls at 96%.」），但拿到最大牌、面對過牌或全下時，「Jev shoved in sixteen runs out of sixteen」，而求解器 100% 選擇過牌——作者的解釋：「you hold the nuts, so shoving four times the pot gets called by nothing you beat, and folds out every hand that would have paid you.」

**實際打 300 手**（jev-poker，6 人桌：2 個 Jev、2 個只比較勝率與底池賠率的規則機器人、2 個隨機）：每 100 手的大盲輸贏，規則機器人 +134.8、Jev +29.6（標準誤 57.6，作者說「is not a profit」，跟打平分不出來）、隨機 −164.4。Jev 的問題是棄牌太多：「against a bet of ten big blinds or more it folds 83% of the time, with 38% equity on average when it does.」成本不是問題：941 次決策、每次 268 毫秒、總共 0.040 美元。

### 寶可夢紅版：只在分岔點問 📚

valentynkit/jev-plays-pokemon-red 把路線和所有算術交給程式，只在遊戲真的出現分岔時才問 Jev，而且只讓它在程式確認過合法的動作裡挑。每回合的「這一招會不會把對手打昏」預測拿 Brier 分數對照遊戲記憶體的實際結果——但作者刻意還沒公布校準數字，因為免費額度下最長的一段只有 5 回合。

### 所有遊戲專案的共同做法 📚

1. 遊戲引擎負責規則，列出所有合法動作。
2. 每個合法動作是 Choice 的一個選項（一題最多 255 個選項），結構上不可能走出不合法的步。
3. 最好把「選了這個會發生什麼」寫在選項裡，例如結果盤面。
4. 算術和規則交給程式，Jev 只在分岔點選擇。

### 放到 TCG 上 💭

照本 repo 的核心判準——答案能不能從給它的內容直接讀出來——TCG 的決策可以這樣分：

**適合交給 Jev 的**（事實都能先算好放進 `state`）：
- 引擎列出合法動作、每個動作都附上結果時，從中挑一個
- 起手要不要換牌：手牌、牌組的打法、對手可能的牌型都寫進去
- 選目標、選要攻擊誰
- 「這一波打得死嗎」：傷害由程式算好寫進去，讓 Jev 讀結果，不要叫它自己算

**不適合單獨交給 Jev 的**（西洋棋和撲克都示範過失敗）：
- 多回合規劃與出牌順序
- 從隱藏資訊推對手手牌、判斷虛張聲勢
- 戰鬥算術、連鎖效果結算

這些要搭配程式的搜尋，或把低信心的決策升級給大模型或人——直接讀遊戲畫面的變體 PlayJev 就是把低信心的步驟交給搜尋程式（見 [`jev-variants.md`](../jev-variants.md)）。

**卡牌文字要放進 `state`**：TCG 跟棋類最大的不同是每張牌都有自己的規則文字。照核心判準，Jev 不會「記得」某張牌的效果，相關卡牌的完整文字要跟著局面一起給。

**要驗證的話**（照 [`AGENTS.md`](../AGENTS.md) 的最小驗證流程）：從實際對局挑 10 到 20 個有明確好壞答案的決策點；由引擎或人列出合法動作並寫清楚每個動作的結果；比較 Jev 的選擇與信心跟正確答案差多少。最值得做的是**同一批決策點跑兩種條件**——只給原始局面，以及程式先算好事實——直接量出西洋棋那個「事實比模型重要」的效應在 TCG 上有多大。

## 限制

- 全部是第三方自述，我們沒有重跑。
- 樣本都很小：撲克求解器對照只有一個翻牌、30 個局面；300 手撲克的標準誤比結果本身還大；西洋棋 30 個局面。
- 棋類、撲克跟 TCG 不是同一種遊戲：TCG 同時有隱藏資訊、每張牌不同的規則文字、以及連鎖效果，現有證據只能類推，不能直接套用。

## 標籤

💭（我們的綜合判斷；引用的事實在正文個別標 📚）

---

# Jev for strategy games and trading card games (TCGs): evidence so far and design principles (English)

Compiled 2026-09-22

## What this analysis says

**There is no public test of Jev on a trading card game (TCG) yet.** The closest evidence comes from chess and poker, and both say the same thing: **what decides the outcome isn't the model, it's how many facts you compute for it beforehand.** Given only the raw board, Jev plays chess no better than random; with code computing each move's consequences first, it reaches about 950 Elo. In poker, a simple rule that only compares equity against pot odds beat Jev. For a TCG: anything code can compute — legal actions, each action's result, damage, lethal, resources — should be computed and put in the `state`, leaving Jev only to choose among those facts; multi-turn planning and reading the opponent's hidden information shouldn't be handed to it alone.

## What this is built on

We searched in English and Chinese (2026-09-22) and found no Jev + TCG project or discussion. The closest third-party tests are below; all are self-reported and not re-run by us:

- Chess: [wondertwins/jev-benchmark](https://github.com/wondertwins/jev-benchmark)
- Poker: [backnotprop, "Jev is the fish at the poker table"](https://backnotprop.com/blog/jev-poker/) (2026-09-17), [dperezcabrera/jev-poker](https://github.com/dperezcabrera/jev-poker)
- Pokémon Red: [valentynkit/jev-plays-pokemon-red](https://github.com/valentynkit/jev-plays-pokemon-red)
- Other game projects (tic-tac-toe and Connect Four comparisons, StarCraft, Doom, 2048) and variants that read game frames directly: the Game & Simulation category of [awesome-jev](https://github.com/yibie/awesome-jev) and [`jev-variants.en.md`](../jev-variants.en.md)
- This repo's core test (can the answer be read from what you give it?): [`README.en.md`](../README.en.md)

## Analysis

### Chess: facts matter more than the model 📚

wondertwins/jev-benchmark uses 30 middlegame positions and 25 mate-in-one puzzles with Stockfish 19 as ground truth; code handles legality, board state and scoring, and Jev only picks among 20 to 40 legal moves. In the author's words: "No better than random from a raw board. Beats random by ~65% with code-supplied facts and ~78% with one-ply tactical facts. Finds mate-in-one 24% of the time. With tactical facts it plays at roughly 950 Elo on a Stockfish-anchored ladder: checkmates every bot up to ~650, loses to depth-1 Stockfish (~1166)."

The "code-supplied facts" are what python-chess computes first: both sides' pieces, material, which pieces are attacked and whether they're defended, and for every legal move whether the moved piece can be captured afterwards. The "one-ply tactical facts" add the net material of the capture sequence, whether a move gives or allows mate, and what it newly threatens — all one ply, no search. The author describes Jev's job shrinking from "read this grid of letters and play chess" to "given that this bishop will hang, which move is sensible?" The same repo found that yes/no questions asked over an ASCII board ("is White in check?") landed only a little above always guessing the majority answer — **it can't read board geometry; code has to compute it**. Speed: 0.2 s median even with 40 options; about 2,100 input tokens per move.

### Poker: a simple arithmetic rule beat Jev 📚

**Against a solver** (backnotprop): the author solved one flop with TexasSolver (heads-up, 100bb deep, 0.59% exploitability) and tried five phrasings over 30 spots: "Across 30 random spots it matched the solver's top action 63% of the time." Easy spots were fine ("Jev calls at 94%, the solver calls at 96%."), but holding the nuts in a check-or-shove spot, "Jev shoved in sixteen runs out of sixteen," while the solver checks 100% of the time — because "you hold the nuts, so shoving four times the pot gets called by nothing you beat, and folds out every hand that would have paid you."

**300 real hands** (jev-poker, six seats: 2 Jev, 2 rule bots that only compare equity against pot odds, 2 random): big blinds won per 100 hands — rule bots +134.8, Jev +29.6 (standard error 57.6; the author: "is not a profit"), random −164.4. Jev folds too much: "against a bet of ten big blinds or more it folds 83% of the time, with 38% equity on average when it does." Cost isn't the issue: 941 decisions at 268 ms each for $0.040 in total.

### Pokémon Red: ask only at branches 📚

valentynkit/jev-plays-pokemon-red gives the route and all arithmetic to code, calls Jev only where the game actually branches, and only lets it pick among actions the code has proved legal. Each battle turn's "will this faint the opponent?" prediction is scored by Brier against the game's memory — but the author deliberately hasn't published calibration yet, because the longest run on the free tier is only 5 turns.

### What every game project does 📚

1. The game engine owns the rules and lists every legal action.
2. Each legal action is one option of a Choice (up to 255 options per question), so an illegal move is structurally impossible.
3. Ideally each option says what happens if it's chosen, e.g. the resulting board.
4. Code owns arithmetic and rules; Jev only chooses at branches.

### Applying this to TCGs 💭

By this repo's core test — can the answer be read directly from what you give it? — TCG decisions split like this:

**Suitable for Jev** (the facts can all be computed and put in `state`):
- Picking one of the legal actions the engine lists, each with its result attached
- Mulligan or keep: hand, the deck's game plan, and the likely opposing archetypes written in
- Choosing targets and what to attack
- "Is this lethal?": with damage computed by code and written in, so Jev reads a result instead of doing the arithmetic

**Not for Jev alone** (chess and poker have both shown it failing):
- Multi-turn planning and sequencing
- Inferring the opponent's hand from hidden information, reading bluffs
- Combat arithmetic and resolving chained effects

Those need search in code, or low-confidence decisions escalated to a large model or a person — PlayJev, a variant that reads game frames, hands low-confidence steps to a search program (see [`jev-variants.en.md`](../jev-variants.en.md)).

**Card text belongs in the `state`**: the biggest difference from board games is that every card carries its own rules text. By the core test, Jev won't "remember" what a card does; the full text of the relevant cards has to come along with the game state.

**To verify** (following the minimal verification flow in [`AGENTS.en.md`](../AGENTS.en.md)): pick 10 to 20 decision points with clear right answers from real games; have the engine or a person list the legal actions with each one's result; compare Jev's choices and confidence against the right answers. Most worth doing is **running the same decision points under two conditions** — raw game state only, and code-computed facts — to measure directly how large chess's "facts matter more than the model" effect is in a TCG.

## Limitations

- All of it is self-reported by third parties; we haven't re-run any of it.
- Every sample is small: the solver comparison is one flop and 30 spots; the 300-hand poker test has a standard error larger than the result; chess is 30 positions.
- Chess and poker aren't TCGs: a TCG combines hidden information, per-card rules text and chained effects, so the existing evidence can only be carried over by analogy, not applied directly.

## Tag

💭 (our synthesis; the facts it cites are tagged 📚 in the body)
