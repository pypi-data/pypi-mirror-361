#!/usr/bin/env python3


import sys
import subprocess
import re
import time
import argparse
import requests

# ─── Регэкспы ──────────────────────────────────────────────────────────────────
_RE_IP      = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
_RE_SCHEME  = re.compile(r"^https?://", re.I)
_RE_RTT     = re.compile(r"time[=<]([0-9.]+)\s*ms", re.I)   # time=12.5 ms  / time<1 ms

# ─── Вспомогательные функции ──────────────────────────────────────────────────
def strip_scheme(host: str) -> str:
    """Удаляем http/https из начала строки."""
    return _RE_SCHEME.sub("", host)

def is_ip(host: str) -> bool:
    """True, если строка выглядит как IPv4-адрес."""
    return bool(_RE_IP.match(strip_scheme(host)))

# ─── ICMP-пинг (через системную утилиту ping) ────────────────────────────────
def icmp_ping(host: str, timeout: int = 1) -> float | None:
    """RTT в мс или None, если хост не ответил."""
    host = strip_scheme(host)
    if sys.platform.startswith("win"):                     # Windows
        cmd = ["ping", "-n", "1", "-w", str(timeout * 1000), host]
    elif sys.platform.startswith("linux"):                 # Linux
        cmd = ["ping", "-c", "1", "-W", str(timeout), host]
    else:                                                  # macOS / *BSD
        cmd = ["ping", "-c", "1", host]                    # без -W
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None
    match = _RE_RTT.search(res.stdout)
    return float(match.group(1)) if match else None

# ─── HTTP-пинг ────────────────────────────────────────────────────────────────
def http_ping(target: str, timeout: float = 1.0) -> float | None:
    url = target if target.startswith(("http://", "https://")) else "https://" + target
    try:
        t0 = time.time()
        requests.get(url, timeout=timeout)
        return (time.time() - t0) * 1000
    except requests.RequestException:
        return None

# ─── Форматирование эмодзи-вывода ────────────────────────────────────────────
def emoji_latency(ms: float | None) -> str:
    if ms is None:
        return "🔴 No response"
    if ms < 100:
        return f"🟢 Fast: {int(ms)} ms"
    if ms < 500:
        return f"🟡 Medium: {int(ms)} ms"
    return f"🔴 Slow: {int(ms)} ms"

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cping",
        description="Ping host/IP with emoji latency (ICMP by default, HTTP via --http)",
    )
    parser.add_argument("target", help="hostname or IPv4 address")
    parser.add_argument("--http", action="store_true", help="use HTTP latency instead of ICMP")
    args = parser.parse_args()

    latency = http_ping(args.target) if args.http else icmp_ping(args.target)
    print(emoji_latency(latency))
    sys.exit(0 if latency is not None else 1)

if __name__ == "__main__":
    main()
