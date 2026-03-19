from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


pdfmetrics.registerFont(TTFont("DejaVu", "files/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuBold", "files/DejaVuSans-Bold.ttf"))


@dataclass(frozen=True)
class Theme:
    text: HexColor = HexColor("#0f172a")
    muted: HexColor = HexColor("#475569")
    accent: HexColor = HexColor("#2563eb")
    line: HexColor = HexColor("#e2e8f0")
    bar_bg: HexColor = HexColor("#e0f2fe")
    bar_fg: HexColor = HexColor("#2563eb")


THEME = Theme()
W, H = A4

OUT_FILE = "Oleh_Bedenok_CV.pdf"

# Layout
M = 48
GAP = 22
SIDEBAR_W = 190
CONTENT_W = W - (M * 2) - GAP - SIDEBAR_W
SIDEBAR_X = W - M - SIDEBAR_W
CONTENT_X = M
TOP = H - 48
BOTTOM = 48


def draw_hr(c: canvas.Canvas, x: float, y: float, w: float) -> None:
    c.setStrokeColor(THEME.line)
    c.setLineWidth(1)
    c.line(x, y, x + w, y)


def wrap_text(
    text: str, *, font: str, size: float, max_width: float
) -> list[str]:
    words = text.replace("\n", " ").split()
    if not words:
        return [""]

    lines: list[str] = []
    cur = words[0]
    for w in words[1:]:
        cand = f"{cur} {w}"
        if pdfmetrics.stringWidth(cand, font, size) <= max_width:
            cur = cand
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    return lines


def draw_paragraph(
    c: canvas.Canvas,
    text: str,
    *,
    x: float,
    y: float,
    w: float,
    font: str = "DejaVu",
    size: float = 10,
    color=THEME.text,
    leading: float | None = None,
) -> float:
    leading = leading or (size * 1.35)
    c.setFont(font, size)
    c.setFillColor(color)
    for line in wrap_text(text, font=font, size=size, max_width=w):
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_section_title(
    c: canvas.Canvas, title: str, *, x: float, y: float, w: float
) -> float:
    c.setFont("DejaVuBold", 11)
    c.setFillColor(THEME.accent)
    c.drawString(x, y, title.upper())
    y -= 10
    draw_hr(c, x, y, w)
    return y - 14


def draw_bullets(
    c: canvas.Canvas,
    items: Iterable[str],
    *,
    x: float,
    y: float,
    w: float,
    bullet: str = "•",
    size: float = 10,
    color=THEME.text,
) -> float:
    leading = size * 1.35
    c.setFont("DejaVu", size)
    c.setFillColor(color)
    bullet_w = pdfmetrics.stringWidth(f"{bullet} ", "DejaVu", size)

    for item in items:
        first = True
        for line in wrap_text(item, font="DejaVu", size=size, max_width=w - bullet_w):
            if first:
                c.drawString(x, y, f"{bullet} {line}")
                first = False
            else:
                c.drawString(x + bullet_w, y, line)
            y -= leading
        y -= 2

    return y


def draw_skill(
    c: canvas.Canvas,
    name: str,
    val: float,
    *,
    x: float,
    y: float,
    w: float,
) -> float:
    val = max(0.0, min(1.0, val))
    c.setFont("DejaVu", 9.5)
    c.setFillColor(THEME.text)
    c.drawString(x, y, name)
    y -= 11

    bar_h = 6
    c.setFillColor(THEME.bar_bg)
    c.roundRect(x, y, w, bar_h, 2, fill=1, stroke=0)
    c.setFillColor(THEME.bar_fg)
    c.roundRect(x, y, w * val, bar_h, 2, fill=1, stroke=0)
    return y - 14


def main() -> None:
    c = canvas.Canvas(OUT_FILE, pagesize=A4)

    # Header
    y = TOP
    c.setFillColor(THEME.text)
    c.setFont("DejaVuBold", 28)
    c.drawString(CONTENT_X, y, "Oleh Bedenok")

    c.setFont("DejaVu", 12.5)
    c.setFillColor(THEME.muted)
    c.drawRightString(W - M, y + 4, "Machine Learning Engineer")

    y -= 16
    draw_hr(c, M, y, W - (M * 2))
    y -= 18

    y = draw_paragraph(
        c,
        "Forecasting systems (GraphCast → SWAN), time series, geospatial data pipelines, "
        "GPU inference optimisation, and production APIs.",
        x=CONTENT_X,
        y=y,
        w=CONTENT_W,
        font="DejaVu",
        size=10.5,
        color=THEME.text,
    )

    # Sidebar
    sy = y + 6
    sy = draw_section_title(c, "Contact", x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_paragraph(
        c,
        "Email\noleg11228811@gmail.com",
        x=SIDEBAR_X,
        y=sy,
        w=SIDEBAR_W,
        size=9.8,
        color=THEME.text,
    )
    sy -= 4
    sy = draw_paragraph(
        c,
        "Phone\n+48 577 165 986",
        x=SIDEBAR_X,
        y=sy,
        w=SIDEBAR_W,
        size=9.8,
        color=THEME.text,
    )
    sy -= 4
    sy = draw_paragraph(
        c,
        "Location\nKowale (Gdańsk), Poland",
        x=SIDEBAR_X,
        y=sy,
        w=SIDEBAR_W,
        size=9.8,
        color=THEME.text,
    )

    sy -= 10
    sy = draw_section_title(c, "Skills", x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_skill(c, "Python / NumPy / Pandas", 0.92, x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_skill(c, "Forecasting models", 0.95, x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_skill(c, "NetCDF / xarray / GRIB", 0.90, x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_skill(c, "Docker / FastAPI / Git", 0.85, x=SIDEBAR_X, y=sy, w=SIDEBAR_W)
    sy = draw_skill(c, "GPU / CUDA", 0.75, x=SIDEBAR_X, y=sy, w=SIDEBAR_W)

    # Main content
    cy = y
    cy = draw_section_title(c, "Experience", x=CONTENT_X, y=cy, w=CONTENT_W)

    c.setFillColor(THEME.text)
    c.setFont("DejaVuBold", 11)
    c.drawString(CONTENT_X, cy, "Machine Learning Engineer — MEWO")
    c.setFont("DejaVu", 9.5)
    c.setFillColor(THEME.muted)
    c.drawRightString(CONTENT_X + CONTENT_W, cy + 1, "2025 — present")
    cy -= 14

    cy = draw_bullets(
        c,
        [
            "Operational forecast system: GraphCast → SWAN (production).",
            "ERA5 / GFS data ingestion and preprocessing pipelines.",
            "GPU inference optimisation and deployment hardening.",
            "REST API and forecast visualisation tooling.",
        ],
        x=CONTENT_X,
        y=cy,
        w=CONTENT_W,
        size=10,
        color=THEME.text,
    )

    cy -= 10
    cy = draw_section_title(c, "Projects", x=CONTENT_X, y=cy, w=CONTENT_W)
    cy = draw_bullets(
        c,
        [
            "GraphCast + SWAN operational forecasting pipeline (end-to-end).",
            "ERA5 / GFS / GEBCO data processing and dataset building.",
            "Sonar data segmentation with U-Net.",
        ],
        x=CONTENT_X,
        y=cy,
        w=CONTENT_W,
        size=10,
        color=THEME.text,
    )

    cy -= 10
    cy = draw_section_title(c, "Education", x=CONTENT_X, y=cy, w=CONTENT_W)
    cy = draw_paragraph(
        c,
        "Kyiv Telecommunications University — Computer Engineering",
        x=CONTENT_X,
        y=cy,
        w=CONTENT_W,
        size=10,
        color=THEME.text,
    )

    # Column divider
    c.setStrokeColor(THEME.line)
    c.setLineWidth(1)
    c.line(SIDEBAR_X - (GAP / 2), BOTTOM, SIDEBAR_X - (GAP / 2), TOP - 34)

    # Safety: ensure we didn't run off the page (simple guard for future edits)
    min_y = min(cy, sy)
    if min_y < BOTTOM:
        c.setFillColor(THEME.muted)
        c.setFont("DejaVu", 8.5)
        c.drawString(M, BOTTOM - 10, "Note: content exceeds one page; reduce text or add pagination.")

    c.save()
    print(f"CV generated: {OUT_FILE}")


if __name__ == "__main__":
    main()