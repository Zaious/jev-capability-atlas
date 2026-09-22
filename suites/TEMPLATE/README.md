🇹🇼 中文｜🇬🇧 English below

# 測試組範本

複製整個 `TEMPLATE/` 資料夾，改名成你的 suite slug，填以下區塊：

## 這組測什麼

（一句話）

## 為什麼測這個

（它對應能力地圖那條軸的哪一邊？你預期會強還是弱，為什麼？）

## 方法論

（題目怎麼設計的、樣本數、誰標的答案——誠實講清楚是不是單一標註者）

## 資料來源與授權

（自己寫的題目直接說明；公開資料集寫來源連結、授權、有沒有把原文放進 repo；取自私人系統的資料寫明怎麼去識別化）

## 結果

（貼真實數字，對應 `runs/` 裡的 log 檔名；收據要存下實際送出的 state，`run.py` 要支援 `--dry-run`）

## 限制

（樣本數小、單一標註者、只測了一種語言……不要省略）

## 標籤

🔬 / 📚 / 📖 / 💭 （通常新測試組是 🔬）

---

# Suite template (English)

Copy this whole folder, rename it to your suite's slug, fill in:

## What this tests
## Why this task
(Which side of the capability-map axis? What did you expect, and why?)
## Methodology
(How items were designed, sample size, who labeled the answers — say plainly if it was a single annotator)
## Data source and license
(For original items, say so; for public datasets, the source link, license, and whether the text is committed; for data from a private system, how it was de-identified)
## Results
(Real numbers, matched to filenames in `runs/`; receipts must store the exact state sent, and `run.py` should support `--dry-run`)
## Limitations
(Small N, single annotator, one language only — don't omit these)
## Tag
🔬 / 📚 / 📖 / 💭 (a new suite is usually 🔬)
