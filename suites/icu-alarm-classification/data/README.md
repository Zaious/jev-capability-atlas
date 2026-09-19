🇹🇼 中文｜🇬🇧 English below

`sample.csv` 只記錄我們從 [PhysioNet/CinC Challenge 2015](https://physionet.org/content/challenge-2015/1.0.0/) 訓練集（[ODC-By 授權](https://physionet.org/content/challenge-2015/view-license/1.0.0/)）抽樣的 30 筆記錄名稱、類型、真假標籤——不含原始波形，原始資料請自行從 PhysioNet 下載（`https://physionet.org/files/challenge-2015/1.0.0/training/<record>.hea` / `.mat`，免 credential）。

`cases.json` 是 `extract_features.py` 跑完的產出，state 欄位是從波形抽出來的文字特徵摘要，不是原始波形本身。

`extract_features.py` 獨立撰寫，只依賴 MIT-license 的 `wfdb`／`neurokit2`，沒有引用 `NeillWhite/icu-false-alarm-reduction`（該專案未掛授權）的程式碼——細節見 `../README.md`。

---

`sample.csv` only records the record names, types, and true/false labels of the 30 records we sampled from the [PhysioNet/CinC Challenge 2015](https://physionet.org/content/challenge-2015/1.0.0/) training set ([ODC-By license](https://physionet.org/content/challenge-2015/view-license/1.0.0/)) — it does not include the raw waveforms; download those yourself from PhysioNet (`https://physionet.org/files/challenge-2015/1.0.0/training/<record>.hea` / `.mat`, no credentialing required).

`cases.json` is the output of running `extract_features.py` — its `state` field is a text feature summary derived from the waveform, not the raw waveform itself.

`extract_features.py` was written independently, depending only on MIT-licensed `wfdb`/`neurokit2` -- no code was reused from `NeillWhite/icu-false-alarm-reduction` (which carries no license). Details in `../README.md`.
