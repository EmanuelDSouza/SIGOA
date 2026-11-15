# -*- coding: utf-8 -*-
"""Renderiza a saída capturada do unittest como evidência visual imprimível."""
from pathlib import Path
import textwrap
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
LOG = ROOT / "Evidencia_Testes_SIGOA_2026-11-13.txt"
OUTPUT = ROOT / "Evidencia_Testes_SIGOA_2026-11-13.png"

font_path = Path(r"C:\Windows\Fonts\consola.ttf")
font_bold_path = Path(r"C:\Windows\Fonts\consolab.ttf")
font = ImageFont.truetype(str(font_path), 22)
font_bold = ImageFont.truetype(str(font_bold_path), 27)
title_font = ImageFont.truetype(str(font_bold_path), 30)

raw = LOG.read_text(encoding="utf-8").strip().splitlines()
wrapped = []
for line in raw:
    wrapped.extend(textwrap.wrap(line, width=105, subsequent_indent="    ") or [""])

width = 1900
line_height = 34
top = 145
bottom = 42
height = top + len(wrapped) * line_height + bottom
image = Image.new("RGB", (width, height), "#111827")
draw = ImageDraw.Draw(image)
draw.rounded_rectangle((22, 20, width - 22, height - 20), radius=22,
                       fill="#0b1220", outline="#334155", width=2)
draw.text((55, 43), "SIGOA | Evidência da execução automatizada", font=title_font,
          fill="#e2e8f0")
draw.text((58, 92), "python -m unittest test_app.SIGOATestCase -v  |  13/11/2026",
          font=font_bold, fill="#93c5fd")

y = top
for line in wrapped:
    color = "#86efac" if line.rstrip().endswith("... ok") or line == "OK" else "#cbd5e1"
    if line.startswith("Ran 8 tests"):
        color = "#86efac"
    draw.text((60, y), line, font=font, fill=color)
    y += line_height

image.save(OUTPUT, optimize=True)
print(OUTPUT)
