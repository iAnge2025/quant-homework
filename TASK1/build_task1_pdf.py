import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


TASK_DIR = Path(__file__).resolve().parent
DATA_PATH = TASK_DIR / "data" / "pingan_bank_000001_sz_daily_1y.csv"
FIG_PATH = TASK_DIR / "figures" / "pingan_bank_close_price.png"
PDF_PATH = TASK_DIR / "罗威TASK1.pdf"
OLD_PDF_PATH = TASK_DIR / "luow25TASK1.pdf"


def load_rows():
    with DATA_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    for row in rows:
        for key in [
            "open",
            "high",
            "low",
            "close",
            "pre_close",
            "change",
            "pct_chg",
            "vol",
            "amount",
        ]:
            row[key] = float(row[key])
    return rows


def fmt_date(value):
    return f"{value[:4]}-{value[4:6]}-{value[6:8]}"


def fmt_num(value, digits=2):
    return f"{value:.{digits}f}"


def fmt_pct(value):
    return f"{value:+.2f}%"


def compact_cn(value):
    if abs(value) >= 100000000:
        return f"{value / 100000000:.2f}亿"
    if abs(value) >= 10000:
        return f"{value / 10000:.2f}万"
    return f"{value:.2f}"


def register_fonts():
    pdfmetrics.registerFont(
        TTFont("SimSun", r"C:\Windows\Fonts\simsun.ttc", subfontIndex=0)
    )


def build_styles():
    font_size = 10.5
    leading = font_size * 1.5
    return {
        "font_size": font_size,
        "leading": leading,
        "title": ParagraphStyle(
            "title",
            fontName="SimSun",
            fontSize=15,
            leading=22.5,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "meta": ParagraphStyle(
            "meta",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_JUSTIFY,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=font_size * 2,
            wordWrap="CJK",
        ),
        "body_no_indent": ParagraphStyle(
            "body_no_indent",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_JUSTIFY,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
            wordWrap="CJK",
        ),
        "caption": ParagraphStyle(
            "caption",
            fontName="SimSun",
            fontSize=font_size,
            leading=leading,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="SimSun",
            fontSize=8.5,
            leading=11,
            alignment=TA_LEFT,
            spaceBefore=0,
            spaceAfter=0,
            firstLineIndent=0,
            wordWrap="CJK",
        ),
    }


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("SimSun", 9)
    canvas.drawCentredString(A4[0] / 2, 1.25 * cm, f"- {doc.page} -")
    canvas.restoreState()


def build_pdf():
    rows = load_rows()
    register_fonts()
    styles = build_styles()
    font_size = styles["font_size"]
    leading = styles["leading"]

    first = rows[0]
    last = rows[-1]
    period_return = (last["close"] / first["close"] - 1) * 100
    high_row = max(rows, key=lambda row: row["high"])
    low_row = min(rows, key=lambda row: row["low"])
    avg_vol = sum(row["vol"] for row in rows) / len(rows)
    avg_amount = sum(row["amount"] for row in rows) / len(rows)

    def p(text, style="body"):
        return Paragraph(text, styles[style])

    def h2(text):
        return Paragraph(text, styles["h2"])

    def h3(text):
        return Paragraph(text, styles["h3"])

    code_excerpt = '''import os, csv, json
from urllib import request
import matplotlib.pyplot as plt

payload = {
    "api_name": "daily",
    "token": os.environ["TUSHARE_TOKEN"],
    "params": {"ts_code": "000001.SZ", "start_date": "20250628", "end_date": "20260628"},
    "fields": "ts_code,trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"
}
req = request.Request("https://api.tushare.pro", data=json.dumps(payload).encode("utf-8"),
                      headers={"Content-Type": "application/json"}, method="POST")
result = json.loads(request.urlopen(req).read().decode("utf-8"))
rows = sorted([dict(zip(result["data"]["fields"], item)) for item in result["data"]["items"]],
              key=lambda row: row["trade_date"])
with open("data/pingan_bank_000001_sz_daily_1y.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=payload["fields"].split(","))
    writer.writeheader(); writer.writerows(rows)
plt.plot([r["trade_date"] for r in rows], [float(r["close"]) for r in rows])
plt.savefig("figures/pingan_bank_close_price.png")'''

    story = [
        Paragraph("量化交易与股票交易数据分析报告", styles["title"]),
        p("姓名：罗威　任务：TASK1　日期：2026年6月28日", "meta"),
        Spacer(1, leading),
        h2("一、量化交易相较于传统手工交易的优势"),
        p(
            "量化交易是指把交易思想、选股规则、择时条件和风险控制方法转化为可以被计算机执行的模型或程序。"
            "相较于传统手工交易，量化交易的主要优势体现在以下几个方面。"
        ),
        p(
            "第一，量化交易具有更强的纪律性。手工交易容易受到恐惧、贪婪、从众心理和临时判断的影响，"
            "而量化交易在模型确定后按照规则执行，可以减少情绪波动对交易结果的干扰。"
        ),
        p(
            "第二，量化交易具有更高的处理效率。计算机可以同时跟踪大量股票、指数、行业和因子数据，"
            "在短时间内完成筛选、排序、下单和风险监控，效率明显高于人工逐只查看。"
        ),
        p(
            "第三，量化交易便于历史回测和复盘。交易策略在实盘前可以使用历史数据检验收益、回撤、胜率和波动率等指标，"
            "从而提前发现策略缺陷。手工交易往往依赖经验，复盘的可重复性较弱。"
        ),
        p(
            "第四，量化交易有利于统一风险控制。程序可以预先设置仓位上限、止损条件、止盈条件、行业暴露和最大回撤约束，"
            "一旦触发规则就自动执行，避免人为犹豫导致风险扩大。"
        ),
        p(
            "第五，量化交易具有可复制、可扩展的特点。同一套策略可以应用于不同股票池或不同时间周期，"
            "也可以不断迭代参数和因子，使交易过程更加标准化。"
        ),
        h2("二、基本概念解释"),
        h3("（一）K 线"),
        p(
            "K 线是一种常见的价格图形，用一根蜡烛线表示某一交易周期内的开盘价、最高价、最低价和收盘价。"
            "实体部分表示开盘价与收盘价之间的区间，上影线表示最高价与实体上端之间的距离，"
            "下影线表示最低价与实体下端之间的距离。若收盘价高于开盘价，通常说明该周期买方力量较强；"
            "若收盘价低于开盘价，则说明卖方力量较强。实际分析时，不应只看单根 K 线，而要结合多根 K 线的形态、位置和成交量进行判断。"
        ),
        h3("（二）基本面"),
        p(
            "基本面分析关注公司的内在价值和长期经营能力，主要研究营业收入、净利润、现金流、资产负债率、"
            "毛利率、行业竞争格局、商业模式和估值水平等内容。基本面分析回答的问题是：这家公司是否具有长期价值，"
            "以及当前价格相对于其价值是否合理。对于长期投资者而言，基本面是判断公司质量和估值安全边际的重要依据。"
        ),
        h3("（三）技术面"),
        p(
            "技术面分析主要研究价格、成交量和由此衍生出的技术指标，例如均线、MACD、RSI、支撑位和压力位等。"
            "技术面并不直接判断公司的内在价值，而是从市场交易行为中观察趋势强弱、买卖力量和可能的转折位置。"
            "技术面更适合辅助判断买卖时机、设置止损位置和控制短期交易风险。"
        ),
        h2("三、Tushare 数据获取与 Python 实现"),
        p(
            f"本部分选择沪深市场股票平安银行（股票代码：000001.SZ）作为样本，使用 Tushare Pro 的日线行情接口获取过去一年内每个交易日的"
            f"开盘价、最高价、最低价、收盘价、涨跌幅、成交量和成交额等数据。由于 2026年6月28日为周日，最近一个实际交易日为 2026年6月26日。"
            f"本次共获取 {len(rows)} 个交易日的数据，时间范围为 {fmt_date(first['trade_date'])} 至 {fmt_date(last['trade_date'])}。"
            "数据已保存为 CSV 文件：TASK1/data/pingan_bank_000001_sz_daily_1y.csv。"
        ),
    ]

    table_data = [
        [p("指标", "h3"), p("结果", "h3")],
        [p("样本股票", "body_no_indent"), p("平安银行（000001.SZ）", "body_no_indent")],
        [p("交易日数量", "body_no_indent"), p(f"{len(rows)} 个", "body_no_indent")],
        [
            p("期初收盘价", "body_no_indent"),
            p(f"{fmt_num(first['close'])} 元（{fmt_date(first['trade_date'])}）", "body_no_indent"),
        ],
        [
            p("期末收盘价", "body_no_indent"),
            p(f"{fmt_num(last['close'])} 元（{fmt_date(last['trade_date'])}）", "body_no_indent"),
        ],
        [p("区间涨跌幅", "body_no_indent"), p(fmt_pct(period_return), "body_no_indent")],
        [
            p("区间最高价", "body_no_indent"),
            p(f"{fmt_num(high_row['high'])} 元（{fmt_date(high_row['trade_date'])}）", "body_no_indent"),
        ],
        [
            p("区间最低价", "body_no_indent"),
            p(f"{fmt_num(low_row['low'])} 元（{fmt_date(low_row['trade_date'])}）", "body_no_indent"),
        ],
        [p("日均成交量", "body_no_indent"), p(f"{compact_cn(avg_vol)} 股", "body_no_indent")],
        [p("日均成交额", "body_no_indent"), p(f"{compact_cn(avg_amount)} 千元", "body_no_indent")],
    ]
    table = Table(table_data, colWidths=[4.2 * cm, 10.3 * cm], hAlign="CENTER")
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "SimSun"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("LEADING", (0, 0), (-1, -1), leading),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    story.append(table)

    story.append(
        KeepTogether(
            [
                Spacer(1, 4),
                Image(str(FIG_PATH), width=15.2 * cm, height=8.15 * cm),
                p("图1 平安银行（000001.SZ）过去一年每日收盘价走势", "caption"),
            ]
        )
    )
    story.append(
        p(
            f"从图1可以看出，平安银行在样本区间内收盘价整体呈现阶段性波动。期初收盘价为 {fmt_num(first['close'])} 元，"
            f"期末收盘价为 {fmt_num(last['close'])} 元，区间涨跌幅为 {fmt_pct(period_return)}。"
            f"曲线在 {fmt_date(high_row['trade_date'])} 附近达到区间高点 {fmt_num(high_row['high'])} 元，"
            f"在 {fmt_date(low_row['trade_date'])} 附近达到区间低点 {fmt_num(low_row['low'])} 元，说明该股票在过去一年中经历了较明显的价格起伏。"
            "后续任务若继续研究该股票，可以在本次 CSV 数据基础上进一步计算收益率、波动率、均线和成交量因子。"
        )
    )

    story.extend(
        [
            h2("四、Python 核心代码"),
            p(
                "为保护个人 Tushare key，程序中不直接写入 key，而是从环境变量 TUSHARE_TOKEN 中读取。"
                "核心实现如下，完整脚本保存在 TASK1/task1_stock_analysis.py。"
            ),
            Preformatted(code_excerpt, styles["code"], maxLineLength=96),
            h2("五、结论"),
            p(
                "通过本次任务可以看到，量化交易的核心优势在于规则化、自动化和可复盘。"
                "K 线、基本面和技术面分别从价格形态、公司价值和市场交易行为三个角度帮助投资者理解股票。"
                "借助 Tushare 与 Python，可以较方便地获取历史行情数据、保存为 CSV 文件，并绘制每日收盘价曲线，"
                "为后续因子分析、策略回测和风险管理奠定数据基础。"
            ),
        ]
    )

    if OLD_PDF_PATH.exists():
        OLD_PDF_PATH.unlink()

    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=2.45 * cm,
        rightMargin=2.35 * cm,
        topMargin=2.15 * cm,
        bottomMargin=2.0 * cm,
        title="罗威TASK1",
        author="罗威",
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return PDF_PATH


if __name__ == "__main__":
    print(build_pdf())
