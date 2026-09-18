#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""共用的 Jev API 存取樣板。每個 suite 不用自己重寫 key 讀取邏輯。

Shared TypeSafe/Jev API access helper. Every suite should import this instead
of re-implementing key loading.

存取順序 / lookup order:
  1. 環境變數 TYPESAFE_API_KEY(此处是主要路徑——貢獻者不會有我們自己的私人保管庫)
     env var TYPESAFE_API_KEY (the primary path for external contributors)
  2. 專案本地 .env.local(gitignored,方便本地開發)
     a local, gitignored .env.local file, for local dev convenience

不支援任何特定保管庫機制(那是每個人自己環境的事)。
This does not support any specific secret-vault mechanism — that's each
contributor's own environment's business.
"""
import os
import sys


def load_key() -> str | None:
    key = os.environ.get("TYPESAFE_API_KEY")
    if key:
        return key
    env_local = os.path.join(os.getcwd(), ".env.local")
    if os.path.isfile(env_local):
        for line in open(env_local, encoding="utf-8"):
            line = line.strip()
            if line.startswith("TYPESAFE_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def get_client(timeout: float = 60.0):
    """回傳一個已設定好 key 的 TypeSafeClient;拿不到 key 就直接退出、說清楚為什麼。
    Returns a configured TypeSafeClient; exits clearly if no key is found."""
    key = load_key()
    if not key:
        print(
            "✗ TYPESAFE_API_KEY 未設定。請先執行: export TYPESAFE_API_KEY=<your key>\n"
            "✗ TYPESAFE_API_KEY not set. Run: export TYPESAFE_API_KEY=<your key>",
            file=sys.stderr,
        )
        sys.exit(1)
    from typesafe_sdk import TypeSafeClient
    return TypeSafeClient(api_key=key, timeout=timeout)


if __name__ == "__main__":
    # 自檢:確認服務活著,不花錢(用錯的 key 故意碰 401)
    # Self-check: confirm the service is live, at zero real cost (deliberately
    # trigger a 401 with a bad key rather than a real call).
    from typesafe_sdk import TypeSafeClient, TypeSafeAuthenticationError

    c = TypeSafeClient(api_key="selfcheck-invalid-key", timeout=15.0)
    try:
        c.system_one(state="ping", model="jev-latest",
                     questions={"x": __import__("typesafe_sdk").Noul(instructions="ping?")})
        print("⚠ 預期外的成功——你的錯 key 竟然通過了?")
    except TypeSafeAuthenticationError as e:
        print(f"✓ 服務活著,行為與文件一致(預期的 401): {e}")
    except Exception as e:
        print(f"✗ 連線層本身出問題(不是預期的 401): {type(e).__name__}: {e}")
        sys.exit(1)
