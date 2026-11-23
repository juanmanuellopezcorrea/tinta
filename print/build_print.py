#!/usr/bin/env python3
"""Dossier / pitch de venta A4 — tinta. by negra."""

from pathlib import Path
import io
import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PRINT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets"
FONTS = ROOT.parent / "print" / "fonts"
PREVIEW = PRINT / "preview"
PREVIEW.mkdir(exist_ok=True)

FONT_XB = str(FONTS / "BarlowCondensed-ExtraBold.ttf")
FONT_B = str(FONTS / "BarlowCondensed-Bold.ttf")
FONT_SB = str(FONTS / "BarlowCondensed-SemiBold.ttf")
FONT_L = str(FONTS / "Lato-Regular.ttf")
FONT_LB = str(FONTS / "Lato-Bold.ttf")

BLACK = (0.055, 0.047, 0.043)
INK = (0.10, 0.09, 0.08)
MUTED = (0.48, 0.44, 0.42)
MALBEC = (122 / 255, 31 / 255, 50 / 255)
MALBEC_SOFT = (0.91, 0.63, 0.68)
WHITE = (1, 1, 1)
PAPER = (0.98, 0.969, 0.949)
MIST = (0.94, 0.922, 0.890)

A4 = fitz.paper_rect("a4")
PHONE = "+34 669 691 421"
EMAIL = "jmlopezcorrea08@gmail.com"
WA = "wa.me/34669691421"


def register(page):
    page.insert_font(fontname="xb", fontfile=FONT_XB)
    page.insert_font(fontname="bc", fontfile=FONT_B)
    page.insert_font(fontname="sb", fontfile=FONT_SB)
    page.insert_font(fontname="lat", fontfile=FONT_L)
    page.insert_font(fontname="latb", fontfile=FONT_LB)


def line(page, text, x, y, font="xb", size=18, color=BLACK):
    ffile = {"xb": FONT_XB, "bc": FONT_B, "sb": FONT_SB, "lat": FONT_L, "latb": FONT_LB}[font]
    page.insert_text(fitz.Point(x, y), text, fontname="f", fontfile=ffile, fontsize=size, color=color)


def txt(page, rect, text, font="lat", size=11, color=INK, align=0):
    files = {"xb": FONT_XB, "bc": FONT_B, "sb": FONT_SB, "lat": FONT_L, "latb": FONT_LB}
    return page.insert_textbox(
        rect, text, fontname=font, fontfile=files[font],
        fontsize=size, color=color, align=align,
    )


def word_tinta(page, x, y, size=28, color=BLACK, dot=MALBEC):
    line(page, "tinta", x, y, "xb", size, color)
    w = fitz.Font(fontfile=FONT_XB).text_length("tinta", fontsize=size)
    line(page, ".", x + w * 0.98, y, "xb", size, dot)


def brand_lockup(page, x, y, word_size=22, light=False):
    word_tinta(page, x, y + word_size * 0.72, word_size, WHITE if light else BLACK, MALBEC_SOFT if light else MALBEC)
    line(
        page,
        "BY NEGRA.  ·  SOFTWARE  ·  PROCESOS  ·  BOTS",
        x,
        y + word_size + 12,
        "sb",
        8,
        (0.7, 0.7, 0.7) if light else MUTED,
    )


def cover_image(page, path, rect, dpi=180):
    """Fill rect with image cropped to cover (no stretch distortion)."""
    page.draw_rect(rect, color=BLACK, fill=BLACK, width=0)
    tw = max(1, int(rect.width * dpi / 72))
    th = max(1, int(rect.height * dpi / 72))
    im = Image.open(path).convert("RGB")
    iw, ih = im.size
    scale = max(tw / iw, th / ih)
    nw, nh = int(iw * scale), int(ih * scale)
    im = im.resize((nw, nh), Image.Resampling.LANCZOS)
    left = max(0, (nw - tw) // 2)
    top = max(0, (nh - th) // 2)
    im = im.crop((left, top, left + tw, top + th))
    buf = io.BytesIO()
    im.save(buf, format="JPEG", quality=92, optimize=True)
    page.insert_image(rect, stream=buf.getvalue(), keep_proportion=False)


def contain_image(page, path, rect, bg=BLACK):
    """Fit image inside rect without cropping; letterbox on bg."""
    page.draw_rect(rect, color=bg, fill=bg, width=0)
    page.insert_image(rect, filename=str(path), keep_proportion=True)


def export_pages(doc, stem):
    for i, page in enumerate(doc, 1):
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
        pix.save(PREVIEW / f"{stem}-{i:02d}.png")


# ---------------------------------------------------------------------------
# PAGES
# ---------------------------------------------------------------------------

def page_cover(doc):
    page = doc.new_page(width=A4.width, height=A4.height)
    register(page)
    page.draw_rect(page.rect, color=PAPER, fill=PAPER, width=0)
    brand_lockup(page, 42, 28)

    # Portrait: bodega + tablet — contain, not stretch
    left = fitz.Rect(42, 100, 268, 520)
    contain_image(page, ASSETS / "bodega-tablet-retrato.jpg", left, bg=(0.12, 0.11, 0.10))

    # Right copy
    line(page, "PITCH DE VENTA", 290, 130, "sb", 10, MALBEC)
    line(page, "LA OPERACIÓN", 290, 175, "xb", 32, BLACK)
    line(page, "ESCRITA.", 290, 212, "xb", 32, BLACK)
    line(page, "LOS BOTS QUE", 290, 258, "xb", 32, BLACK)
    line(page, "LA EJECUTAN.", 290, 295, "xb", 32, BLACK)

    txt(
        page,
        fitz.Rect(290, 320, A4.width - 42, 430),
        "Desarrollo de software.\n"
        "Automatización de procesos.\n"
        "Ingeniería de procesos.\n"
        "Bots de tareas.\n\n"
        "Una marca de negra.",
        "lat", 12, MUTED,
    )

    # Bottom landscape band — cover crop
    band = fitz.Rect(0, 545, A4.width, A4.height - 36)
    cover_image(page, ASSETS / "vinedo-andres.jpg", band)
    shape = page.new_shape()
    shape.draw_rect(band)
    shape.finish(color=None, fill=BLACK, fill_opacity=0.42)
    shape.commit()
    line(page, "DOSSIER  ·  4 PÁGINAS", 42, A4.height - 48, "sb", 9, WHITE)


def page_oferta(doc):
    page = doc.new_page(width=A4.width, height=A4.height)
    register(page)
    page.draw_rect(page.rect, color=PAPER, fill=PAPER, width=0)
    brand_lockup(page, 42, 28)
    line(page, "QUÉ RESOLVEMOS", 42, 100, "xb", 28, BLACK)
    txt(
        page,
        fitz.Rect(42, 112, A4.width - 42, 150),
        "Cuatro capas. Se venden por fase: mapear → automatizar → software que sostiene.",
        "lat", 11, MUTED,
    )

    items = [
        ("01  SOFTWARE A MEDIDA", "Aplicaciones sobre el proceso real: captura, trazabilidad, stock, reportes e integraciones."),
        ("02  AUTOMATIZACIÓN", "Flujos que hoy viven en mail y Excel: avisos, conciliaciones, pases entre áreas, cierres."),
        ("03  INGENIERÍA DE PROCESOS", "Mapa as-is / to-be, dueños, SLAs y excepciones. Sin ingeniería, el bot replica el caos."),
        ("04  BOTS DE TAREAS", "Agentes que ejecutan: leer, cargar, disparar, conciliar, sincronizar."),
    ]
    y = 165
    for title, body in items:
        page.draw_rect(fitz.Rect(42, y, A4.width - 42, y + 78), color=MIST, fill=MIST, width=0)
        page.draw_rect(fitz.Rect(42, y, 48, y + 78), color=MALBEC, fill=MALBEC, width=0)
        line(page, title, 62, y + 26, "xb", 15, BLACK)
        txt(page, fitz.Rect(62, y + 36, A4.width - 56, y + 72), body, "lat", 11, MUTED)
        y += 90

    # Method strip with landscape image
    band = fitz.Rect(42, y + 10, A4.width - 42, A4.height - 50)
    cover_image(page, ASSETS / "bodega-tablet-equipo.jpg", band)
    shape = page.new_shape()
    shape.draw_rect(band)
    shape.finish(color=None, fill=BLACK, fill_opacity=0.55)
    shape.commit()
    line(page, "MÉTODO", 58, band.y0 + 36, "sb", 9, MALBEC_SOFT)
    line(page, "PRIMERO EL PROCESO. DESPUÉS EL BOT.", 58, band.y0 + 62, "xb", 18, WHITE)
    txt(
        page,
        fitz.Rect(58, band.y0 + 75, band.x1 - 20, band.y1 - 16),
        "El entregable no es un dashboard vacío: es una tarea que deja de hacerse a mano.",
        "lat", 11, (0.85, 0.85, 0.85),
    )


def page_equipo(doc):
    page = doc.new_page(width=A4.width, height=A4.height)
    register(page)
    page.draw_rect(page.rect, color=PAPER, fill=PAPER, width=0)
    brand_lockup(page, 42, 28)
    line(page, "EQUIPO", 42, 100, "xb", 28, BLACK)
    txt(
        page,
        fitz.Rect(42, 112, A4.width - 42, 148),
        "Campo + planta + inteligencia artificial. Dos perfiles en el diagnóstico y en la entrega.",
        "lat", 11, MUTED,
    )

    # Juan card
    page.draw_rect(fitz.Rect(42, 165, A4.width / 2 - 10, 430), color=MIST, fill=MIST, width=0)
    line(page, "FUNDADOR", 58, 195, "sb", 9, MALBEC)
    line(page, "JUAN MANUEL", 58, 230, "xb", 22, BLACK)
    line(page, "LÓPEZ CORREA", 58, 256, "xb", 22, BLACK)
    txt(
        page,
        fitz.Rect(58, 280, A4.width / 2 - 24, 420),
        "Ingeniero Agrónomo\n"
        "Ph.D. in Artificial Intelligence\n\n"
        "Software a medida, datos y automatización.\n"
        "Une criterio de campo y planta con sistemas\n"
        "inteligentes: modela el problema, diseña la\n"
        "solución y la pone a producir.",
        "lat", 11, INK,
    )

    # Pabla card
    page.draw_rect(fitz.Rect(A4.width / 2 + 10, 165, A4.width - 42, 430), color=MIST, fill=MIST, width=0)
    line(page, "INGENIERÍA DE PROCESOS", A4.width / 2 + 26, 195, "sb", 9, MALBEC)
    line(page, "PABLA TORRES", A4.width / 2 + 26, 230, "xb", 22, BLACK)
    txt(
        page,
        fitz.Rect(A4.width / 2 + 26, 280, A4.width - 56, 420),
        "Ingeniera Industrial\n"
        "Ingeniería de procesos\n\n"
        "Mapa operativo, mejora continua y SLAs.\n"
        "Ordena el as-is, define el to-be y deja el\n"
        "proceso listo para automatizar — sin perder\n"
        "el control de quien opera.",
        "lat", 11, INK,
    )

    # Bottom how we work
    line(page, "CÓMO TRABAJAMOS", 42, 475, "xb", 16, BLACK)
    steps = [
        ("01  DIAGNÓSTICO", "45–90 min. Un proceso que duele. Mapa y prioridad."),
        ("02  DISEÑO", "Ingeniería + alcance de software/bot."),
        ("03  ENTREGA", "Piloto en semanas. Una tarea menos a mano."),
    ]
    x = 42
    w = (A4.width - 84 - 20) / 3
    for i, (t, b) in enumerate(steps):
        rx = x + i * (w + 10)
        page.draw_rect(fitz.Rect(rx, 495, rx + w, A4.height - 48), color=WHITE, fill=WHITE, width=0)
        page.draw_rect(fitz.Rect(rx, 495, rx + w, A4.height - 48), color=MIST, fill=None, width=0.6)
        line(page, t, rx + 12, 520, "xb", 11, BLACK)
        txt(page, fitz.Rect(rx + 12, 530, rx + w - 12, A4.height - 58), b, "lat", 10, MUTED)


def page_cta(doc):
    page = doc.new_page(width=A4.width, height=A4.height)
    register(page)
    page.draw_rect(page.rect, color=BLACK, fill=BLACK, width=0)

    # Top landscape
    top = fitz.Rect(0, 0, A4.width, 260)
    cover_image(page, ASSETS / "vinedo-cosecha-tablet.jpg", top)
    shape = page.new_shape()
    shape.draw_rect(top)
    shape.finish(color=None, fill=BLACK, fill_opacity=0.5)
    shape.commit()

    word_tinta(page, 42, 70, 34, WHITE, MALBEC_SOFT)
    line(page, "BY NEGRA.", 42, 98, "sb", 10, MALBEC_SOFT)

    line(page, "LA TINTA DEJA RASTRO.", 42, 310, "xb", 32, WHITE)
    line(page, "EL EXCEL NO.", 42, 348, "xb", 32, WHITE)

    txt(
        page,
        fitz.Rect(42, 380, A4.width - 42, 470),
        "Diagnóstico de procesos.\n"
        "Mapa + primer bot o módulo en alcance cerrado.\n\n"
        "Juan Manuel López Correa — Ing. Agrónomo · Ph.D. AI\n"
        "Pabla Torres — Ing. Industrial · Ingeniería de procesos",
        "lat", 12, (0.82, 0.82, 0.82),
    )

    line(page, PHONE, 42, 510, "xb", 22, WHITE)
    line(page, EMAIL, 42, 540, "lat", 12, (0.72, 0.72, 0.72))
    line(page, WA, 42, 562, "lat", 12, (0.72, 0.72, 0.72))

    # Small portrait bottom-right: bodega tablet
    contain_image(
        page,
        ASSETS / "bodega-tablet-retrato.jpg",
        fitz.Rect(A4.width - 210, A4.height - 230, A4.width - 36, A4.height - 40),
        bg=(0.12, 0.1, 0.1),
    )


def build():
    doc = fitz.open()
    page_cover(doc)
    page_oferta(doc)
    page_equipo(doc)
    page_cta(doc)
    out = PRINT / "tinta-dossier-venta.pdf"
    doc.save(out)
    export_pages(doc, "dossier")
    doc.close()
    print("wrote", out)


if __name__ == "__main__":
    build()
