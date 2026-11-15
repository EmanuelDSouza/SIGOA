# -*- coding: utf-8 -*-
"""Gera o arquivo Word (.docx) editável do Trabalho Final — Laboratório de Engenharia de Software (SIGOA)."""
from pathlib import Path
import re

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from docx.shared import Inches, Mm, Pt, RGBColor

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "SIGOA_Trabalho_Final_Laboratorio_Engenharia_Software.md"
OUTPUT = ROOT / "SIGOA_Trabalho_Final_Laboratorio_Engenharia_Software.docx"

NAVY = RGBColor(0x17, 0x36, 0x5D)
SUB_NAVY = RGBColor(0x23, 0x4B, 0x7A)
INK = RGBColor(0x1E, 0x29, 0x3B)
MUTED = RGBColor(0x47, 0x55, 0x69)

TOKEN_RE = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`)")


def clean_symbols(text: str) -> str:
    replacements = {
        r"$\rightarrow$": "->",
        r"$\leftrightarrow$": "<->",
        r"$\ge 4,0/5,0$": ">= 4,0/5,0",
        r"$\approx 0,43\text{s}$": "~0,43s",
        r"$4,25/5,0$": "4,25/5,0",
        r"$4,5/5,0$": "4,5/5,0",
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text


def set_cell_shading(cell, fill_hex: str):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tc_pr.append(shd)


def set_cell_margins(cell, top=80, bottom=80, left=110, right=110):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("bottom", bottom), ("left", left), ("right", right)):
        node = OxmlElement(f"w:{side}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def add_formatted_runs(
    paragraph,
    text: str,
    font_size: float = 10.5,
    base_color: RGBColor = INK,
    base_bold: bool = False,
):
    text = clean_symbols(text.strip())
    parts = TOKEN_RE.split(text)
    for part in parts:
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            run = paragraph.add_run(part[2:-2])
            run.bold = True
            run.font.name = "Calibri"
            run.font.size = Pt(font_size)
            run.font.color.rgb = base_color
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.italic = True
            run.bold = base_bold
            run.font.name = "Calibri"
            run.font.size = Pt(font_size)
            run.font.color.rgb = base_color
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            run = paragraph.add_run(part[1:-1])
            run.bold = True
            run.font.name = "Consolas"
            run.font.size = Pt(max(font_size - 0.5, 8.5))
            run.font.color.rgb = base_color
        else:
            run = paragraph.add_run(part)
            run.bold = base_bold
            run.font.name = "Calibri"
            run.font.size = Pt(font_size)
            run.font.color.rgb = base_color


def split_table_row(line: str):
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def add_markdown_table(doc: Document, lines):
    rows = [split_table_row(line) for line in lines]
    if len(rows) > 1 and all(
        re.fullmatch(r":?-{2,}:?", c.replace(" ", "")) for c in rows[1]
    ):
        rows.pop(1)
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    table = doc.add_table(rows=len(rows), cols=col_count)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for r_idx, row in enumerate(rows):
        is_header = r_idx == 0
        for c_idx, cell_text in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            set_cell_margins(cell)
            if is_header:
                set_cell_shading(cell, "DCE8F4")
            elif r_idx % 2 == 0:
                set_cell_shading(cell, "F8FAFC")

            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(
                p,
                cell_text,
                font_size=9.0,
                base_color=NAVY if is_header else INK,
                base_bold=is_header,
            )


def build_docx():
    doc = Document()

    # Margens A4 (16 mm nas laterais e topo, 18 mm na base)
    for section in doc.sections:
        section.page_width = Mm(210)
        section.page_height = Mm(297)
        section.top_margin = Mm(16)
        section.bottom_margin = Mm(18)
        section.left_margin = Mm(16)
        section.right_margin = Mm(16)

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.LEFT
        fr = fp.add_run("SIGOA • Trabalho Final — Laboratório de Engenharia de Software • UNEMAT")
        fr.font.name = "Calibri"
        fr.font.size = Pt(8.5)
        fr.font.color.rgb = MUTED

    normal_style = doc.styles["Normal"]
    normal_style.font.name = "Calibri"
    normal_style.font.size = Pt(10.5)
    normal_style.font.color.rgb = INK

    lines = SOURCE.read_text(encoding="utf-8").splitlines()
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
            i += 1  # pula fechamento ```
            code_table = doc.add_table(rows=1, cols=1)
            code_table.style = "Table Grid"
            cell = code_table.cell(0, 0)
            set_cell_shading(cell, "F1F5F9")
            set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_before = Pt(0)
            cp.paragraph_format.space_after = Pt(0)
            cp.paragraph_format.line_spacing = 1.05
            crun = cp.add_run("\n".join(code_lines))
            crun.font.name = "Consolas"
            crun.font.size = Pt(8.5)
            crun.font.color.rgb = INK
            doc.add_paragraph().paragraph_format.space_after = Pt(2)
            continue

        # Imagem ![legenda](arquivo)
        if line.startswith("!["):
            match = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", line)
            if match:
                caption_text, rel_path = match.group(1), match.group(2)
                image_path = SOURCE.parent / rel_path
                if image_path.exists():
                    ip = doc.add_paragraph()
                    ip.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    ip.paragraph_format.space_before = Pt(6)
                    ip.paragraph_format.space_after = Pt(3)
                    irun = ip.add_run()
                    irun.add_picture(str(image_path), width=Inches(6.4))
                    if caption_text:
                        cp = doc.add_paragraph()
                        cp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                        cp.paragraph_format.space_after = Pt(8)
                        add_formatted_runs(cp, f"*{caption_text}*", font_size=9.0, base_color=MUTED)
            i += 1
            continue

        # Tabela Markdown
        if line.startswith("|"):
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                table_lines.append(lines[i].strip())
                i += 1
            add_markdown_table(doc, table_lines)
            sp = doc.add_paragraph()
            sp.paragraph_format.space_before = Pt(0)
            sp.paragraph_format.space_after = Pt(4)
            continue

        # Títulos
        if line.startswith("# "):
            p = doc.add_paragraph()
            if first_h1:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(8)
                add_formatted_runs(p, line[2:], font_size=18.0, base_color=NAVY, base_bold=True)
                first_h1 = False
            else:
                p.paragraph_format.space_before = Pt(14)
                p.paragraph_format.space_after = Pt(6)
                add_formatted_runs(p, line[2:], font_size=14.0, base_color=NAVY, base_bold=True)
        elif line.startswith("## "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            add_formatted_runs(p, line[3:], font_size=14.0, base_color=NAVY, base_bold=True)
        elif line.startswith("### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            add_formatted_runs(p, line[4:], font_size=12.0, base_color=SUB_NAVY, base_bold=True)
        elif line.startswith("#### "):
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.keep_with_next = True
            add_formatted_runs(p, line[5:], font_size=10.8, base_color=INK, base_bold=True)
        elif line.startswith("---"):
            i += 1
            continue
        elif raw_line.startswith("  - "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Mm(10)
            p.paragraph_format.first_line_indent = Mm(-4)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2.5)
            add_formatted_runs(p, "– " + line[2:], font_size=10.0)
        elif re.match(r"^\s{2,}\d+\.\s+", raw_line):
            num_match = re.match(r"^\s*(\d+\.)\s+(.*)$", raw_line)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Mm(10)
            p.paragraph_format.first_line_indent = Mm(-5)
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2.5)
            add_formatted_runs(p, f"**{num_match.group(1)}** {num_match.group(2)}", font_size=10.0)
        elif line.startswith("- "):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Mm(5)
            p.paragraph_format.first_line_indent = Mm(-4)
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(3)
            add_formatted_runs(p, "• " + line[2:], font_size=10.5)
        elif re.match(r"^\d+\.\s+", line):
            num_match = re.match(r"^(\d+\.)\s+(.*)$", line)
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Mm(5)
            p.paragraph_format.first_line_indent = Mm(-5)
            p.paragraph_format.space_before = Pt(1.5)
            p.paragraph_format.space_after = Pt(3)
            add_formatted_runs(p, f"**{num_match.group(1)}** {num_match.group(2)}", font_size=10.5)
        else:
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(5)
            p.paragraph_format.line_spacing = 1.15
            add_formatted_runs(p, line, font_size=10.5)

        i += 1

    doc.save(str(OUTPUT))
    print(f"DOCX gerado com sucesso: {OUTPUT}")


if __name__ == "__main__":
    build_docx()
