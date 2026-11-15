# -*- coding: utf-8 -*-
"""Gera uma versão PDF simples do documento da Sprint 4 do SIGOA."""
from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
import reportlab

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SIGOA_Sprint4_Qualidade_Entrega_Final.md"
OUTPUT = ROOT / "SIGOA_Sprint4_Qualidade_Entrega_Final.pdf"

FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(FONT_DIR / "VeraBd.ttf")))

INK = colors.HexColor("#243447")
NAVY = colors.HexColor("#17365D")
BLUE = colors.HexColor("#DCE8F4")
GRID = colors.HexColor("#B8C5D1")
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", fontName="Vera-Bold", fontSize=21,
                          leading=27, textColor=NAVY, spaceAfter=14))
styles.add(ParagraphStyle(name="H1Custom", fontName="Vera-Bold", fontSize=15,
                          leading=19, textColor=NAVY, spaceBefore=12, spaceAfter=7,
                          keepWithNext=True))
styles.add(ParagraphStyle(name="H2Custom", fontName="Vera-Bold", fontSize=12,
                          leading=16, textColor=NAVY, spaceBefore=9, spaceAfter=5,
                          keepWithNext=True))
styles.add(ParagraphStyle(name="H3Custom", fontName="Vera-Bold", fontSize=10.5,
                          leading=14, textColor=INK, spaceBefore=7, spaceAfter=4,
                          keepWithNext=True))
styles.add(ParagraphStyle(name="BodyCustom", fontName="Vera", fontSize=9.3,
                          leading=13.5, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="BulletCustom", parent=styles["BodyCustom"],
                          leftIndent=13, firstLineIndent=-8, spaceAfter=3))
styles.add(ParagraphStyle(name="TableCustom", fontName="Vera", fontSize=7.2,
                          leading=9.2, textColor=INK, spaceAfter=0))
styles.add(ParagraphStyle(name="TableHeadCustom", fontName="Vera-Bold", fontSize=7.2,
                          leading=9.2, textColor=NAVY, spaceAfter=0))


def markup(text):
    """Escape text and support the small Markdown subset used in this document."""
    text = escape(text.strip())
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Vera-Bold'>\1</font>", text)
    return text.replace("  ", " ")


def split_table_row(line):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def build_table(lines, page_width):
    rows = [split_table_row(line) for line in lines]
    if len(rows) > 1 and all(re.fullmatch(r":?-{3,}:?", c.replace(" ", "")) for c in rows[1]):
        rows.pop(1)
    count = max(len(row) for row in rows)
    rows = [row + [""] * (count - len(row)) for row in rows]
    data = []
    for ri, row in enumerate(rows):
        style = "TableHeadCustom" if ri == 0 else "TableCustom"
        data.append([Paragraph(markup(cell), styles[style]) for cell in row])
    widths = [page_width / count] * count
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return table


def parse_markdown(source, page_width):
    lines = source.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    first_h1 = True
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith("!["):
            match = re.search(r"\]\(([^)]+)\)", line)
            if match:
                image_path = SOURCE.parent / match.group(1)
                if image_path.exists():
                    picture = Image(str(image_path))
                    scale = min(page_width / picture.imageWidth, 120 * mm / picture.imageHeight)
                    picture.drawWidth = picture.imageWidth * scale
                    picture.drawHeight = picture.imageHeight * scale
                    story.append(picture)
                    story.append(Spacer(1, 7))
            i += 1
            continue
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(build_table(table_lines, page_width))
            story.append(Spacer(1, 6))
            continue
        if line.startswith("### "):
            story.append(Paragraph(markup(line[4:]), styles["H3Custom"]))
        elif line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), styles["H1Custom"]))
        elif line.startswith("# "):
            style = styles["TitleCustom"] if first_h1 else styles["H1Custom"]
            story.append(Paragraph(markup(line[2:]), style))
            first_h1 = False
        elif line.startswith("- "):
            story.append(Paragraph("• " + markup(line[2:]), styles["BulletCustom"]))
        elif line.startswith("---"):
            story.append(Spacer(1, 5))
        else:
            story.append(Paragraph(markup(line), styles["BodyCustom"]))
        i += 1
    return story


class FooterCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._states = []

    def showPage(self):
        self._states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        pages = len(self._states)
        for state in self._states:
            self.__dict__.update(state)
            self.saveState()
            self.setStrokeColor(GRID)
            self.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
            self.setFont("Vera", 7.5)
            self.setFillColor(colors.HexColor("#65758B"))
            self.drawString(18 * mm, 10 * mm, "SIGOA • Sprint 4 • UNEMAT • 2026")
            self.drawRightString(A4[0] - 18 * mm, 10 * mm,
                                 f"Página {self._pageNumber} de {pages}")
            self.restoreState()
            super().showPage()
        super().save()


def main():
    doc = SimpleDocTemplate(str(OUTPUT), pagesize=A4,
                            rightMargin=18 * mm, leftMargin=18 * mm,
                            topMargin=17 * mm, bottomMargin=21 * mm,
                            title="SIGOA — Sprint 4: Qualidade, Estabilização e Entrega Final",
                            author="Yuri Sardinha Milani e Emanuel Faria")
    width = A4[0] - doc.leftMargin - doc.rightMargin
    doc.build(parse_markdown(SOURCE, width), canvasmaker=FooterCanvas)
    print(OUTPUT)


if __name__ == "__main__":
    main()
