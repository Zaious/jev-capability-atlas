"""三種語言的 token 成本：tokens = a + b x 字元數，b 就是每個字元要幾個 token。
全部從既有收據 + 本地重建的 cases 算，不打 API。"""
import importlib.util
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m


def fit(pairs):
    """最小平方擬合 y = a + b x。"""
    n = len(pairs)
    sx = sum(x for x, _ in pairs)
    sy = sum(y for _, y in pairs)
    sxx = sum(x * x for x, _ in pairs)
    sxy = sum(x * y for x, y in pairs)
    b = (n * sxy - sx * sy) / (n * sxx - sx * sx)
    a = (sy - b * sx) / n
    return a, b


def report(label, pairs):
    a, b = fit(pairs)
    chars = sum(x for x, _ in pairs) / len(pairs)
    toks = sum(y for _, y in pairs) / len(pairs)
    print(f"{label:26s} n={len(pairs):4d}  平均 {chars:5.1f} 字 / {toks:6.1f} tokens  "
          f"每字 {b:5.3f} tokens  固定開銷 {a:6.1f}")


# --- 英文 / 繁中：expression-selection，單句那兩臂 ---
sel = load("sel_bc", os.path.join(ROOT, "expression-selection", "data", "build_cases.py"))
sel_sets = sel.build()
sel_run = json.load(open(os.path.join(ROOT, "expression-selection", "runs", "2026-09-23.json"),
                         encoding="utf-8"))
meld_len = {c["id"]: len(c["speaker"]) + len(c["line"]) for c in sel_sets["meld"]}
zh_len = {c["id"]: len(c["line"]) for c in sel_sets["zh"]}
en_pairs, zh_pairs = [], []
for r in sel_run["results"]:
    if "input_tokens" not in r:
        continue
    if r["arm"] == "meld_no_context" and r["repeat"] == 0:
        en_pairs.append((meld_len[r["id"]], r["input_tokens"]))
    elif r["arm"] == "zh_single" and r["repeat"] == 0:
        zh_pairs.append((zh_len[r["id"]], r["input_tokens"]))

# --- 日文：expression-japanese ---
ja = load("ja_bc", os.path.join(ROOT, "expression-japanese", "data", "build_cases.py"))
ja_len = {c["id"]: len(c["text"]) for c in ja.build()}
ja_run = json.load(open(os.path.join(ROOT, "expression-japanese", "runs", "2026-09-23.json"),
                        encoding="utf-8"))
ja_pairs = [(ja_len[r["id"]], r["input_tokens"]) for r in ja_run["results"]
            if r.get("repeat") == 0 and "input_tokens" in r]

print("注意：三組的固定開銷不同（選項數與說明長度不同），要看的是「每字 tokens」這一欄。\n")
report("英文（MELD 單句）", en_pairs)
report("繁中（單句）", zh_pairs)
report("日文（WRIME 貼文）", ja_pairs)
print()
_, be = fit(en_pairs)
_, bz = fit(zh_pairs)
_, bj = fit(ja_pairs)
print(f"每字 token 相對英文：繁中 {bz / be:.2f}x，日文 {bj / be:.2f}x")
print(f"日文相對繁中：{bj / bz:.2f}x")
