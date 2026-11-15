# -*- coding: utf-8 -*-
"""Gera o PDF com formatação simples do Trabalho Final — Laboratório de Engenharia de Software (SIGOA)."""
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
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    Preformatted,
    HRFlowable,
)
from reportlab.pdfgen import canvas
import reportlab

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SIGOA_Trabalho_Final_Laboratorio_Engenharia_Software.md"
OUTPUT = ROOT / "SIGOA_Trabalho_Final_Laboratorio_Engenharia_Software.pdf"

FONT_DIR = Path(reportlab.__file__).resolve().parent / "fonts"
pdfmetrics.registerFont(TTFont("Vera", str(FONT_DIR / "Vera.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Bold", str(FONT_DIR / "VeraBd.ttf")))
pdfmetrics.registerFont(TTFont("Vera-Italic", str(FONT_DIR / "VeraIt.ttf")))
pdfmetrics.registerFont(TTFont("Vera-BoldItalic", str(FONT_DIR / "VeraBI.ttf")))
pdfmetrics.registerFontFamily(
    "Vera",
    normal="Vera",
    bold="Vera-Bold",
    italic="Vera-Italic",
    boldItalic="Vera-BoldItalic",
)

INK = colors.HexColor("#1E293B")
NAVY = colors.HexColor("#17365D")
SUB_NAVY = colors.HexColor("#234B7A")
BLUE_HEADER = colors.HexColor("#DCE8F4")
ROW_ALT = colors.HexColor("#F8FAFC")
GRID = colors.HexColor("#B8C5D1")
CODE_BG = colors.HexColor("#F1F5F9")

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleCustom",
        fontName="Vera-Bold",
        fontSize=17.5,
        leading=22,
        textColor=NAVY,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="H1Custom",
        fontName="Vera-Bold",
        fontSize=13.5,
        leading=17.5,
        textColor=NAVY,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="H2Custom",
        fontName="Vera-Bold",
        fontSize=11.2,
        leading=15,
        textColor=SUB_NAVY,
        spaceBefore=9,
        spaceAfter=4,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="H3Custom",
        fontName="Vera-Bold",
        fontSize=9.8,
        leading=13.5,
        textColor=INK,
        spaceBefore=7,
        spaceAfter=3.5,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCustom",
        fontName="Vera",
        fontSize=9.0,
        leading=13.2,
        textColor=INK,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletCustom",
        parent=styles["BodyCustom"],
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        name="SubBulletCustom",
        parent=styles["BodyCustom"],
        leftIndent=24,
        firstLineIndent=-10,
        spaceAfter=2.5,
    )
)
styles.add(
    ParagraphStyle(
        name="CaptionCustom",
        fontName="Vera-Italic",
        fontSize=8.0,
        leading=11,
        textColor=colors.HexColor("#475569"),
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="CodeCustom",
        fontName="Courier",
        fontSize=7.4,
        leading=10.0,
        textColor=INK,
        backColor=CODE_BG,
        borderColor=GRID,
        borderWidth=0.4,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="TableCustom",
        fontName="Vera",
        fontSize=7.4,
        leading=9.8,
        textColor=INK,
        spaceAfter=0,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeadCustom",
        fontName="Vera-Bold",
        fontSize=7.5,
        leading=9.8,
        textColor=NAVY,
        spaceAfter=0,
    )
)


def clean_symbols(text: str) -> str:
    """Substitui expressões LaTeX simples por caracteres suportados pela fonte Vera."""
    replacements = {
        r"$\rightarrow$": "->",
        r"$\leftrightarrow$": "<->",
        r"$\ge 4,0/5,0$": ">= 4,0/5,0",
        r"$\approx 0,43\text{s}$": "~0,43s",
        r"$4,25/5,0$": "4,25/5,0",
        r"$4,5/5,0$": "4,5/5,0",
        "→": "->",
        "↔": "<->",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def markup(text: str) -> str:
    """Escapa XML e converte negrito, itálico e código inline para tags ReportLab."""
    text = clean_symbols(text.strip())
    text = escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Vera-Bold'>\1</font>", text)
    return text


def split_table_row(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def compute_col_widths(rows, page_width):
    count = len(rows[0])
    weights = []
    min_widths = []
    for col in range(count):
        col_texts = [re.sub(r"[*`]", "", clean_symbols(r[col])) for r in rows]
        longest_line = max((len(t) for t in col_texts), default=5)
        longest_word = max(
            (min(len(w), 22) for t in col_texts for w in t.split()),
            default=5,
        )
        # Largura mínima para caber palavras comuns sem quebrar 1-2 letras no final
        min_w = min(page_width * 0.28, longest_word * 4.5 + 12.0)
        min_widths.append(min_w)
        weight = max(float(longest_word) * 1.4, min(float(longest_line), 75.0) ** 0.72)
        weights.append(weight)

    total_w = sum(weights) or 1.0
    widths = [(w / total_w) * page_width for w in weights]
    for i in range(count):
        if widths[i] < min_widths[i]:
            widths[i] = min_widths[i]
    scale = page_width / sum(widths)
    return [w * scale for w in widths]


def build_table(lines, page_width):
    rows = [split_table_row(line) for line in lines]
    if len(rows) > 1 and all(
        re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in rows[1]
    ):
        rows.pop(1)
    count = max(len(row) for row in rows)
    rows = [row + [""] * (count - len(row)) for row in rows]
    data = []
    for ri, row in enumerate(rows):
        style = "TableHeadCustom" if ri == 0 else "TableCustom"
        data.append([Paragraph(markup(cell), styles[style]) for cell in row])
    widths = compute_col_widths(rows, page_width)
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), BLUE_HEADER),
        ("GRID", (0, 0), (-1, -1), 0.35, GRID),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4.5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4.5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for ri in range(1, len(rows)):
        if ri % 2 == 0:
            ts.append(("BACKGROUND", (0, ri), (-1, ri), ROW_ALT))
    table.setStyle(TableStyle(ts))
    return table


def parse_markdown(source: Path, page_width: float):
    lines = source.read_text(encoding="utf-8").splitlines()
    story = []
    i = 0
    first_h1 = True
    while i < len(lines):
        raw_line = lines[i]
        line = raw_line.strip()
        if not line:
            i += 1
            continue

        # Bloco de código ```
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # pula o fechamento ```
            story.append(
                Preformatted("\n".join(code_lines), styles["CodeCustom"])
            )
            continue

        # Imagem ![legenda](arquivo)
        if line.startswith("!["):
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if match:
                caption_text, rel_path = match.group(1), match.group(2)
                image_path = SOURCE.parent / rel_path
                if image_path.exists():
                    picture = Image(str(image_path))
                    scale = min(
                        page_width / picture.imageWidth,
                        115 * mm / picture.imageHeight,
                    )
                    picture.drawWidth = picture.imageWidth * scale
                    picture.drawHeight = picture.imageHeight * scale
                    picture.hAlign = "CENTER"
                    story.append(Spacer(1, 4))
                    story.append(picture)
                    if caption_text:
                        story.append(
                            Paragraph(markup(caption_text), styles["CaptionCustom"])
                        )
                    else:
                        story.append(Spacer(1, 6))
            i += 1
            continue

        # Tabela Markdown
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            story.append(build_table(table_lines, page_width))
            story.append(Spacer(1, 6))
            continue

        # Títulos
        if line.startswith("#### "):
            story.append(Paragraph(markup(line[5:]), styles["H3Custom"]))
        elif line.startswith("### "):
            story.append(Paragraph(markup(line[4:]), styles["H2Custom"]))
        elif line.startswith("## "):
            story.append(Paragraph(markup(line[3:]), styles["H1Custom"]))
        elif line.startswith("# "):
            style = styles["TitleCustom"] if first_h1 else styles["H1Custom"]
            story.append(Paragraph(markup(line[2:]), style))
            first_h1 = False
        elif line.startswith("---"):
            story.append(Spacer(1, 3))
            story.append(
                HRFlowable(
                    width="100%",
                    thickness=0.5,
                    color=GRID,
                    spaceBefore=2,
                    spaceAfter=6,
                )
            )
        # Sub-itens indentados
        elif raw_line.startswith("  - "):
            story.append(
                Paragraph("– " + markup(line[2:]), styles["SubBulletCustom"])
            )
        elif re.match(r"^\s{2,}\d+\.\s+", raw_line):
            num_match = re.match(r"^\s*(\d+\.)\s+(.*)$", raw_line)
            story.append(
                Paragraph(
                    f"<b>{num_match.group(1)}</b> {markup(num_match.group(2))}",
                    styles["SubBulletCustom"],
                )
            )
        # Itens de lista
        elif line.startswith("- "):
            story.append(
                Paragraph("• " + markup(line[2:]), styles["BulletCustom"])
            )
        elif re.match(r"^\d+\.\s+", line):
            num_match = re.match(r"^(\d+\.)\s+(.*)$", line)
            story.append(
                Paragraph(
                    f"<b>{num_match.group(1)}</b> {markup(num_match.group(2))}",
                    styles["BulletCustom"],
                )
            )
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
            self.setLineWidth(0.5)
            self.line(16 * mm, 14 * mm, A4[0] - 16 * mm, 14 * mm)
            self.setFont("Vera", 7.3)
            self.setFillColor(colors.HexColor("#64748B"))
            self.drawString(
                16 * mm,
                9.5 * mm,
                "SIGOA • Trabalho Final — Laboratório de Engenharia de Software • UNEMAT",
            )
            self.drawRightString(
                A4[0] - 16 * mm,
                9.5 * mm,
                f"Página {self._pageNumber} de {pages}",
            )
            self.restoreState()
            super().showPage()
        super().save()


def main():
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=16 * mm,
        bottomMargin=20 * mm,
        title="TRABALHO FINAL — LABORATÓRIO DE ENGENHARIA DE SOFTWARE (SIGOA)",
        author="Yuri Sardinha Milani e Emanuel Faria",
    )
    width = A4[0] - doc.leftMargin - doc.rightMargin
    doc.build(parse_markdown(SOURCE, width), canvasmaker=FooterCanvas)
    print(f"PDF gerado com sucesso: {OUTPUT}")


if __name__ == "__main__":
    main()
