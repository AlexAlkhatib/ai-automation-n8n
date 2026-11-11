#!/usr/bin/env python3
"""Génère la documentation à partir de scripts/content.py.

Sorties :
    * docs/GUIDE.md
    * docs/AI-Workflow-Automation-n8n-Guide.pdf
    * docs/AI-Workflow-Automation-n8n-Presentation.pptx

Usage : python3 scripts/generate_docs.py
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Preformatted,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from content import CHAPTERS, META, SLIDES

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FONT_DIR = ROOT / "scripts" / "fonts"

PDF_PATH = DOCS / "AI-Workflow-Automation-n8n-Guide.pdf"
PPTX_PATH = DOCS / "AI-Workflow-Automation-n8n-Presentation.pptx"
MD_PATH = DOCS / "GUIDE.md"

NAVY = colors.HexColor("#0D1228")
INK = colors.HexColor("#1B213A")
VIOLET = colors.HexColor("#6C5CE7")
VIOLET_SOFT = colors.HexColor("#EEEBFC")
CYAN = colors.HexColor("#00B2CC")
PINK = colors.HexColor("#E94A83")
GREEN = colors.HexColor("#20A87D")
AMBER = colors.HexColor("#E89618")
LIGHT = colors.HexColor("#F6F7FC")
MUTED = colors.HexColor("#687091")
BORDER = colors.HexColor("#DFE2F0")
WHITE = colors.white

TONE = {
    "info": (VIOLET, VIOLET_SOFT),
    "success": (GREEN, colors.HexColor("#EAF7F1")),
    "warn": (AMBER, colors.HexColor("#FDF3E3")),
    "danger": (PINK, colors.HexColor("#FDECF2")),
}

PAGE_W, PAGE_H = A4
MARGIN_X = 50
MARGIN_TOP = 76
MARGIN_BOTTOM = 54
FRAME_W = PAGE_W - 2 * MARGIN_X
FRAME_H = PAGE_H - MARGIN_TOP - MARGIN_BOTTOM


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("DejaVu", str(FONT_DIR / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(FONT_DIR / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Mono", str(FONT_DIR / "DejaVuSansMono.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Mono-Bold", str(FONT_DIR / "DejaVuSansMono-Bold.ttf")))
    pdfmetrics.registerFontFamily(
        "DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu", boldItalic="DejaVu-Bold"
    )


BODY = ParagraphStyle(
    "Body", fontName="DejaVu", fontSize=9.6, leading=15.2, textColor=INK,
    alignment=TA_JUSTIFY, spaceAfter=7,
)
LEAD = ParagraphStyle(
    "Lead", fontName="DejaVu", fontSize=12, leading=18.5, textColor=NAVY, spaceAfter=12,
)
H2 = ParagraphStyle(
    "H2", fontName="DejaVu-Bold", fontSize=12.8, leading=17, textColor=VIOLET,
    spaceBefore=12, spaceAfter=6, keepWithNext=True,
)
BULLET = ParagraphStyle(
    "Bullet", parent=BODY, leftIndent=15, bulletIndent=2, spaceAfter=4.6, alignment=TA_LEFT,
)
CHAPTER_KICKER = ParagraphStyle(
    "ChapterKicker", fontName="DejaVu-Bold", fontSize=7.6, leading=10, textColor=VIOLET,
    charSpace=1.4, spaceAfter=4,
)
CHAPTER_TITLE = ParagraphStyle(
    "ChapterTitle", fontName="DejaVu-Bold", fontSize=22, leading=27, textColor=NAVY,
    spaceAfter=16,
)
CAPTION = ParagraphStyle(
    "Caption", fontName="DejaVu", fontSize=7.8, leading=11, textColor=MUTED,
    alignment=TA_CENTER, spaceBefore=5, spaceAfter=12,
)
TABLE_HEAD = ParagraphStyle(
    "TableHead", fontName="DejaVu-Bold", fontSize=7.9, leading=10.2, textColor=WHITE,
)
TABLE_CELL = ParagraphStyle(
    "TableCell", fontName="DejaVu", fontSize=7.9, leading=10.4, textColor=INK,
)
TABLE_CELL_SMALL = ParagraphStyle(
    "TableCellSmall", fontName="DejaVu", fontSize=6.9, leading=8.9, textColor=INK,
)
CODE_STYLE = ParagraphStyle(
    "Code", fontName="DejaVu-Mono", fontSize=7.5, leading=10.4,
    textColor=colors.HexColor("#E8EBF7"),
)
TOC_HEADING = ParagraphStyle(
    "TOCHeading", fontName="DejaVu-Bold", fontSize=21, leading=26, textColor=NAVY,
    spaceAfter=14,
)
NOTE = ParagraphStyle(
    "Note", fontName="DejaVu", fontSize=8, leading=11.5, textColor=MUTED, alignment=TA_LEFT,
)
CENTER_NOTE = ParagraphStyle(
    "CenterNote", parent=NOTE, alignment=TA_CENTER, fontSize=8.6, leading=12,
)


def hexcode(color) -> str:
    """Retourne une couleur ReportLab au format #rrggbb pour les balises."""
    return color.hexval().replace("0x", "#")


def md_inline(text: str) -> str:
    """Convertit **gras** et `code` en balises ReportLab."""
    escaped = escape(str(text))
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"`(.+?)`", r'<font name="DejaVu-Mono" size="7.6">\1</font>', escaped)
    return escaped


def cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)

    canvas.setFillColor(VIOLET)
    canvas.rect(0, PAGE_H - 10, PAGE_W, 10, fill=1, stroke=0)

    for radius, alpha in ((150, 0.18), (230, 0.10), (310, 0.06)):
        canvas.setStrokeColor(VIOLET)
        canvas.setStrokeAlpha(alpha)
        canvas.setLineWidth(1.1)
        canvas.circle(PAGE_W - 55, PAGE_H - 90, radius, fill=0, stroke=1)
    canvas.setStrokeAlpha(1)

    canvas.setFillColor(CYAN)
    canvas.rect(56, PAGE_H - 92, 10, 10, fill=1, stroke=0)
    canvas.setFillColor(colors.HexColor("#9AA3C4"))
    canvas.setFont("DejaVu-Bold", 8.4)
    canvas.drawString(74, PAGE_H - 90, META["eyebrow"])

    title_style = ParagraphStyle(
        "CoverTitle", fontName="DejaVu-Bold", fontSize=37, leading=43, textColor=WHITE,
    )
    title = Paragraph(META["title"], title_style)
    _, title_h = title.wrapOn(canvas, 470, 300)
    title.drawOn(canvas, 56, PAGE_H - 240 - title_h)

    canvas.setFillColor(VIOLET)
    canvas.rect(56, PAGE_H - 262 - title_h, 92, 4, fill=1, stroke=0)

    subtitle_style = ParagraphStyle(
        "CoverSub", fontName="DejaVu", fontSize=12.5, leading=19,
        textColor=colors.HexColor("#C9CEE4"),
    )
    subtitle = Paragraph(META["subtitle"], subtitle_style)
    _, subtitle_h = subtitle.wrapOn(canvas, 420, 200)
    subtitle.drawOn(canvas, 56, PAGE_H - 320 - title_h - subtitle_h)

    stats_y = 150
    canvas.setStrokeColor(colors.HexColor("#2A3155"))
    canvas.setLineWidth(0.7)
    canvas.line(56, stats_y + 44, PAGE_W - 56, stats_y + 44)
    canvas.setFont("DejaVu-Bold", 18)
    canvas.setFillColor(WHITE)
    cursor = 56
    for item in META["stats"]:
        label = f"{item['value']} {item['label']}"
        canvas.drawString(cursor, stats_y, label)
        cursor += pdfmetrics.stringWidth(label, "DejaVu-Bold", 18) + 24
    canvas.setFont("DejaVu", 8.4)
    canvas.setFillColor(colors.HexColor("#8B93B5"))
    canvas.drawString(56, stats_y - 18,
                      "Du premier agent au système multi-agents  ·  zéro secret dans le dépôt")
    canvas.drawString(56, stats_y - 32, "16 workflows n8n prêts à importer, documentation incluse")

    canvas.setFont("DejaVu", 8.6)
    canvas.setFillColor(colors.HexColor("#A7AECB"))
    canvas.drawString(56, 68, META["author"])
    canvas.drawString(56, 54, META["date"])
    canvas.drawRightString(PAGE_W - 56, 68, f"Version {META['version']}")
    canvas.drawRightString(PAGE_W - 56, 54, f"Licence {META['license']}")
    canvas.restoreState()


class GuideDoc(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs) -> None:
        super().__init__(filename, **kwargs)
        cover_frame = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
        body_frame = Frame(MARGIN_X, MARGIN_BOTTOM, FRAME_W, FRAME_H, id="body")
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=cover),
            PageTemplate(id="Body", frames=[body_frame], onPage=self.decorate),
        ])
        self.current_chapter = ""
        self.title = META["title"]
        self.author = META["author"]
        self.subject = META["subtitle"]

    def decorate(self, canvas, doc) -> None:
        canvas.saveState()
        canvas.setStrokeColor(BORDER)
        canvas.setLineWidth(0.5)
        canvas.line(MARGIN_X, PAGE_H - 46, PAGE_W - MARGIN_X, PAGE_H - 46)
        canvas.setFont("DejaVu", 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN_X, PAGE_H - 39, "AI Workflow Automation avec n8n")
        canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 39,
                               "Guide technique · Version 2.0")
        canvas.line(MARGIN_X, 38, PAGE_W - MARGIN_X, 38)
        canvas.setFont("DejaVu", 7.2)
        canvas.drawString(MARGIN_X, 27, f"Version {META['version']} · {META['date']}")
        canvas.drawRightString(PAGE_W - MARGIN_X, 27, f"{doc.page}")
        canvas.setFillColor(VIOLET)
        canvas.setFont("DejaVu-Bold", 7.2)
        canvas.drawCentredString(PAGE_W / 2, 27, "Documentation générée automatiquement")
        canvas.restoreState()

    def afterFlowable(self, flowable) -> None:
        style = getattr(flowable, "style", None)
        if style is not None and style.name == "ChapterTitle":
            text = flowable.getPlainText()
            self.notify("TOCEntry", (0, text, self.page))
            self.current_chapter = text


def table_widths(headers: list[str], rows: list[list[str]], available: float,
                 small: bool = False, ratios: list[float] | None = None) -> list[float]:
    if ratios:
        return [available * ratio for ratio in ratios]
    weights = []
    for index in range(len(headers)):
        longest = max(len(str(row[index])) for row in rows + [headers])
        weights.append(min(max(longest, 6), 34))
    total = sum(weights)
    widths = [available * weight / total for weight in weights]
    if small:
        widths = [width * 1.0 for width in widths]
    return widths


def render_table(block: dict, available: float = FRAME_W) -> KeepTogether:
    headers = block["headers"]
    rows = block["rows"]
    small = block.get("small", False)
    cell_style = TABLE_CELL_SMALL if small else TABLE_CELL
    head_style = TABLE_HEAD if not small else ParagraphStyle(
        "TableHeadSmall", parent=TABLE_HEAD, fontSize=6.9, leading=8.9
    )

    data = [[Paragraph(md_inline(header), head_style) for header in headers]]
    for row in rows:
        data.append([Paragraph(md_inline(cell), cell_style) for cell in row])

    table = Table(
        data,
        colWidths=table_widths(headers, rows, available, small, block.get("widths")),
        repeatRows=1,
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
    ]))

    elements: list = []
    if block.get("title"):
        elements.append(Paragraph(md_inline(block["title"]), H2))
    elements.append(table)
    elements.append(Spacer(1, 10))
    return KeepTogether(elements)


def render_callout(block: dict) -> KeepTogether:
    accent, tint = TONE.get(block.get("tone", "info"), TONE["info"])
    content = (
        f'<font name="DejaVu-Bold" color="{hexcode(accent)}" size="9">'
        f'{escape(block["title"])}</font><br/>'
        f'<font name="DejaVu" size="8.8">{md_inline(block["text"])}</font>'
    )
    cell = Paragraph(content, ParagraphStyle("Callout", leading=13.4, textColor=INK))
    table = Table([[cell]], colWidths=[FRAME_W])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), tint),
        ("LINEBEFORE", (0, 0), (0, -1), 3.2, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return KeepTogether([table, Spacer(1, 12)])


def render_stats(block: dict) -> Table:
    cells = []
    for index, item in enumerate(block["items"]):
        accent = [VIOLET, CYAN, PINK, GREEN][index % 4]
        cell = [
            Paragraph(
                f'<font name="DejaVu-Bold" size="22" color="{hexcode(accent)}">{item["value"]}</font>',
                ParagraphStyle("StatValue", leading=25),
            ),
            Paragraph(
                f'<font name="DejaVu-Bold" size="7.2" color="#687091">{item["label"].upper()}</font>',
                ParagraphStyle("StatLabel", leading=11, spaceBefore=2),
            ),
            Paragraph(
                f'<font name="DejaVu" size="7.4" color="#1B213A">{item["note"]}</font>',
                ParagraphStyle("StatNote", leading=10),
            ),
        ]
        cells.append(cell)

    table = Table([cells], colWidths=[FRAME_W / len(cells)] * len(cells))
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, WHITE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return KeepTogether([table, Spacer(1, 12)])


def render_code(block: dict) -> KeepTogether:
    code = Preformatted(block["text"].strip("\n"), CODE_STYLE)
    table = Table([[code]], colWidths=[FRAME_W])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("LEFTPADDING", (0, 0), (-1, -1), 11),
        ("RIGHTPADDING", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return KeepTogether([table, Spacer(1, 11)])


def render_image(block: dict) -> KeepTogether:
    path = ROOT / block["path"]
    image = Image(str(path))
    ratio = image.imageHeight / image.imageWidth
    width = FRAME_W
    height = width * ratio
    if height > 330:
        height = 330
        width = height / ratio
    image.drawWidth = width
    image.drawHeight = height
    elements = [Spacer(1, 4), image]
    if block.get("caption"):
        elements.append(Paragraph(block["caption"], CAPTION))
    return KeepTogether(elements)


def chapter_header(chapter: dict) -> list:
    return [
        Spacer(1, 6),
        Paragraph(
            f'{"ANNEXE" if chapter["number"].isalpha() else "CHAPITRE"} '
            f'{chapter["number"]} · {chapter["kicker"]}',
            CHAPTER_KICKER,
        ),
        Paragraph(chapter["title"], CHAPTER_TITLE),
        Table([[""]], colWidths=[FRAME_W], rowHeights=[1.6],
              style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), VIOLET)])),
        Spacer(1, 16),
    ]


def build_pdf() -> None:
    register_fonts()
    DOCS.mkdir(exist_ok=True)
    doc = GuideDoc(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=MARGIN_X,
        rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title=META["title"],
        author=META["author"],
        subject=META["subtitle"],
    )

    story: list = [NextPageTemplate("Body"), Spacer(1, 1), PageBreak()]

    story += [
        Paragraph("Sommaire", TOC_HEADING),
        Paragraph(
            "Ce guide couvre l'architecture, les patrons de conception et la mise en route de la "
            "bibliothèque. Les annexes regroupent le catalogue complet et la configuration.",
            LEAD,
        ),
        Spacer(1, 10),
    ]
    toc = TableOfContents()
    toc.levelStyles = [ParagraphStyle(
        "TOC0", fontName="DejaVu", fontSize=9.6, leading=21, textColor=INK,
        rightIndent=26, firstLineIndent=0,
    )]
    toc.dotsMinLevel = 0
    story += [toc, PageBreak()]

    for chapter in CHAPTERS:
        story += chapter_header(chapter)
        for block in chapter["blocks"]:
            kind = block["type"]
            if kind == "lead":
                story.append(Paragraph(md_inline(block["text"]), LEAD))
            elif kind == "paragraph":
                story.append(Paragraph(md_inline(block["text"]), BODY))
            elif kind == "bullets":
                if block.get("title"):
                    story.append(Paragraph(block["title"], H2))
                for item in block["items"]:
                    story.append(Paragraph(md_inline(item), BULLET, bulletText="•"))
                story.append(Spacer(1, 8))
            elif kind == "numbered":
                if block.get("title"):
                    story.append(Paragraph(block["title"], H2))
                for index, item in enumerate(block["items"], start=1):
                    story.append(Paragraph(md_inline(item), BULLET, bulletText=f"{index}."))
                story.append(Spacer(1, 8))
            elif kind == "callout":
                story.append(render_callout(block))
            elif kind == "stats":
                story.append(render_stats(block))
            elif kind == "table":
                story.append(render_table(block))
            elif kind == "code":
                if block.get("title"):
                    story.append(Paragraph(block["title"], H2))
                story.append(render_code(block))
            elif kind == "image":
                story.append(render_image(block))
            else:
                raise ValueError(f"Bloc inconnu : {kind}")
        story.append(PageBreak())

    story += [
        Paragraph("Fin du guide", CHAPTER_TITLE),
        Paragraph(
            "La documentation est générée depuis un contenu unique. Pour la mettre à jour, "
            "modifiez scripts/content.py puis lancez la commande make docs.", LEAD,
        ),
        Spacer(1, 8),
        Paragraph(
            f"{META['repo']} · version {META['version']} · {META['date']} · "
            f"licence {META['license']} · {META['author']}",
            NOTE,
        ),
    ]

    doc.multiBuild(story)
    print(f"✓ docs/{PDF_PATH.name}")


# ---------------------------------------------------------------------------
# Markdown
# ---------------------------------------------------------------------------

def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |",
             "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(cell).replace("|", "\\|") for cell in row) + " |")
    return lines


def build_markdown() -> None:
    lines = [
        f"# {META['title']}",
        "",
        f"*{META['subtitle']}*",
        "",
        f"**Version {META['version']}** · {META['date']} · {META['author']} · "
        f"Licence {META['license']}",
        "",
        "> Document généré automatiquement depuis [`scripts/content.py`]"
        "(../scripts/content.py). Modifiez le contenu source puis lancez `make docs`.",
        "",
        "## Sommaire",
        "",
    ]
    for chapter in CHAPTERS:
        anchor = re.sub(r"[^a-z0-9]+", "-", chapter["title"].lower()).strip("-")
        lines.append(f"- [{chapter['number']} · {chapter['title']}](#{anchor})")

    for chapter in CHAPTERS:
        lines += ["", "---", "", f"## {chapter['number']} · {chapter['title']}", "",
                  f"*{chapter['kicker']}*", ""]
        for block in chapter["blocks"]:
            kind = block["type"]
            if kind in ("lead", "paragraph"):
                lines += [block["text"], ""]
            elif kind == "bullets":
                if block.get("title"):
                    lines += [f"### {block['title']}", ""]
                lines += [f"- {item}" for item in block["items"]] + [""]
            elif kind == "numbered":
                if block.get("title"):
                    lines += [f"### {block['title']}", ""]
                lines += [f"{index}. {item}" for index, item in enumerate(block["items"], 1)]
                lines += [""]
            elif kind == "callout":
                lines += [f"> **{block['title']}** — {block['text']}", ""]
            elif kind == "stats":
                lines += md_table(
                    ["Indicateur", "Valeur", "Précision"],
                    [[item["label"], item["value"], item["note"]] for item in block["items"]],
                )
                lines += [""]
            elif kind == "table":
                if block.get("title"):
                    lines += [f"### {block['title']}", ""]
                lines += md_table(block["headers"], block["rows"]) + [""]
            elif kind == "code":
                if block.get("title"):
                    lines += [f"### {block['title']}", ""]
                lines += ["```" + block.get("language", ""), block["text"].strip("\n"), "```", ""]
            elif kind == "image":
                relative = block["path"].removeprefix("docs/")
                lines += [f"![{block.get('caption', '')}]({relative})", "",
                          f"*{block.get('caption', '')}*", ""]

    lines += ["", "---", "",
              f"*{META['repo']} · version {META['version']} · {META['date']} · "
              f"licence {META['license']}*", ""]
    MD_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"✓ docs/{MD_PATH.name}")


# ---------------------------------------------------------------------------
# PowerPoint
# ---------------------------------------------------------------------------

def build_pptx() -> None:
    try:
        from pptx import Presentation
        from pptx.dml.color import RGBColor
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
        from pptx.util import Emu, Inches, Pt
    except ImportError:
        print("⚠ python-pptx absent : PowerPoint non généré", file=sys.stderr)
        return

    def rgb(hex_color: str) -> RGBColor:
        hex_color = hex_color.lstrip("#")
        return RGBColor(int(hex_color[0:2], 16), int(hex_color[2:4], 16),
                        int(hex_color[4:6], 16))

    C = {
        "navy": rgb("#0D1228"), "ink": rgb("#1B213A"), "violet": rgb("#6C5CE7"),
        "violet_soft": rgb("#EEEBFC"), "cyan": rgb("#00B2CC"), "pink": rgb("#E94A83"),
        "green": rgb("#20A87D"), "amber": rgb("#E89618"), "light": rgb("#F6F7FC"),
        "muted": rgb("#687091"), "border": rgb("#DFE2F0"), "white": rgb("#FFFFFF"),
        "pale": rgb("#C9CEE4"),
    }

    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank = prs.slide_layouts[6]

    def background(slide, color):
        slide.background.fill.solid()
        slide.background.fill.fore_color.rgb = color

    def textbox(slide, left, top, width, height, text, size, bold=False,
                color=C["ink"], align=PP_ALIGN.LEFT, spacing=1.05,
                font="Arial", anchor=MSO_ANCHOR.TOP):
        box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
        frame = box.text_frame
        frame.word_wrap = True
        frame.vertical_anchor = anchor
        frame.margin_left = 0
        frame.margin_right = 0
        frame.margin_top = 0
        frame.margin_bottom = 0
        paragraph = frame.paragraphs[0]
        paragraph.alignment = align
        paragraph.line_spacing = spacing
        run = paragraph.add_run()
        run.text = text
        run.font.size = Pt(size)
        run.font.bold = bold
        run.font.color.rgb = color
        run.font.name = font
        return box

    def rich_paragraph(paragraph, text, size, color, font="Arial"):
        parts = re.split(r"(\*\*.+?\*\*)", text)
        for part in parts:
            if not part:
                continue
            bold = part.startswith("**") and part.endswith("**")
            run = paragraph.add_run()
            run.text = part[2:-2] if bold else part
            run.font.size = Pt(size)
            run.font.bold = bold
            run.font.color.rgb = color
            run.font.name = font

    def footer(slide, number):
        line = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.02), Inches(11.73), Pt(0.8)
        )
        line.fill.solid()
        line.fill.fore_color.rgb = C["border"]
        line.line.fill.background()
        textbox(slide, 0.8, 7.12, 8.0, 0.3,
                "AI Workflow Automation (n8n) · Guide v2.0", 9, color=C["muted"])
        textbox(slide, 11.4, 7.12, 1.13, 0.3, str(number), 9,
                color=C["muted"], align=PP_ALIGN.RIGHT)

    def slide_header(slide, kicker, title):
        background(slide, C["white"])
        bar = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(0.62), Inches(0.09), Inches(0.52)
        )
        bar.fill.solid()
        bar.fill.fore_color.rgb = C["violet"]
        bar.line.fill.background()
        textbox(slide, 1.02, 0.58, 10, 0.3, kicker.upper(), 10.5, True, C["violet"])
        textbox(slide, 0.8, 0.98, 11.7, 0.95, title, 28, True, C["navy"])

    def add_stats(slide, stats):
        colors_list = [C["violet"], C["cyan"], C["pink"], C["green"]]
        left = 0.8
        width = 2.78
        gap = 0.2
        for index, item in enumerate(stats):
            x = left + index * (width + gap)
            card = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(2.45), Inches(width), Inches(2.5)
            )
            card.fill.solid()
            card.fill.fore_color.rgb = C["light"]
            card.line.color.rgb = C["border"]
            card.adjustments[0] = 0.08
            accent = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(x), Inches(2.45), Inches(width), Inches(0.08)
            )
            accent.fill.solid()
            accent.fill.fore_color.rgb = colors_list[index % 4]
            accent.line.fill.background()
            textbox(slide, x + 0.25, 2.78, width - 0.5, 0.9, item["value"], 44, True,
                    colors_list[index % 4])
            textbox(slide, x + 0.25, 3.75, width - 0.5, 0.4, item["label"].upper(), 11, True,
                    C["muted"])
            textbox(slide, x + 0.25, 4.15, width - 0.5, 0.6, item["note"], 10, False, C["ink"])

    def add_table(slide, headers, rows, width=11.73, left=0.8, top=1.95):
        rows_count = len(rows) + 1
        height = 0.44 * rows_count
        shape = slide.shapes.add_table(
            rows_count, len(headers), Inches(left), Inches(top), Inches(width), Inches(height)
        )
        table = shape.table
        table.first_row = True
        table.horz_banding = False
        weights = []
        for index in range(len(headers)):
            longest = max(len(str(row[index])) for row in rows + [headers])
            weights.append(min(max(longest, 6), 40))
        total = sum(weights)
        for index, weight in enumerate(weights):
            table.columns[index].width = Emu(int(Inches(width) * weight / total))
        for column, header in enumerate(headers):
            cell = table.cell(0, column)
            cell.fill.solid()
            cell.fill.fore_color.rgb = C["navy"]
            cell.margin_left = Inches(0.12)
            cell.margin_right = Inches(0.12)
            cell.margin_top = Inches(0.06)
            cell.margin_bottom = Inches(0.06)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            frame = cell.text_frame
            frame.word_wrap = True
            paragraph = frame.paragraphs[0]
            run = paragraph.add_run()
            run.text = header
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = C["white"]
            run.font.name = "Arial"
        for row_index, row in enumerate(rows, start=1):
            for column, value in enumerate(row):
                cell = table.cell(row_index, column)
                cell.fill.solid()
                cell.fill.fore_color.rgb = C["white"] if row_index % 2 else C["light"]
                cell.margin_left = Inches(0.12)
                cell.margin_right = Inches(0.12)
                cell.margin_top = Inches(0.06)
                cell.margin_bottom = Inches(0.06)
                cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                frame = cell.text_frame
                frame.word_wrap = True
                paragraph = frame.paragraphs[0]
                rich_paragraph(paragraph, str(value), 10.5, C["ink"])
        return table

    def add_picture(slide, path, top=1.8, max_height=4.55):
        from PIL import Image as PILImage

        image_path = ROOT / path
        with PILImage.open(image_path) as image:
            ratio = image.height / image.width
        width = 11.73
        height = width * ratio
        if height > max_height:
            height = max_height
            width = height / ratio
        left = (13.333 - width) / 2
        slide.shapes.add_picture(str(image_path), Inches(left), Inches(top),
                                 width=Inches(width), height=Inches(height))

    number = 0
    for spec in SLIDES:
        slide = prs.slides.add_slide(blank)
        number += 1
        kind = spec["kind"]

        if kind == "cover":
            background(slide, C["navy"])
            bar = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.85), Inches(1.45), Inches(0.1), Inches(2.2)
            )
            bar.fill.solid()
            bar.fill.fore_color.rgb = C["violet"]
            bar.line.fill.background()
            textbox(slide, 1.15, 1.4, 9, 0.35, spec["eyebrow"], 10.5, True, C["cyan"])
            textbox(slide, 1.15, 1.85, 10.4, 1.9, spec["title"], 46, True, C["white"])
            textbox(slide, 1.15, 3.85, 9.2, 1.3, spec["subtitle"], 16, False, C["pale"])
            textbox(slide, 1.15, 6.35, 9, 0.4, spec["meta"], 11, False, C["muted"])
            for index in range(4):
                square = slide.shapes.add_shape(
                    MSO_SHAPE.RECTANGLE, Inches(1.15 + index * 0.22), Inches(6.0),
                    Inches(0.12), Inches(0.12)
                )
                square.fill.solid()
                square.fill.fore_color.rgb = [C["violet"], C["cyan"], C["pink"], C["green"]][index]
                square.line.fill.background()

        elif kind == "section":
            background(slide, C["navy"])
            textbox(slide, 0.85, 1.15, 3, 1.6, spec["number"], 96, True, C["violet"])
            textbox(slide, 0.85, 3.05, 10.5, 1.0, spec["title"], 38, True, C["white"])
            textbox(slide, 0.9, 4.15, 10.0, 1.2, spec["subtitle"], 16, False, C["pale"])
            line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(6.4), Inches(2.0), Inches(0.06)
            )
            line.fill.solid()
            line.fill.fore_color.rgb = C["cyan"]
            line.line.fill.background()

        elif kind == "bullets":
            slide_header(slide, spec["kicker"], spec["title"])
            top = 2.15
            height = 4.35
            box = slide.shapes.add_textbox(Inches(0.8), Inches(top), Inches(11.7), Inches(height))
            frame = box.text_frame
            frame.word_wrap = True
            frame.margin_left = 0
            for index, item in enumerate(spec["bullets"]):
                paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
                paragraph.space_after = Pt(13)
                paragraph.line_spacing = 1.05
                bullet = paragraph.add_run()
                bullet.text = "▸  "
                bullet.font.size = Pt(17)
                bullet.font.bold = True
                bullet.font.color.rgb = C["violet"]
                bullet.font.name = "Arial"
                rich_paragraph(paragraph, item, 17, C["ink"])
            if spec.get("note"):
                note = slide.shapes.add_shape(
                    MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(6.35),
                    Inches(11.7), Inches(0.55)
                )
                note.fill.solid()
                note.fill.fore_color.rgb = C["violet_soft"]
                note.line.fill.background()
                note.adjustments[0] = 0.3
                textbox(slide, 1.05, 6.46, 11.2, 0.35, spec["note"], 11,
                        False, C["violet"])
            footer(slide, number)

        elif kind == "stats":
            slide_header(slide, spec["kicker"], spec["title"])
            add_stats(slide, spec["stats"])
            footer(slide, number)

        elif kind == "image":
            slide_header(slide, spec["kicker"], spec["title"])
            add_picture(slide, spec["image"])
            if spec.get("caption"):
                textbox(slide, 0.8, 6.55, 11.7, 0.4, spec["caption"], 10.5,
                        False, C["muted"], align=PP_ALIGN.CENTER)
            footer(slide, number)

        elif kind == "table":
            slide_header(slide, spec["kicker"], spec["title"])
            add_table(slide, spec["headers"], spec["rows"])
            footer(slide, number)

        elif kind == "code":
            slide_header(slide, spec["kicker"], spec["title"])
            panel = slide.shapes.add_shape(
                MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.95),
                Inches(11.73), Inches(3.85)
            )
            panel.fill.solid()
            panel.fill.fore_color.rgb = C["navy"]
            panel.line.fill.background()
            panel.adjustments[0] = 0.04
            box = slide.shapes.add_textbox(Inches(1.15), Inches(2.2), Inches(11.0), Inches(3.4))
            frame = box.text_frame
            frame.word_wrap = True
            frame.margin_left = 0
            for index, line in enumerate(spec["code"].split("\n")):
                paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
                paragraph.line_spacing = 1.15
                run = paragraph.add_run()
                run.text = line if line else " "
                run.font.size = Pt(13)
                run.font.name = "Consolas"
                run.font.color.rgb = C["pale"] if line.strip().startswith("#") else C["white"]
            if spec.get("note"):
                textbox(slide, 0.8, 6.2, 11.7, 0.5, spec["note"], 11.5, False, C["muted"])
            footer(slide, number)

        elif kind == "end":
            background(slide, C["navy"])
            textbox(slide, 0.9, 2.35, 11.5, 1.0, spec["title"], 44, True, C["white"])
            textbox(slide, 0.9, 3.45, 9.6, 1.0, spec["subtitle"], 17, False, C["pale"])
            line = slide.shapes.add_shape(
                MSO_SHAPE.RECTANGLE, Inches(0.9), Inches(4.55), Inches(2.2), Inches(0.06)
            )
            line.fill.solid()
            line.fill.fore_color.rgb = C["violet"]
            line.line.fill.background()
            textbox(slide, 0.9, 6.35, 11.5, 0.4, spec["meta"], 11, False, C["muted"])

    prs.save(str(PPTX_PATH))
    print(f"✓ docs/{PPTX_PATH.name}")


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    build_markdown()
    build_pdf()
    build_pptx()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
