#!/usr/bin/env python3
"""拉取行情并重算大盘估值面板的数据，写到 static/data/valuation.json。

由 .github/workflows/update-valuation.yml 每个交易日收盘后跑一次。
只用标准库，Action 里不需要装依赖。

数据：
  SPX / NDX / VIX    Yahoo chart 接口（10 年日线）
  10Y 美债           Yahoo ^TNX，失败时退回 FRED DGS10
  CNN 恐惧贪婪       production.dataviz.cnn.io（需要 UA + Referer）
  TTM PE             没有稳定的免费接口，沿用 JSON 里的值（财报季手动改）

方法：对窗口内日收盘取对数做 OLS，偏离 = 最后一天收盘 / 趋势值 - 1；
分位 = 窗口内偏离 <= 当前偏离的交易日占比。VIX 分位同理。
"""

from __future__ import annotations

import json
import math
import re
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "data" / "valuation.json"
UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
WINDOWS = (1, 3, 5, 10)
DEFAULT_PE = 26.12
DEFAULT_PE_ASOF = "2026-10-16"
DEFAULT_GROWTH = 0.10


def fetch(url: str, headers: dict[str, str] | None = None, tries: int = 3) -> bytes:
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(headers or {})
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers=h)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except Exception as exc:  # noqa: BLE001 - 网络错误统一重试后抛出
            last = exc
            if i < tries - 1:
                time.sleep(2 * (i + 1))
    raise RuntimeError(f"fetch failed: {url}: {last}")


def yahoo_history(symbol: str) -> list[tuple[date, float]]:
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{urllib.parse.quote(symbol, safe='')}?range=10y&interval=1d&includePrePost=false"
    )
    data = json.loads(fetch(url))
    result = data["chart"]["result"][0]
    stamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    pairs = [
        (datetime.fromtimestamp(t, tz=timezone.utc).date(), float(c))
        for t, c in zip(stamps, closes)
        if c is not None
    ]
    if len(pairs) < 250:
        raise RuntimeError(f"{symbol}: not enough history ({len(pairs)})")
    return pairs


def window_slice(pairs: list[tuple[date, float]], years: int) -> list[tuple[date, float]]:
    cutoff = pairs[-1][0] - timedelta(days=round(365.25 * years))
    return [(d, c) for d, c in pairs if d >= cutoff]


def trend_stats(pairs: list[tuple[date, float]], years: int) -> dict:
    window = window_slice(pairs, years)
    n = len(window)
    if n < 200:
        raise RuntimeError(f"window {years}y has only {n} points")
    xs = list(range(n))
    ys = [math.log(c) for _, c in window]
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    slope = sxy / sxx
    intercept = my - slope * mx
    deviations = [math.exp(y - (intercept + slope * x)) - 1 for x, y in zip(xs, ys)]
    current = deviations[-1]
    pct = 100 * sum(1 for d in deviations if d <= current + 1e-12) / n
    return {
        "price": round(window[-1][1], 2),
        "deviation": round(current * 100, 1),
        "percentile": round(pct),
    }


def vix_stats(pairs: list[tuple[date, float]], years: int) -> dict:
    window = window_slice(pairs, years)
    values = [c for _, c in window]
    current = values[-1]
    pct = 100 * sum(1 for v in values if v <= current) / len(values)
    return {"value": round(current, 2), "percentile": round(pct)}


def ten_year() -> tuple[float, str]:
    pairs = yahoo_history("^TNX")
    d, v = pairs[-1]
    return round(v, 2), d.isoformat()


def ten_year_fred() -> tuple[float, str]:
    text = fetch("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10").decode()
    rows = [line.split(",") for line in text.strip().splitlines()[1:]]
    rows = [(d, float(v)) for d, v in rows if v not in ("", ".")]
    d, v = rows[-1]
    return round(v, 2), d


def ttm_pe() -> float:
    """multpl.com 的 S&P 500 TTM PE，页面 meta 里有当日值。"""
    html = fetch("https://www.multpl.com/s-p-500-pe-ratio/table/by-month").decode(
        "utf-8", "ignore"
    )
    m = re.search(r"Current S&P 500 PE Ratio is ([\d.]+)", html)
    if not m:
        raise RuntimeError("multpl: current PE not found")
    return float(m.group(1))


def fear_greed() -> dict:
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    data = json.loads(
        fetch(url, headers={"Referer": "https://www.cnn.com/", "Accept": "application/json"})
    )
    fg = data["fear_and_greed"]
    return {
        "fearGreed": round(float(fg["score"])),
        "rating": fg.get("rating", ""),
        "asOf": str(fg.get("timestamp", ""))[:10],
        "source": "CNN",
    }


def previous() -> dict:
    if not OUT.exists():
        return {}
    try:
        return json.loads(OUT.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def main() -> None:
    prev = previous()
    pv = prev.get("valuation", {})

    spx = yahoo_history("^GSPC")
    ndx = yahoo_history("^NDX")
    vix = yahoo_history("^VIX")

    try:
        yield10, yield_asof = ten_year()
    except Exception as exc:  # noqa: BLE001
        print(f"^TNX failed ({exc}); falling back to FRED")
        yield10, yield_asof = ten_year_fred()

    try:
        pe = ttm_pe()
        pe_asof = spx[-1][0].isoformat()
        pe_source = "multpl.com"
    except Exception as exc:  # noqa: BLE001
        pe = pv.get("ttmPE", DEFAULT_PE)
        pe_asof = pv.get("ttmPEAsOf", DEFAULT_PE_ASOF)
        pe_source = pv.get("ttmPESource", "快照")
        print(f"multpl PE failed ({exc}); keeping {pe} from {pe_asof}")

    windows = {}
    for years in WINDOWS:
        windows[str(years)] = {
            "spx": trend_stats(spx, years),
            "ndx": trend_stats(ndx, years),
            "vix": vix_stats(vix, years),
        }

    payload = {
        "asOf": spx[-1][0].isoformat(),
        "close": "美股收盘",
        "generatedAt": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "valuation": {
            "ttmPE": pe,
            "ttmPEAsOf": pe_asof,
            "ttmPESource": pe_source,
            "forwardEpsGrowth": pv.get("forwardEpsGrowth", DEFAULT_GROWTH),
            "tenYearYield": yield10,
            "tenYearAsOf": yield_asof,
        },
        "sentiment": fear_greed(),
        "windows": windows,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {OUT}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
