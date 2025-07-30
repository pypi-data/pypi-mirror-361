# ppecli (py-ping-emoji)

`cping` – a cross‑platform CLI to **ping any host/IP and get an emoji latency badge**.

```bash
cping 8.8.8.8              # 🟢 Fast: 11 ms
cping google.com           # 🟢 Fast: 7 ms
cping --http google.com    # 🟡 Medium: 120 ms
```

> ICMP by default · HTTP latency with `--http` · Works on macOS, Linux, Windows

---

## 🚀 Installation

```bash
pip install ppecli
```

Creates the command **`cping`** in your PATH.

---

## 🌟 Usage

```bash
cping <host|ip> [--http]
```

| Example                    | What happens                           |
| -------------------------- | -------------------------------------- |
| `cping 8.8.8.8`            | ICMP‑ping → emoji & RTT                |
| `cping google.com`         | ICMP‑ping of resolved IP               |
| `cping https://github.com` | Same, scheme stripped automatically    |
| `cping --http example.com` | Full HTTPS request latency measurement |

Exit code is **0** on success, **1** on error — handy for CI scripts.

---

## 🛠️ Features

* **Emoji output** — 🟢 <100 ms · 🟡 100‑500 ms · 🔴 >500 ms or no reply
* **Auto‑scheme handling** — give `google.com`, `https://google.com`, or raw IP
* **Cross‑platform** — macOS, Linux, Windows (`ping` flags auto‑detected)
* **HTTP mode** — measure real web latency with TLS handshake (`--http`)
* **Tiny footprint** — stdlib + `requests` only

---

## 📦 Library API

```python
from ppecli import icmp_ping, http_ping, emoji_latency

ms = icmp_ping("8.8.8.8")
print(emoji_latency(ms))
```

---

## 📝 License

MIT — see [LICENSE](https://github.com/froas-dev/ppe-cli/tree/master) for details.

---

Made with ❤️ by [Froas](https://github.com/Froas)
