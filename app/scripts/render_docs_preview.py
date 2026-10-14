"""Render the repository's documentation preview image from its static layout spec."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "docs" / "images" / "insight-query-console.png"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "msyhbd.ttc" if bold else "msyh.ttc"
    return ImageFont.truetype(f"C:/Windows/Fonts/{name}", size)


def label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: str):
    draw.rounded_rectangle((xy[0], xy[1], xy[0] + len(text) * 22 + 28, xy[1] + 34), 3, fill="#dcebdd")
    draw.text((xy[0] + 12, xy[1] + 7), text, font=font(16), fill=fill)


def main() -> None:
    image = Image.new("RGB", (1440, 900), "#f7f1e8")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, 310, 900), fill="#efe6d8", outline="#d4cbc0")
    draw.rectangle((26, 30, 68, 72), fill="#20201d")
    draw.text((39, 38), "▥", font=font(22, True), fill="#fffaf1")
    draw.text((82, 32), "企业经营智能问数", font=font(20, True), fill="#20201d")
    draw.text((82, 57), "enterprise operations", font=font(12), fill="#77736c")
    draw.line((22, 97, 288, 97), fill="#d4cbc0")
    draw.rectangle((24, 122, 286, 170), fill="#20201d")
    draw.text((96, 136), "+  新会话", font=font(16, True), fill="#fffaf1")
    draw.text((28, 208), "CONTINUOUS ANALYSIS STATE", font=font(11, True), fill="#7d786f")
    draw.rectangle((24, 230, 286, 435), fill="#fffdf9", outline="#d4cbc0")
    rows = [("指标", ["收入", "客户数"]), ("时间", ["本月"]), ("维度", ["区域"]), ("筛选", ["华东"])]
    y = 252
    for row, values in rows:
        draw.text((42, y), row, font=font(14), fill="#77736c")
        x = 95
        for value in values:
            label(draw, (x, y - 4), value, "#2f6b4f")
            x += len(value) * 22 + 36
        y += 44
    draw.text((28, 485), "RETRIEVAL PIPELINE", font=font(11, True), fill="#7d786f")
    draw.multiline_text((28, 510), "Dense + Reranker\nValue retrieval\nSchema dependency expansion", font=font(14), fill="#77736c", spacing=12)
    draw.line((310, 84, 1440, 84), fill="#d4cbc0")
    draw.text((382, 25), "企业经营智能问数 Agent", font=font(18, True), fill="#20201d")
    draw.text((382, 52), "Hybrid retrieval · Stateful analytics", font=font(13), fill="#77736c")
    draw.text((1275, 38), "●  就绪", font=font(14), fill="#2f6b4f")
    draw.rounded_rectangle((382, 157, 647, 191), 3, fill="#dcebdd", outline="#b7d1b9")
    draw.text((397, 164), "✦  Stateful semantic analytics", font=font(14, True), fill="#2f6b4f")
    draw.text((382, 225), "让每一次追问，", font=font(49, True), fill="#20201d")
    draw.text((382, 290), "都延续正确的分析上下文。", font=font(49, True), fill="#20201d")
    draw.multiline_text((382, 380), "将业务自然语言映射为可靠的 SQL：自动融合指标、时间、维度与筛选条件，\n并用混合检索和 Schema 依赖扩展降低语义偏差。", font=font(17), fill="#706d66", spacing=10)
    cards = [("⌁", "Dense + Reranker", "Cross-Encoder 精排，\n动态选择召回范围。"), ("◫", "连续上下文", "会话状态持续维护指标\n和过滤条件。"), ("⌘", "SQL 闭环", "生成、校验、修正、执行\n全程可观测。")]
    x = 382
    for icon, title, desc in cards:
        draw.rectangle((x, 500, x + 280, 650), fill="#fffdf9", outline="#d4cbc0")
        draw.text((x + 22, 522), icon, font=font(24), fill="#9a6f2d")
        draw.text((x + 22, 570), title, font=font(16, True), fill="#20201d")
        draw.multiline_text((x + 22, 600), desc, font=font(13), fill="#77736c", spacing=7)
        x += 300
    draw.rectangle((382, 700, 1282, 758), fill="#fffaf1", outline="#c9c0b4")
    draw.text((405, 719), "例如：统计本月各区域收入，并仅查看华东…", font=font(15), fill="#77736c")
    draw.rectangle((1190, 712, 1260, 746), fill="#2f6b4f")
    draw.text((1205, 719), "发送 ↑", font=font(13, True), fill="#ffffff")
    draw.text((382, 785), "FastAPI SSE · LangGraph · Qdrant · Elasticsearch", font=font(12), fill="#8b867e")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, "PNG", optimize=True)


if __name__ == "__main__":
    main()
