import csv
import json
import os
from pathlib import Path
from urllib import request

import matplotlib.pyplot as plt


TS_CODE = "000001.SZ"
START_DATE = "20250628"
END_DATE = "20260628"
FIELDS = "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"


def fetch_daily_data(token: str):
    payload = {
        "api_name": "daily",
        "token": token,
        "params": {
            "ts_code": TS_CODE,
            "start_date": START_DATE,
            "end_date": END_DATE,
        },
        "fields": FIELDS,
    }
    body = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        "https://api.tushare.pro",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=30) as response:
        result = json.loads(response.read().decode("utf-8"))
    if result.get("code") != 0:
        raise RuntimeError(f"Tushare error: {result.get('msg')}")
    fields = result["data"]["fields"]
    rows = [dict(zip(fields, item)) for item in result["data"]["items"]]
    return sorted(rows, key=lambda row: row["trade_date"])


def save_csv(rows, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDS.split(","))
        writer.writeheader()
        writer.writerows(rows)


def plot_close_price(rows, output_path: Path):
    dates = [row["trade_date"] for row in rows]
    closes = [float(row["close"]) for row in rows]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.rcParams["font.sans-serif"] = ["SimSun", "Microsoft YaHei", "Arial Unicode MS"]
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=160)
    ax.plot(dates, closes, color="#2d6cdf", linewidth=1.8)
    ax.set_title("图1 平安银行（000001.SZ）过去一年每日收盘价走势")
    ax.set_xlabel("交易日期")
    ax.set_ylabel("收盘价（元）")
    ax.grid(True, linestyle="--", alpha=0.35)
    tick_step = max(1, len(dates) // 6)
    ax.set_xticks(dates[::tick_step])
    ax.set_xticklabels([date[4:6] + "-" + date[6:8] for date in dates[::tick_step]])
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)


def main():
    token = os.environ.get("TUSHARE_TOKEN")
    if not token:
        raise RuntimeError("Please set TUSHARE_TOKEN before running this script.")

    base_dir = Path(__file__).resolve().parent
    rows = fetch_daily_data(token)
    save_csv(rows, base_dir / "data" / "pingan_bank_000001_sz_daily_1y.csv")
    plot_close_price(rows, base_dir / "figures" / "pingan_bank_close_price.png")
    print(f"Saved {len(rows)} rows.")


if __name__ == "__main__":
    main()
