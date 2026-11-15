# -*- coding: utf-8 -*-
import os
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

fonts_dir = "C:/Windows/Fonts"
if os.path.exists(os.path.join(fonts_dir, "arial.ttf")):
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(fonts_dir, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(fonts_dir, 'arialbd.ttf')))
    FONT_NORMAL = 'Arial'
    FONT_BOLD = 'Arial-Bold'
else:
    FONT_NORMAL = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def build_pdf():
    pdf_path = os.path.join(os.path.dirname(__file__), "Blueprint_Arquitetural_SIGOA.pdf")
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=landscape(A4),
        leftMargin=40,
        rightMargin=40,
        topMargin=35,
        bottomMargin=35
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'Title', parent=styles['Heading1'],
        fontName=FONT_BOLD, fontSize=13, leading=16,
        textColor=colors.black, spaceAfter=2
    )

    sub_style = ParagraphStyle(
        'Sub', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=9, leading=12,
        textColor=colors.HexColor("#374151"), spaceAfter=10
    )
    
    th_style = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9, leading=12,
        textColor=colors.black
    )
    
    td_style = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.5, leading=11.5,
        textColor=colors.black
    )

    story = [
        Paragraph("SIGOA — Sistema de Gerenciamento de Organização Acadêmica", title_style),
        Paragraph("Blueprint da Arquitetura Proposta", sub_style)
    ]

    table_data = [
        [
            Paragraph("<b>Decisão</b>", th_style),
            Paragraph("<b>Alternativas consideradas</b>", th_style),
            Paragraph("<b>Escolha da equipe</b>", th_style),
            Paragraph("<b>Justificativa</b>", th_style)
        ],
        [
            Paragraph("Tipo de aplicação", td_style),
            Paragraph("Web / Mobile / Desktop", td_style),
            Paragraph("Web", td_style),
            Paragraph("Facilita o acesso direto pelos estudantes via navegador", td_style)
        ],
        [
            Paragraph("Arquitetura", td_style),
            Paragraph("Monolítica / Microsserviços", td_style),
            Paragraph("Monolítica em camadas", td_style),
            Paragraph("Simples de manter e viável para o semestre", td_style)
        ],
        [
            Paragraph("Frontend", td_style),
            Paragraph("React / Vue / HTML-CSS-JS", td_style),
            Paragraph("HTML, CSS e JS (Tailwind e Jinja2)", td_style),
            Paragraph("Interface rápida, responsiva e sem sobrecarga de frameworks", td_style)
        ],
        [
            Paragraph("Backend", td_style),
            Paragraph("Node.js / Django / Flask", td_style),
            Paragraph("Python (Flask)", td_style),
            Paragraph("Leve, rápido para criar rotas e fácil de integrar", td_style)
        ],
        [
            Paragraph("Banco de dados", td_style),
            Paragraph("MySQL / PostgreSQL / SQLite", td_style),
            Paragraph("SQLite", td_style),
            Paragraph("Banco relacional simples, em arquivo local e sem custos", td_style)
        ],
        [
            Paragraph("Armazenamento de arquivos", td_style),
            Paragraph("Nuvem (S3/Drive) / Local", td_style),
            Paragraph("Pasta local (uploads)", td_style),
            Paragraph("Armazenamento direto no servidor com segurança e custo zero", td_style)
        ],
        [
            Paragraph("Comunicação", td_style),
            Paragraph("WebSockets / GraphQL / HTTP REST", td_style),
            Paragraph("HTTP REST (JSON)", td_style),
            Paragraph("Padrão simples e assíncrono para atualizar dados sem recarregar a tela", td_style)
        ],
        [
            Paragraph("Integrações externas", td_style),
            Paragraph("Nenhuma / Google APIs", td_style),
            Paragraph("Google Calendar e Google Identity", td_style),
            Paragraph("Login rápido e sincronização direta com a agenda do aluno", td_style)
        ],
        [
            Paragraph("IA gratuita", td_style),
            Paragraph("ChatGPT / Claude / Gemini", td_style),
            Paragraph("Gemini (Google Antigravity)", td_style),
            Paragraph("Auxílio no planejamento, testes e geração de código", td_style)
        ],
        [
            Paragraph("IA paga", td_style),
            Paragraph("ChatGPT Plus / Claude Pro / Copilot", td_style),
            Paragraph("GitHub Copilot", td_style),
            Paragraph("Autocompletar de código no editor", td_style)
        ],
        [
            Paragraph("Ferramentas de apoio", td_style),
            Paragraph("Miro / Trello / Figma e Forms", td_style),
            Paragraph("Figma e Google Forms", td_style),
            Paragraph("Prototipação da interface e validação com os alunos", td_style)
        ]
    ]

    t = Table(table_data, colWidths=[130, 180, 180, 272])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E5E7EB")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#9CA3AF")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('PADDING', (0,0), (-1,-1), 4.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))

    story.append(t)
    doc.build(story)
    print(f"PDF successfully built at: {pdf_path}")

if __name__ == "__main__":
    build_pdf()
