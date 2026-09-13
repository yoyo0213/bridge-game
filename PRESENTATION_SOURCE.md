# Bridge Game 簡報原始資料

> 目的：讓第一次接觸本專案的人，先理解玩家眼中的遊戲、目前可被 repository 證明的規則，以及 Ability Cards 設計會議真正需要決定的事項。
>
> 查核基準：2026-09-12，Git `main` / `origin/main` 指向 commit `1205089`。本文件嚴格區分「程式已實作」、「測試已驗證」、「只有規劃」與「未定」；不以傳統橋牌規則補齊空白。

## 0. 閱讀標記與證據原則

- **【已實作】**：目前 Python 程式確實具備該行為。
- **【已有測試驗證】**：除已實作外，測試明確覆蓋該行為；本次執行 `.venv/bin/python -m pytest -q` 為 **154 passed**。
- **【已確定規則但尚未實作】**：專案治理文件明確列為目標，但沒有對應程式行為。
- **【仍在討論／未定】**：repository 沒有足夠資訊，或現有元件尚未串接到能回答該問題。
- `README.md` 與 `main.py` 目前都是 0 bytes，不能作為規則來源。
- Git 只有 `main` 與 `origin/main`，沒有 tag 或其他可見分支。歷史中未發現 Ability 規則或實作；最新 commit 訊息為 `Complete phase 4 game state contract result and scoring`。

---

# 一、目前專案實際進度

## 1.1 已完成的 class / module

| 領域 | class / module | 現況 |
|---|---|---|
| 紙牌 | `Suit`, `Rank`, `Card` | 【已有測試驗證】四種花色、2 到 A、相等／hash／顯示字串 |
| 牌庫 | `Deck` | 【已有測試驗證】建立 52 張唯一標準牌、抽牌、一次發多張、洗牌 |
| 手牌 | `Hand` | 【已有測試驗證】持有、加入、移除、包含判斷 |
| 玩家 | `Player` | 【已有測試驗證】身份／名稱／位置、收牌、出牌 |
| 隊伍 | `Team` | 【已有測試驗證】兩名玩家成隊、成員包含判斷 |
| 合法出牌 | `rules.can_play_card` | 【已有測試驗證】牌須在手中、首家任意出、有首引花色必須跟牌、缺門可出任意牌 |
| 一墩 | `Trick` | 【已有測試驗證】首引、四人各出一張、王牌／無王勝負、完成後找 winner |
| 一輪 | `Round` | 【已有測試驗證】玩家依序出牌、每墩勝者領出下一墩、固定完成 13 墩、接收叫牌結果 |
| 叫牌值 | `Strain`, `Bid` | 【已有測試驗證】1–7 階、♣/♦/♥/♠/NT 的順序與比較 |
| 叫牌過程 | `Bidding` | 【已有測試驗證】輪流叫牌或 Pass、必須提高、連續 Pass 結束、保存最高叫牌者 |
| 叫牌結果 | `BiddingResult` | 【已有測試驗證】合約有無、叫牌方目標、對手目標、trump strain |
| 合約轉換 | `contract.py` | 【已有測試驗證】strain 轉為實際 trump；NT 轉為 `None` |
| 合約分隊 | `ContractAssignment` | 【已有測試驗證】最高叫牌者所在隊為 bidding team，另一隊為 opposing team，並配置目標墩數 |
| 輪結果 | `RoundResult` | 【已有測試驗證】由 13 墩 winner 計算兩隊墩數與是否達標 |
| 計分 | `BaseScoringPolicy`, `ScoringContext`, `ScoringResult` | 【已有測試驗證】逐墩 2/3/4 分的既定基礎公式，輸出兩隊本輪分數增量 |
| 全場狀態 | `GameState` | 【已有測試驗證】固定 4 人、2 隊、4 輪，追蹤目前輪次／進行中 Round／結束狀態，建立分數容器 |

## 1.2 已完成的遊戲邏輯

【已有測試驗證】

- 標準 52 張牌資料結構，以及牌庫、手牌、玩家出牌的基礎操作。
- 四人、兩隊的狀態驗證；測試採 North/South 對 East/West，程式本身只要求每人恰屬一隊，沒有強制座位命名或對家位置。
- 一墩的合法出牌、王牌與無王勝負判定。
- 一輪固定 13 墩，且一定打完 13 墩；達標不會讓 Round 提前停止。
- 叫牌從傳入順序的第一位開始，依序行動；合法 bid 必須高於當前最高 bid。
- 叫牌結果決定最高叫牌方、目標墩數及 Trump / No Trump。
- 兩隊本輪取得的 trick count、合約是否達標，以及既定逐墩計分。
- GameState 在第四輪完成時標記整場結束。

## 1.3 測試現況

共有 16 個測試檔、154 個測試通過：

| 測試檔 | 測試數 | 主題 |
|---|---:|---|
| `test_card.py` | 3 | Card |
| `test_deck.py` | 5 | Deck |
| `test_hand.py` | 4 | Hand |
| `test_player.py` | 3 | Player |
| `test_team.py` | 2 | Team |
| `test_rules.py` | 4 | 跟牌合法性 |
| `test_trick.py` | 10 | Trick 流程與勝負 |
| `test_round.py` | 15 | Round 流程、13 墩、叫牌結果整合 |
| `test_bid.py` | 6 | Bid 合法性與大小 |
| `test_bidding.py` | 12 | Bidding 行動與結束條件 |
| `test_bidding_result.py` | 9 | 目標墩數、NT、無合約結果 |
| `test_contract.py` | 8 | Trump 轉換 |
| `test_contract_assignment.py` | 8 | 合約隊伍配置 |
| `test_round_result.py` | 14 | 墩數、達標與完整性 |
| `test_scoring.py` | 18 | 各輪逐墩分值與決定點 |
| `test_game_state.py` | 14 | 四人兩隊四輪與生命週期 |

## 1.4 只有介面／架構，尚未形成完整功能

- 【已實作但未整合】`Deck.deal(count)` 能取出若干牌，但沒有「開局洗牌後平均發給四人」的 Round / Game 流程，也沒有驗證每人開輪為 13 張。
- 【已實作但未整合】`BaseScoringPolicy.calculate()` 會回傳本輪兩隊 score delta；`GameState.team_scores` 會初始化為 0，但沒有 method 把 delta 累加進去。
- 【已實作但未整合】`Bidding`、`ContractAssignment`、`RoundResult`、`Scoring`、`GameState` 都存在，但沒有一個上層 controller 串起完整遊戲。`main.py` 為空。
- 【仍在討論／未定】Round 間的發牌、首位叫牌者、第一墩 leader 如何輪替或決定。
- 【仍在討論／未定】Round Winner 的唯一判定、平分處理、累積分數、Final Winner。

## 1.5 只有規則規劃，尚未實作

根據 `AGENTS.md`：

- 【已確定方向但尚未實作】遊戲「最終」會支援 Special Ability Cards。
- 【已確定方向但尚未實作】Round results 會影響 Ability Card distribution。
- 【已確定方向但尚未實作】未來支援 multiplayer networking、room codes、browser gameplay。
- 【仍在討論／未定】Ability 的種類、效果、取得條件、使用時機、持有者、持續範圍、平衡與 UI，repository 均沒有定義。

## 1.6 現在位於哪一階段？下一階段是什麼？

- 從實際 Git 最新 commit 看，最近完成的是「phase 4：game state、contract result、scoring」。這不是 `AGENTS.md` 的 1–13 編號，兩套 phase 命名沒有正式對照。
- 從功能成熟度看：Card 到 Round、Bidding、Round Result、基礎 Scoring、四輪 GameState 已有獨立模型與測試，但尚未完成端到端整合。
- `AGENTS.md` 的原定順序把 Ability Cards 放在第 9、Game state 放在第 10；實際上 GameState 與 Scoring 已先出現，而 Ability 仍為零實作。這是進度文件落後於程式的現象。
- 【最合理但仍需人工確認】下一個產品設計階段是 Ability Cards；下一個工程階段究竟先整合 scoring/game flow，或先實作 Ability，repository 沒有明示。

---

# 二、玩家眼中的遊戲

## 2.1 一句話版本

這是一款 **四人、兩隊、固定四輪** 的橋牌啟發式 trick-taking 遊戲：玩家先用 Bidding 爭取合約並決定 Trump / No Trump，再逐墩合作取勝、累積分數；未來會加入由前輪結果影響取得的 Ability Cards，讓後續流程或規則產生變化。

## 2.2 玩家如何理解它

- **玩家與隊伍**：【已實作】4 位玩家分成 2 隊，每隊 2 人。測試以相對座位 North/South 同隊、East/West 同隊示範；正式座位／組隊規則未被程式固定。
- **一場幾輪**：【已有測試驗證】固定 4 輪。
- **每輪做什麼**：可證明的核心順序是 Bidding 結果必須在出牌開始前設定，之後進行 13 個 Tricks，再計算兩隊墩數與本輪分數。Deal 與各元件的自動串接尚未實作。
- **玩家的主要決策**：在 Bidding 選擇提高合約或 Pass；在 Trick 中選擇一張合法手牌。Ability 使用決策尚未定義。
- **Trick-taking 是什麼**：每位玩家依序出一張牌，四張形成一墩（Trick）；依首引花色、王牌與點數判出一位 winner，winner 所在隊取得該墩。
- **Bidding / Trump 的角色**：最高叫牌決定叫牌方要拿到的目標墩數，以及本輪的王牌花色或 No Trump。
- **Ability Cards 為什麼存在**：【只有專案方向】作為本作相較一般橋牌的特殊系統，而且前輪結果會影響其分配。其確切設計目的（變化性、追趕機制、策略延伸等）repository 沒有寫明，不應宣稱已定。
- **全場勝負**：【仍在討論／未定】程式可在第 4 輪後結束，但尚未把每輪分數累積，也沒有 Final Winner 判定。

## 2.3 與傳統橋牌相同與不同

以下「傳統橋牌」只用作觀念對照；本專案的正式規則仍以 repository 為準。

| 面向 | 相同／近似 | 本專案目前可證明的不同或特色 |
|---|---|---|
| 玩家 | 4 人、2 對 2 | 固定四輪的完整遊戲狀態 |
| 牌 | 四花色、2 到 A，共 52 張 | 尚未完成每輪正式 Deal 流程 |
| 出牌 | 首引、跟牌、每墩四張、winner 領出下一墩 | 目前沒有 dummy、declarer 操作 dummy 等實作 |
| 叫牌 | 1–7 階；♣ < ♦ < ♥ < ♠ < NT；後叫必須更高；支援 Pass | 沒有 Double / Redouble；只保存最高叫牌者，沒有 declarer 的「同隊最先叫出最終 strain 者」規則 |
| 合約目標 | 叫牌階數 + 6 墩 | 額外替 opposing team 建立 `7 - level` 的 target；這不是拿傳統橋牌規則補出的，而是本專案程式明定 |
| 計分 | 合約是否可達成會影響局勢 | 採逐墩 2/3/4 分，且第 1–3 輪在合約成敗已無法逆轉後，後續墩升為 3 分；不是傳統橋牌計分 |
| 特殊系統 | 無對應核心機制 | 規劃加入 Ability Cards，且前輪結果影響分配；細節未定 |

---

# 三、目前可證明的完整 Game Flow

## 3.1 流程總覽

```text
Game 建立【已實作】
→ 驗證 4 位唯一玩家、2 個唯一隊伍，每人恰屬一隊
→ team_scores 初始化為 0；Round number = 1

每一輪預期流程
→ 準備／洗牌／Deal【只有 Deck 操作；整體流程未實作】
→ Bidding【已實作為獨立元件】
   → 玩家依序 Bid 或 Pass
   → 有 bid 後連續 3 Pass：最高 bid 成為結果
   → 開始即 4 Pass：無合約【後續如何處理未定】
→ 合約配置【已實作】
   → 最高叫牌者所在隊 = bidding team
   → Bid level + 6 = bidding team target
   → 7 - Bid level = opposing team target
   → Strain 決定 Trump，或 No Trump
→ 將 BiddingResult 設入 Round【已實作】
   → 必須在任何出牌前；無合約不能設入
→ 13 Tricks【已實作】
   → Leader 出第一張，產生 lead suit
   → 其餘三人依序合法出牌
   → 判斷 winner；winner 所在隊取得該墩
   → winner 領出下一墩
   → 即使合約成敗已確定，仍打完 13 墩
→ RoundResult【已實作】
   → 統計兩隊 trick count
   → 判斷各隊是否達到自己的 target
→ ScoringResult【已實作為獨立計算】
   → 輸出兩隊本輪 score delta
→ 累積進 GameState.team_scores【尚未實作】
→ Ability distribution / draw【只有方向，所有條件未定】
→ GameState 完成 Round【已實作】
   → Round 1→2→3→4
   → 完成 Round 4 後 is_finished = True
→ Final Score / Winner【未實作／未定】
```

## 3.2 各階段的玩家、系統與後續狀態

| 階段 | 發生什麼 | 玩家做什麼 | 系統判斷 | 影響後續 |
|---|---|---|---|---|
| Game 建立 | 建立四人兩隊 | 組隊方式未定 | 人數、ID、隊伍成員唯一性 | 建立四輪生命週期與空分數表 |
| Deal | 應準備手牌 | 未定 | 只有牌庫可洗／抽／deal N 張 | 尚未串入 Round，不能宣稱正式順序 |
| Bidding | 輪流競價 | Bid 或 Pass | 輪到誰、bid 是否更高、是否結束 | 產生最高 bid 與 bidder |
| Contract | 叫牌轉為合約 | 無額外行動 | bidding team、雙方 targets、Trump/NT | 決定 Round 規則與 scoring 判定點 |
| Trick | 四人各出一張 | 選合法牌 | 跟牌是否合法、trump/lead/rank 勝負 | winner 的隊多一墩；winner 成為下一 leader |
| Round Result | 13 墩完成 | 無 | 兩隊墩數與 target 是否達成 | 提供 scoring input；理論上也將影響 Ability 分配 |
| Scoring | 逐墩計分 | 無 | 該輪、合約何時已決定、每墩 winner | 產生 score delta，但尚未累加 |
| Ability | 預定進行分配／使用 | 未定 | 未定 | 預計影響後輪，但作用方式未知 |
| Round 推進 | 進入下一輪 | 未定 | 第四輪是否完成 | 第四輪後 Game 結束 |
| Final Winner | 比較整場成果 | 無 | 未定 | 尚無可執行結果 |

---

# 四、Trick 規則

## 4.1 已確定且測試驗證的規則

1. **Lead player 是誰**：第一墩由建立 `Round` 時的 `leader_index` 指定，預設為傳入玩家順序的第 1 位。第二墩起，由上一墩 winner 領出。跨 Round 的 leader 決定方式未定。
2. **Lead suit 如何產生**：leader 在該墩出的第一張牌，其花色就是 lead suit。
3. **必須跟牌嗎**：玩家手上若有 lead suit，必須出該花色。
4. **沒有 lead suit 時**：可以出手中任意花色，包括 trump（若有）或其他非 trump 花色；repository 沒有強制將牌／超將規則。
5. **有 Trump 時的 winner**：
   - 只要有人出 trump，非 trump 不能勝過 trump。
   - 多張 trump 之間由同花色最高 rank 勝出。
   - 若無人出 trump，lead suit 中最高 rank 勝出。
   - 脫離 lead suit 且不是 trump 的牌不能贏。
6. **No Trump 時的 winner**：只看 lead suit；lead suit 中最高 rank 勝出，其他花色即使是 A 也不能贏。
7. **Rank 大小**：2 < 3 < … < 10 < J < Q < K < A。
8. **下一墩 leader**：本墩 winner。
9. **Team 如何取得 trick**：`RoundResult` 查看每墩 winner 屬於哪一隊，該隊 trick count +1。Team 本身沒有保存 trick 清單。
10. **Round 長度**：固定 13 Tricks；每墩固定四位玩家各一次，共 52 次出牌。

## 4.2 給新手的四人範例

假設 North 領出，Spades（♠）是 Trump：

| 順序 | 玩家 | 出牌 | 解讀 |
|---:|---|---|---|
| 1 | North | A♥ | 第一張，所以 lead suit = Hearts（♥） |
| 2 | East | K♥ | 有 ♥，跟牌；目前 A♥ 較大 |
| 3 | South | 2♠ | 假設手上沒有 ♥，可出 ♠；♠ 是 Trump，因此壓過 A♥ |
| 4 | West | Q♥ | 跟 ♥，但不能壓過 Trump |

結果：South 贏得此 Trick；South 所在隊取得 1 墩，而且下一墩由 South 先出。

若這一輪是 **No Trump**，同樣四張牌會由 North 的 A♥ 勝出，因為只有 lead suit ♥ 有資格比較。

## 4.3 尚未回答的 Trick 細節

- 第一輪第一墩 leader 如何由玩家規則決定，而非 constructor 預設值。
- 每輪是否一定完整發 13 張給每位玩家；實作的 Round 只依「13 墩完成」判斷。
- Ability 能否改變合法出牌、牌力、leader、winner、trump 或 trick 歸屬，全部未定。
- 相同 suit/rank 的重複 Card 在測試中可被人工加入手牌；正式 Deck 本身沒有重複牌，但 Round 未驗證牌局唯一性。

---

# 五、Bidding / Trump 規則

## 5.1 發生時間

- 【已實作的約束】`BiddingResult` 必須在 Round 尚未有任何出牌時設定；設定後會重建第一墩，讓它使用叫牌決定的 trump。
- 【未完成的編排】沒有 Game controller 自動建立 Bidding、Deal、Round，因此 Deal 與 Bidding 誰先誰後，repository 不能完整證明。

## 5.2 玩家可做的行動

- **Bid**：level 只能是 1–7；strain 為 Clubs、Diamonds、Hearts、Spades、No Trump。
- **Pass**：放棄本次行動，但程式沒有把玩家永久排除；之後輪到他時仍可 bid。
- 沒有 Double、Redouble 或 Ability action。

## 5.3 Bid 大小與 Trump

- 同 level 的順序：♣ < ♦ < ♥ < ♠ < NT。
- 高 level 的任何 strain 都高於低 level 的任何 strain。
- 新 bid 必須嚴格高於現有最高 bid。
- 最終最高 bid 的 strain 成為 Trump；若 strain 是 NT，則該輪 `trump = None`。

## 5.4 如何結束、誰有最終決定權

- 尚無任何 bid 時，四位玩家連續 Pass → Bidding 結束，結果為「無合約」。
- 已有 bid 後，連續三位玩家 Pass → Bidding 結束。
- 任何新 bid 會把連續 Pass 計數歸零。
- 最終最高 bidder 及其 bid 取得合約決定權；其所在隊成為 bidding team。
- 叫牌方 target = `level + 6`（7–13 墩）；對方 target = `7 - level`（6–0 墩）。

## 5.5 對 Round 的影響

- 決定 Trump / No Trump。
- 決定 bidding team 與 opposing team。
- 決定叫牌方是否成功所需的墩數；此目標也決定第 1–3 輪 scoring 何時進入「結果已不可逆」狀態。
- Strain 本身不改變目前的 base scoring；測試明確驗證 NT 與 suit contract 使用相同計分。

## 5.6 Ability 能否介入 Bidding？

【仍在討論／未定】repository 沒有 Ability 類別、hook、event、rule modifier，也沒有「強制敵方 Pass」規則。強制 Pass 只能列為待討論候選，不能描述成既有 Ability。

---

# 六、四輪制與勝負

## 6.1 四輪制

- 【已有測試驗證】一場固定 4 輪，合法 round number 僅 1–4。
- 【已有測試驗證】完成第 1–3 輪後 round number +1；完成第 4 輪後 `is_finished = True`，不能再 start round。
- 【仍在討論／未定】每輪是否更換 dealer、leader、首位 bidder、座位或隊伍。

## 6.2 是否達標就直接結束 Round 或 Game？

- **不會提前結束 Round**：【已有測試驗證】Round 一定完成 13 墩。
- **不會因某隊先達標直接贏得整場**：目前沒有這種程式行為；Game 只因第四輪完成而結束。
- 達標或失敗「已不可逆」只會在第 1–3 輪改變後續 tricks 的分值，不會停止出牌。

## 6.3 四個不同概念必須分開

| 概念 | 目前定義 |
|---|---|
| **Round Winner** | 【未定】`RoundResult` 只提供雙方 trick count 與各自是否達 target，沒有單一 winner 欄位。由於兩個 target 合計 13，恰好照目標分配時兩隊可同時 `met_target=True`。 |
| **Round Score** | 【已實作】`ScoringResult` 提供 bidding team 與 opposing team 的本輪 score delta。 |
| **Total / Cumulative Score** | 【只有容器】`GameState.team_scores` 初始化為 0，但 `complete_current_round()` 明確不改分數，沒有累加 API。 |
| **Final Winner** | 【未實作／未定】第四輪後只標記 finished，沒有比較分數、平手規則或 winner。 |

## 6.4 前輪如何影響後輪

- 【已確定方向但尚未實作】Round results 將影響 Ability Card distribution。
- 【尚未實作】累積分數理應跨 Round，但目前沒有把 score delta 寫回 GameState。
- 【未定】前輪輸贏、是否出完剩餘手牌、Round 1/2 選擇、Round 3 強制條件等，repository 完全沒有規則。

---

# 七、Scoring System

## 7.1 已確定且已實作的公式

計分單位是「每一墩」，每隊拿到自己贏得 tricks 的分數：

- **Round 1–3，合約成敗尚未不可逆前**：每墩 2 分。
- **Round 1–3，使合約成敗確定的那一墩**：仍是 2 分。
- **Round 1–3，確定之後剩餘的每一墩**：每墩 3 分。
- **Round 4**：不論何時確定，13 墩每墩均為 4 分。

「合約已決定」指以下任一情況：

1. bidding team 已取得至少 `level + 6` 墩，合約成功已確定；或
2. 即使 bidding team 拿下所有剩餘墩，也達不到 `level + 6`，合約失敗已確定。

重要細節：

- 判定核心只看 bidding team 的合約成功或失敗；`opposing_team_target` 本身不是 scoring transition 的觸發條件。
- 沒有因 bid level、strain 或 NT 額外加減分。
- 沒有 bonus、penalty、double/redouble、vulnerability。
- Ability modifier 尚不存在。

## 7.2 計分範例

以 1-level 合約為例，叫牌方 target = 7：

- 若叫牌方先拿 7 墩，第 7 墩仍值 2 分；第 8–13 墩各值 3 分，歸實際贏得該墩的隊。
- 若到最後一墩才確定合約成敗，全部 13 墩都各值 2 分。
- Round 4 不看決定點，全部各值 4 分，全輪固定共發出 52 分。

## 7.3 已確定的輸入因素 vs 尚未完成部分

### 目前已確定的輸入因素

- 完整 13 墩及其先後順序。
- 每一墩的 winner 與其所屬隊。
- bidding team / opposing team。
- bidding team target（間接來自 bid level）。
- 當前 round number。

### repository 沒有納入目前公式的因素

- 兩隊進入此輪前的 cumulative score。
- Ability Card 效果。
- Bid strain / No Trump 的分數差異。
- 是否超額完成、特殊獎勵或懲罰（除逐墩分本身外）。

### 尚未完成／未定

- 把本輪 delta 寫入 cumulative score。
- Round Winner 與 Final Winner 公式。
- 平手處理。
- Ability 如何修改 score，以及修改基礎分、單墩分、本輪 delta 或 total score 的哪一層。

---

# 八、Ability Card 系統

## 8.1 在整個遊戲中的定位

repository 能證明的只有兩句方向性資訊：

1. 遊戲最終會支援 **Special Ability Cards**。
2. **Round results 會影響 Ability-card distribution**。

以下問題均為【仍在討論／未定】：

- 玩家何時取得 Ability。
- 哪些 Round 結束後取得，以及 Round 4 後是否取得。
- 是個人持有或 Team 持有。
- 使用時機與每輪／每墩使用上限。
- 是否跨 Round 保存、是否跨整場有效。
- Ability 可影響 Bidding、Deal、Trick、Scoring、資訊或 GameState 的哪些部分。
- 是否公開、隱藏、可反制、可疊加。

## 8.2 使用者指定要檢查的六個方向

搜尋所有 tracked files 與可见 Git 歷史後，六類均沒有名稱、分類、介面、測試或實作；因此只能作為會議候選題目：

| 候選方向 | 核心效果 | 對象／時機／持續 | 可影響狀態 | 現況 | 尚待 balance 決策 |
|---|---|---|---|---|---|
| 1. 改變分數 | 尚未定義 | 全未定 | 可能是 trick / round / total score，但 repository 未選定 | 未實作 | 幅度、正負、何時結算、能否改寫既有分數 |
| 2. 改變遊戲規則 | 尚未定義 | 全未定 | 可能影響合法出牌、trump、winner 等，但沒有 hook | 未實作 | 範圍、優先權、衝突、失效時點 |
| 3. 隊友互通牌／資訊 | 尚未定義 | 全未定 | Hand 資訊 | 未實作 | 看全部或部分、單向或雙向、多久、是否公開使用 |
| 4. 偷看敵方牌 | 尚未定義 | 全未定 | 對手 Hand 資訊 | 未實作 | 看誰、幾張、隨機或選擇、是否通知對方 |
| 5. 所有人互通牌／資訊 | 尚未定義 | 全未定 | 全體 Hand 資訊 | 未實作 | 公開範圍、持續時間、是否破壞隱藏資訊核心 |
| 6. Bidding 強制敵方 Pass | 尚未定義 | 全未定 | Bidding 的某玩家行動 | 未實作 | 對象、使用窗口、是否可連續封鎖、是否過強、四人全 Pass 的處理 |

結論：目前不能說「已提出或確定了這六類」。它們是本次需求要求查核的方向，而 repository 對它們沒有證據。

---

# 九、「改變規則」類 Ability

## 9.1 目前已有設計

【沒有】程式中不存在 Ability、Effect、Rule Modifier、duration 或 scope 概念，也沒有事件 hook。現有規則物件直接執行固定邏輯。

因此下列作用範圍全部是【未定】：

- 單一 Trick。
- 整個 Round。
- 該 Round 剩餘 Tricks。
- 整場 Game。

## 9.2 未來必須人工決策的問題（不是既有規則）

- 效果的最小／最大 scope 可以到哪一層？
- Ability 可在哪些明確窗口使用：Bidding 前、自己行動前、出牌後、Trick 結算前、Round 結算前？
- Trick 中途使用是否允許；若已有人出牌，是否回溯？
- 多張同時有效時，依使用時間、卡片優先級或效果類型排序？
- 同效果是否疊加；上限是多少？
- 相互衝突時誰優先；是否需要禁止組合表？
- 是否存在取消、免疫、反制另一張 Ability 的卡？反制鏈多長？
- 使用與效果是否公開；隱藏效果何時揭露？
- 效果何時失效，跨 Round 時如何清理？
- 如果改變 trump、lead suit、rank 或跟牌義務，如何保持 `Trick.winner()` 與合法出牌判定一致？
- 如果改變 trick winner／歸屬，RoundResult 與 Scoring 應讀「原 winner」或「修改後 winner」？
- 第四輪 4 分固定規則能否被 Ability 改寫？

---

# 十、Ability Card 取得機制

## 10.1 repository 能確認的內容

- Round result 將影響 Ability-card distribution。
- 除此之外沒有 distribution、draw、ability deck、inventory、winner/loser allocation 或剩餘手牌條件。

## 10.2 目前忠於 repository 的 decision tree

```text
Round End
├─ 建立 RoundResult（兩隊 trick count、雙方是否達 target）【已實作】
├─ 計算兩隊本輪 score delta【已實作，但未寫入累積分數】
├─ Round result 影響 Ability distribution【只有方向】
│  ├─ 是否每輪一定抽？【未定】
│  ├─ Round 1 / 2 是否可選擇？【未定】
│  ├─ Round 3 是否必須出完剩餘手牌？【未定；目前本來就固定打完 13 墩】
│  ├─ Winner / Loser 誰抽、抽幾張、機率是否不同？【未定】
│  ├─ 「剩餘手牌是否出完」是否影響取得？【未定】
│  └─ Round 4 後是否仍抽 Ability？【未定】
└─ GameState
   ├─ Round 1–3 完成 → 下一 Round【已實作】
   └─ Round 4 完成 → Game finished【已實作】
```

特別說明：目前 Round 固定打滿 13 Tricks，所以若每位玩家確實先拿 13 張，理論上會自然出完；但正式 Deal 未串接，且「出完牌」沒有成為任何 Ability distribution condition。不能由此推導 Round 3 有特殊強制規則。

---

# 十一、最需要討論的 Ability Design Questions

以下均未被 repository 回答，適合作為會議 agenda；不在此替團隊決定。

## 11.1 產品定位

- Ability 的首要目的為何：增加變化、提供追趕、獎勵勝者、深化資訊戰，或多者並存？
- Ability 應保留多少橋牌式技巧，允許改寫哪些核心規則？
- 一場可出現多少種 Ability；每種牌有幾張？
- 是否需要類型、強度等級或稀有度？

## 11.2 取得與追趕機制

- 哪些 Round 後發牌；Round 4 後是否完全不發？
- 是固定取得、隨機抽牌、公開選牌，或從數張中擇一？
- Round result 的哪個欄位驅動分配：達標、trick 差、round score、cumulative score，或 Round Winner？
- Winner 與 Loser 各得多少、機率是否不同？
- 是否刻意提供 comeback mechanic？如何避免領先者 snowball？
- 若雙方都達 target、都未達 target，或未來 Round 平手，如何分配？
- 是否真的需要「是否出完剩餘手牌」條件；如何與固定 13 墩相容？

## 11.3 所有權與資源限制

- Ability 是個人持有還是 Team 共用？隊友可否看到？
- 可否囤積並跨 Round 保存；整場持有上限？
- 每 Round、每 Trick、每個 timing window 可用幾張？
- 使用後棄置、回牌庫、冷卻，或一次性永久移除？
- 同名卡可否重複持有或同時使用？

## 11.4 Timing、衝突與資訊

- 各類 Ability 的精確使用窗口是什麼？
- 同一 Trick 是否可疊加；效果優先權如何判定？
- 是否可以反制／取消；反制是否也可被反制？
- 使用卡片、目標與結果是否公開？
- 隱藏 Ability 如何避免線上遊戲中的資訊不同步與爭議？
- Duration 是一次行動、單 Trick、剩餘 Round、整 Round 或整場？

## 11.5 六類候選效果的具體問題

- Score modifier 合理幅度是多少；改 trick 分、round delta 還是 cumulative score？
- Rule modifier 最多能改到什麼程度；哪些核心規則不可侵犯？
- 隊友資訊共享是單向／雙向、看全部／部分、持續多久？
- 偷看敵方牌要看誰、幾張、隨機或選定，對方是否知情？
- 全員資訊公開要公開多少、多久，是否讓後續 Tricks 失去推理價值？
- 強制 Pass 是否過強；能否指定最高 bidder、連續使用、造成全員 Pass？

## 11.6 先決規則問題

這些不是 Ability 本身，但若不先確認，Ability 很難平衡：

- Round Winner 到底如何定義？
- 本輪 delta 如何正式累積，Final Winner 如何判定？
- 全員 Pass 後是重叫、重發、換 dealer，或本輪取消？
- Deal、首位 bidder、第一墩 leader 的正式順序與輪替方式？
- Ability 分配所依賴的「Round result」究竟指 trick count、met target、score，還是尚未實作的 winner？

---

# RULE_CONFLICTS

## Conflict 1：全員 Pass 結果可以產生，但 Round 不接受

- **衝突內容**：Bidding 把開局四次 Pass 視為合法結束，產生 `bid=None, bidder_id=None`；但 Round 明確拒絕沒有合約的結果，ContractAssignment 也拒絕無合約。
- **檔案 A**：`bridge_game/game/bidding.py` 與 `tests/test_bidding.py`、`tests/test_bidding_result.py` 支援 all-pass result。
- **檔案 B**：`bridge_game/game/round.py`、`bridge_game/game/contract_assignment.py` 及其測試拒絕 all-pass result。
- **implementation 現況**：叫牌可正常結束，但無法銜接成可玩的 Round。
- **人工確認**：全員 Pass 後要重發、重叫、換首位玩家、使用 No Trump 預設合約、取消本輪，還是其他處理？

## Conflict 2：開發順序把 Ability 放在 GameState 前，但實際進度相反

- **衝突內容**：`AGENTS.md` planned order 是 Round → Ability Cards → Game State；Git 已完成 GameState、Contract Result、Scoring，卻沒有 Ability。
- **檔案／Git**：`AGENTS.md` 對照 commit `1205089` 與目前 tracked files。
- **implementation 現況**：GameState 已存在並通過測試；Ability 不存在。
- **人工確認**：更新 roadmap 時，下一工程階段是先做 Ability，或先完成 GameState 與 scoring 的端到端整合？

## Conflict 3：GameState 有 team_scores，但完成 Round 不會計分

- **衝突內容**：Scoring 已能計算 score delta，GameState 也有 cumulative score 容器；然而 `complete_current_round()` 不接收或套用 ScoringResult。
- **檔案 A**：`bridge_game/game/scoring.py` 與 `tests/test_scoring.py` 定義每輪分數。
- **檔案 B**：`bridge_game/game/game_state.py` 與 `tests/test_game_state.py` 明確驗證完成一輪後分數仍為 0。
- **implementation 現況**：兩個元件各自成立，尚未整合；不是可運作的累積計分。
- **人工確認**：何時結算、由誰提交結果、是否允許 Ability 在寫入前修改、如何驗證同一 Round 不重複計分？

## Conflict 4：`AGENTS.md` 說 Round results 影響 Ability 分配，但 result 的哪個意義不明

- **衝突內容**：文件使用泛稱「Round results」，程式中的 `RoundResult` 只有兩隊墩數與各自是否達標，沒有 Round Winner 或 score；分數另由 `ScoringResult` 表達。
- **檔案 A**：`AGENTS.md`。
- **檔案 B**：`bridge_game/game/round_result.py`、`bridge_game/game/scoring.py`。
- **implementation 現況**：沒有 distribution，因此沒有採用任何一種解讀。
- **人工確認**：Ability 分配應依墩數、達標、score delta、cumulative score，還是要先新增 Round Winner？

> 其餘大量空白（例如 Round 1/2 選擇、Round 3 出完牌、Ability 六類效果）是「沒有規則」，不是互相衝突；已在相應章節標記未定。

---

# 十二、建議簡報架構（14 頁）

## Slide 1 — 這是一款什麼遊戲？

**目的：** 30 秒建立共同畫面。

**應呈現內容：** 四人、兩隊、四輪；Bidding → Trump / NT → 13 Tricks → Scoring；未來加入 Ability Cards。

**適合的圖示 / 流程圖：** 四人圍桌、兩組隊色；底部一條五段流程。

**講者需要補充什麼：** 這是 bridge-inspired，不是完整複製傳統橋牌；今天重點是 Ability 設計前的共同規則基線。

## Slide 2 — 玩家在做哪些決策？

**目的：** 從體驗而非程式切入。

**應呈現內容：** 叫多少、選哪個 strain、何時 Pass、每墩出哪張合法牌；Ability 決策尚待設計。

**適合的圖示 / 流程圖：** 玩家面前兩個決策泡泡：Bidding 與 Play Card。

**講者需要補充什麼：** 隊友合作靠共同取墩；目前沒有 dummy 規則或 Ability 資訊共享。

## Slide 3 — 與傳統橋牌：保留什麼、改變什麼？

**目的：** 用熟悉框架定位本作。

**應呈現內容：** 4 人 2 隊、52 張、叫牌、Trump、跟牌相同；固定四輪、逐墩 2/3/4 分、Ability 規劃為特色；無 Double/Redouble/dummy 實作。

**適合的圖示 / 流程圖：** 兩欄 comparison table。

**講者需要補充什麼：** 不要把傳統橋牌尚未實作的規則默認帶入。

## Slide 4 — 一場遊戲的四輪骨架

**目的：** 建立整場時間軸。

**應呈現內容：** Game Start → Round 1 → Round 2 → Round 3 → Round 4 → Game Finished；前輪結果預計影響 Ability 分配。

**適合的圖示 / 流程圖：** 四段 timeline，Round 4 用「每墩 4 分」標示權重差異。

**講者需要補充什麼：** 累積分數與 Final Winner 尚未完成，不可展示為已定公式。

## Slide 5 — 一輪怎麼玩？

**目的：** 讓聽眾掌握重複的核心 loop。

**應呈現內容：** Deal（整合未定）→ Bidding → Contract/Trump → 13 Tricks → RoundResult → Scoring → Ability distribution（未定）。

**適合的圖示 / 流程圖：** 橫向流程；用實線標已實作、虛線標未定／未整合。

**講者需要補充什麼：** 各零件已有測試，但尚無端到端 controller。

## Slide 6 — Bidding 如何決定合約？

**目的：** 說清楚 Bid、Pass、Trump、目標墩數。

**應呈現內容：** 1–7；♣ < ♦ < ♥ < ♠ < NT；新 bid 必須更高；有 bid 後 3 Pass 結束；target = level + 6。

**適合的圖示 / 流程圖：** Bid ladder，加一個 4H → Hearts Trump → 10 tricks 的例子。

**講者需要補充什麼：** all-pass 後無法開始 Round，是必須確認的規則缺口；沒有 Double/Redouble。

## Slide 7 — Trick-taking，四張牌如何決勝？

**目的：** 讓完全不懂取墩遊戲的人看懂。

**應呈現內容：** leader 出牌產生 lead suit；有該花色必跟；缺門可任意出；trump 優先；否則 lead suit 最高牌勝。

**適合的圖示 / 流程圖：** 使用 A♥、K♥、2♠、Q♥ 的四人出牌例。

**講者需要補充什麼：** winner 的隊取得一墩，且 winner 領出下一墩。

## Slide 8 — 13 墩與「合約已決定」

**目的：** 澄清達標不等於立即停止。

**應呈現內容：** Round 永遠打完 13 墩；合約成功或失敗不可逆時只改變後續計分。

**適合的圖示 / 流程圖：** 13 格 trick track，在決定點畫分界線。

**講者需要補充什麼：** 第 7 墩若是決定墩仍值 2，從下一墩才值 3。

## Slide 9 — 計分：前三輪與第四輪

**目的：** 說清楚本作最明確的差異規則。

**應呈現內容：** Round 1–3：決定前／決定墩 2 分，之後 3 分；Round 4：每墩 4 分。

**適合的圖示 / 流程圖：** 上下兩條 trick-value timeline。

**講者需要補充什麼：** strain/NT 不影響 base score；score delta 尚未累積入 GameState。

## Slide 10 — Round Result、Round Score、Total、Winner 不同

**目的：** 防止設計討論混用名詞。

**應呈現內容：** 四格：trick count / 本輪 delta / 累積分數 / Final Winner；前兩者已算得出，後兩者尚未完成。

**適合的圖示 / 流程圖：** 四層漏斗或資料流。

**講者需要補充什麼：** RoundResult 沒有唯一 Round Winner；兩隊恰好達各自 target 時可同時 met target。

## Slide 11 — Ability Cards 為什麼現在要討論？

**目的：** 從已穩定的核心規則轉入創作議題。

**應呈現內容：** 已定：會有 Special Ability Cards、Round results 影響分配。未定：取得、持有、使用、效果、持續、衝突。

**適合的圖示 / 流程圖：** 核心規則圓環外加一張空白 Ability 卡模板。

**講者需要補充什麼：** repository 目前沒有任何 Ability 實作；今天不是審既有卡表，而是建立設計規格。

## Slide 12 — 六個 Ability 候選方向

**目的：** 給討論一組可比較的設計空間。

**應呈現內容：** 改分數、改規則、隊友資訊、偷看敵手、全員資訊、強制敵方 Pass；全部標「候選／未定」。

**適合的圖示 / 流程圖：** 2×3 卡片矩陣，每張只有一句效果方向與風險標籤。

**講者需要補充什麼：** 這六類來自會議查核需求，不是 repository 已核准內容。

## Slide 13 — Ability 取得流程：已知與空白

**目的：** 聚焦 Round 結果如何轉成資源。

**應呈現內容：** Round End → RoundResult →「影響 distribution」；分支列 Winner/Loser、Round 1/2/3/4、出完牌條件，全標未定。

**適合的圖示 / 流程圖：** 本文件第 10.2 節 decision tree，以顏色區分已實作與未定。

**講者需要補充什麼：** 先決定 distribution 所讀的是 trick count、達標、score 還是 Winner。

## Slide 14 — 今天要做出的設計決策

**目的：** 直接進入 Ability workshop。

**應呈現內容：** 依序討論：(1) 目的；(2) 取得者與時點；(3) 所有權／囤積；(4) 使用窗口；(5) scope/duration；(6) 疊加／反制；(7) 六類效果數值；(8) snowball 防護。

**適合的圖示 / 流程圖：** 決策 checklist 或空白設計 canvas。

**講者需要補充什麼：** 建議先解決 Final Winner、all-pass、Round Winner 三個先決問題，否則分配與平衡缺少基準。

---

# 附錄 A：重要檔案與證據索引

- 專案方向／順序：`AGENTS.md`
- 空白入口與說明：`README.md`, `main.py`
- 紙牌：`bridge_game/cards/card.py`, `deck.py`, `hand.py`
- 玩家／隊伍：`bridge_game/players/player.py`, `team.py`
- Trick / 跟牌：`bridge_game/game/trick.py`, `rules.py`
- Round：`bridge_game/game/round.py`
- Bidding / Contract：`bid.py`, `bidding.py`, `bidding_result.py`, `contract.py`, `contract_assignment.py`
- Result / Scoring：`round_result.py`, `scoring.py`
- 四輪生命週期：`game_state.py`
- 驗證：`tests/` 下全部 16 個測試檔
- Git 里程碑：`d5a2247` Trick/Rules/Round；`3073870` Bidding/Contract；`4d48ec1` flow hardening；`1205089` GameState/ContractAssignment/RoundResult/Scoring。

# 附錄 B：簡報製作時不可越界的說法

- 不要說 Ability 六類已經確定；目前只是候選方向。
- 不要說 Winner/Loser 會各抽幾張；完全未定。
- 不要說 Round 1/2 可選、Round 3 強制出完牌；repository 無此資訊。
- 不要說已完成累積計分或 Final Winner；只有 score delta 與空的 cumulative 容器。
- 不要說 all-pass 有正式後續；目前是斷裂流程。
- 不要說 Deal 已整合；只有 Deck 的通用操作。
- 不要自動套用傳統橋牌的 dummy、declarer、Double/Redouble、vulnerability 或傳統計分。
