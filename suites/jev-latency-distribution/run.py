#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""量測真實呼叫的延遲分布（中位數 vs 尾端），不是測準確率。
Measures the real latency distribution of live calls (median vs tail),
not accuracy. Each state is short and simple by design, to isolate
network/inference latency from task-difficulty confounds -- following
the same "simple task" framing as the huangserva article this suite
cross-checks (see translations/jev-benchmark-article-huangserva-zh/).
"""
import sys, os, json, time, datetime

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "scripts", "common"))
from jev_client import get_client  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    from typesafe_sdk import Noul

    client = get_client()
    cases = json.load(open(os.path.join(HERE, "data", "cases.json"), encoding="utf-8"))
    Q = {"is_tech": Noul(instructions="Is this text primarily about technology or software?")}

    def timed_call(state):
        t0 = time.perf_counter()
        resp = client.system_one(state=state, model="jev-latest", questions=Q)
        return resp, (time.perf_counter() - t0) * 1000

    # 第一次呼叫要付 TLS 握手與連線建立的錢，那不是推論延遲。
    # 它照樣被計時並記進 run 檔（丟掉的東西要看得見），但不進統計。
    # The first call pays for the TLS handshake and connection setup, which is not
    # inference latency. It is still timed and recorded in the run file -- what was
    # discarded should be visible -- but it is excluded from the statistics.
    _, warmup_ms = timed_call(cases[0]["state"])
    print(f"warm-up (excluded from stats): {warmup_ms:6.1f} ms\n")

    results = []
    for c in cases:
        resp, elapsed_ms = timed_call(c["state"])
        ans = resp.answers["is_tech"]
        row = {
            "id": c["id"],
            "elapsed_ms": round(elapsed_ms, 1),
            "noul": ans.noul,
            "usage": {"input_tokens": resp.usage.input_tokens, "output_tokens": resp.usage.output_tokens},
        }
        results.append(row)
        print(f"{c['id']}: {elapsed_ms:6.1f} ms  p={ans.noul:.2f}")

    latencies = sorted(r["elapsed_ms"] for r in results)
    n = len(latencies)
    median = latencies[n // 2] if n % 2 else (latencies[n // 2 - 1] + latencies[n // 2]) / 2
    # p95 用的是排序後的最近秩（不內插）。n=30 時，第 95 百分位落在第 29 個樣本上，
    # 也就是「只比最大值小一名」——在這種樣本數下，它是尾端的指示，不是穩定的估計。
    # p95 here is the nearest rank on the sorted sample, with no interpolation. At n=30
    # that lands on the 29th sample -- one rank below the maximum -- so read it as an
    # indication of the tail, not a stable estimate.
    p95_idx = min(n - 1, int(round(0.95 * (n - 1))))
    stats = {
        "n": n,
        "min_ms": latencies[0],
        "median_ms": median,
        "p95_ms": latencies[p95_idx],
        "max_ms": latencies[-1],
        "p95_method": f"nearest rank, no interpolation (index {p95_idx} of {n} sorted samples)",
        "warmup_ms": round(warmup_ms, 1),
        "warmup_excluded": True,
    }
    print(f"\nn={n}  min={stats['min_ms']:.1f}ms  median={stats['median_ms']:.1f}ms  "
          f"p95={stats['p95_ms']:.1f}ms  max={stats['max_ms']:.1f}ms")
    print(f"p95 method: {stats['p95_method']}; warm-up call excluded ({stats['warmup_ms']} ms)")

    out_path = os.path.join(HERE, "runs", f"{datetime.date.today().isoformat()}.json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    json.dump({"suite": "jev-latency-distribution", "model": "jev-latest", "stats": stats, "results": results},
              open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"✓ saved: {out_path}")


if __name__ == "__main__":
    main()
