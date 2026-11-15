# -*- coding: utf-8 -*-
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, PageBreak, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfgen import canvas

# ==================== FONTES PADRÃO (ARIAL ABNT) ====================
fonts_dir = "C:/Windows/Fonts"
if os.path.exists(os.path.join(fonts_dir, "arial.ttf")) and os.path.exists(os.path.join(fonts_dir, "arialbd.ttf")):
    pdfmetrics.registerFont(TTFont('Arial', os.path.join(fonts_dir, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Bold', os.path.join(fonts_dir, 'arialbd.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-Italic', os.path.join(fonts_dir, 'ariali.ttf') if os.path.exists(os.path.join(fonts_dir, 'ariali.ttf')) else os.path.join(fonts_dir, 'arial.ttf')))
    pdfmetrics.registerFont(TTFont('Arial-BoldItalic', os.path.join(fonts_dir, 'arialbi.ttf') if os.path.exists(os.path.join(fonts_dir, 'arialbi.ttf')) else os.path.join(fonts_dir, 'arialbd.ttf')))
    registerFontFamily('Arial', normal='Arial', bold='Arial-Bold', italic='Arial-Italic', boldItalic='Arial-BoldItalic')
    FONT_NORMAL = 'Arial'
    FONT_BOLD = 'Arial-Bold'
    FONT_ITALIC = 'Arial-Italic'
else:
    FONT_NORMAL = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'
    FONT_ITALIC = 'Helvetica-Oblique'

class SimpleNumberedCanvas(canvas.Canvas):
    """Numeração e rodapé simples e discretos"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont(FONT_NORMAL, 8.5)
        self.setFillColor(colors.HexColor("#4B5563"))
        
        # Cabeçalho sutil a partir da página 2
        if self._pageNumber > 1:
            self.drawString(40, 810, "SIGOA — Blueprint Técnico e Matriz de Decisões Arquiteturais")
            self.drawRightString(555, 810, "UNEMAT")
            self.setStrokeColor(colors.HexColor("#D1D5DB"))
            self.setLineWidth(0.5)
            self.line(40, 804, 555, 804)

        # Linha divisória e rodapé simples
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(40, 36, 555, 36)
        
        self.drawString(40, 24, "Integrantes: Yuri Sardinha Milani e Emanuel Faria • Laboratório de Engenharia de Software")
        self.drawRightString(555, 24, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def gerar_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(base_dir, "SIGOA_Blueprint_Tecnico_e_Decisoes.pdf")
    blueprint_img = os.path.join(base_dir, "blueprint_arquitetura.png")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=40,
        rightMargin=40,
        topMargin=42,
        bottomMargin=46
    )

    styles = getSampleStyleSheet()

    # Tipografia e estilos acadêmicos refinados e limpos
    style_inst = ParagraphStyle(
        'Instituicao', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9.5, leading=13,
        textColor=colors.HexColor("#1F2937"), alignment=1
    )
    
    style_proj_title = ParagraphStyle(
        'ProjectTitle', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=15, leading=19,
        textColor=colors.black, alignment=1, spaceBefore=4, spaceAfter=3
    )
    
    style_proj_sub = ParagraphStyle(
        'ProjectSub', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=10, leading=14,
        textColor=colors.HexColor("#374151"), alignment=1, spaceAfter=5
    )

    style_integrantes = ParagraphStyle(
        'Integrantes', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=9.5, leading=13,
        textColor=colors.black, alignment=1, spaceAfter=6
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=12, leading=16,
        textColor=colors.black, spaceBefore=6, spaceAfter=6,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9.5, leading=13,
        textColor=colors.HexColor("#1F2937"), spaceBefore=7, spaceAfter=3,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=9, leading=13.5,
        textColor=colors.black, spaceAfter=6, alignment=4 # Justificado
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.5, leading=12.5,
        textColor=colors.black, leftIndent=14, firstLineIndent=-10, spaceAfter=3,
        alignment=4 # Justificado
    )

    style_caption = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=8.5, leading=11.5,
        textColor=colors.HexColor("#1F2937"), alignment=1, spaceBefore=6, spaceAfter=4
    )

    # Estilos da tabela (simples, acadêmicos)
    style_th = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=8, leading=10.5,
        textColor=colors.black, alignment=0
    )

    style_td = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=7.5, leading=10,
        textColor=colors.black, alignment=0
    )

    style_td_bold = ParagraphStyle(
        'TDBold', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=7.5, leading=10,
        textColor=colors.black, alignment=0
    )

    # Estilo de referências ABNT (alinhado à esquerda, espaçamento simples)
    style_ref = ParagraphStyle(
        'ABNT_Ref', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.5, leading=12,
        textColor=colors.black, alignment=0,
        spaceAfter=7
    )

    story = []

    # ==================== PÁGINA 1: APRESENTAÇÃO E DIAGRAMA DO BLUEPRINT ====================
    story.append(Paragraph("UNIVERSIDADE DO ESTADO DE MATO GROSSO — UNEMAT", style_inst))
    story.append(Paragraph("CURSO DE ENGENHARIA DE SOFTWARE • LABORATÓRIO DE ENGENHARIA", style_inst))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#9CA3AF"), spaceBefore=2, spaceAfter=6))
    
    story.append(Paragraph("SIGOA — Sistema de Gerenciamento de Organização Acadêmica", style_proj_title))
    story.append(Paragraph("Documento de Arquitetura: Blueprint Técnico e Matriz de Decisões (MVP)", style_proj_sub))
    story.append(Paragraph("<b>Integrantes:</b> Yuri Sardinha Milani &nbsp;&nbsp;•&nbsp;&nbsp; Emanuel Faria", style_integrantes))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceBefore=0, spaceAfter=8))

    story.append(Paragraph("1. Blueprint Técnico da Arquitetura", style_h1))
    story.append(Paragraph(
        "O <b>SIGOA</b> foi projetado para mitigar os impactos da descentralização de prazos e materiais didáticos enfrentados por universitários no dia a dia acadêmico. A aplicação opera sob um modelo arquitetural em camadas fundamentado no padrão RESTful, promovendo o isolamento de responsabilidades entre interface do usuário, processamento de negócio, persistência relacional e integrações externas.",
        style_body
    ))
    story.append(Paragraph(
        "A <b>Figura 1</b> apresenta o blueprint técnico da solução, detalhando os módulos de frontend, serviços backend, base de dados relacional e serviços integrados que compõem o ecossistema do sistema.",
        style_body
    ))

    # Inserção do Blueprint em destaque
    if os.path.exists(blueprint_img):
        img_width = 515
        img_height = img_width / 1.4545 # Proporção 16:11 do matplotlib
        if img_height > 340:
            img_height = 335
            img_width = img_height * 1.4545
        
        story.append(Spacer(1, 4))
        story.append(Image(blueprint_img, width=img_width, height=img_height))
        story.append(Paragraph("Figura 1 – Blueprint técnico da arquitetura em camadas do SIGOA.", style_caption))

    # ==================== PÁGINA 2: DESCRIÇÃO DETALHADA DO BLUEPRINT ====================
    story.append(PageBreak())

    story.append(Paragraph("1.1. Detalhamento das Camadas e Componentes da Solução", style_h1))
    story.append(Paragraph(
        "Para garantir robustez, manutenibilidade e entrega integral do escopo no semestre letivo, cada camada do blueprint foi especificada com responsabilidades técnicas bem delimitadas:",
        style_body
    ))

    story.append(Paragraph("a) Camada de Apresentação (Frontend Web Responsivo)", style_h2))
    story.append(Paragraph(
        "• <b>Renderização e Estilização:</b> Construída com templates Jinja2 sobre HTML5 semântico e estilizada com o framework utilitário Tailwind CSS. Esta abordagem elimina a sobrecarga de ferramentas de empacotamento pesadas e assegura carregamento instantâneo em navegadores desktop e móveis.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Dinamismo Assíncrono:</b> O script cliente <code>app.js</code> (Vanilla JavaScript ES6+) consome os endpoints da API de forma assíncrona (Fetch API), permitindo navegação fluida entre visualizações mensal, semanal e diária, manipulação de compromissos em modais e filtros de categorias sem recarregamento da página (*Single Page Application feel*).",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Interface e Usabilidade:</b> Emprega a biblioteca de ícones Lucide para sinalização visual limpa e sistema de pílulas coloridas oficiais por modalidade (provas, aulas, trabalhos e seminários).",
        style_bullet
    ))

    story.append(Paragraph("b) Camada de Aplicação e Negócio (Backend REST)", style_h2))
    story.append(Paragraph(
        "• <b>Servidor e Rotas:</b> Desenvolvido em Python 3.10+ utilizando o microframework Flask (<code>app.py</code>). Concentra os controladores RESTful responsáveis por expor serviços para eventos (<code>/api/events</code>), arquivos (<code>/api/files</code>), métricas do painel (<code>/api/stats</code>) e autenticação federada.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Segurança e Sessões:</b> As credenciais de acesso são criptografadas com a biblioteca Werkzeug Security, aplicando derivação de chave robusta com algoritmo PBKDF2/SHA-256 e salting individual. O controle de estado é gerenciado via sessões HTTP seguras.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Conformidade com a LGPD (Lei nº 13.709/2018):</b> Implementa minimização estrita na coleta de dados (apenas nome, e-mail e senha), rota dedicada à portabilidade de dados em formato legível JSON (<code>/api/user/export-data</code>) e rotina de Direito ao Esquecimento com expurgo definitivo da conta.",
        style_bullet
    ))

    story.append(Paragraph("c) Camada de Persistência e Armazenamento", style_h2))
    story.append(Paragraph(
        "• <b>Banco de Dados Relacional:</b> Utiliza o SGBD SQLite3 (<code>academico.db</code>), conferindo conformidade transacional ACID, custo zero de infraestrutura e persistência em arquivo local. A integridade referencial entre as tabelas <code>users</code>, <code>events</code> e <code>user_files</code> é assegurada via <code>PRAGMA foreign_keys = ON</code> com exclusão em cascata.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Repositório de Arquivos:</b> Os materiais complementares anexados pelos alunos (PDFs, documentos e comprovantes) são gravados em diretório seguro do servidor (<code>uploads/</code>), vinculados ao identificador do proprietário (<code>user_id</code>) para garantir isolamento estrito.",
        style_bullet
    ))

    story.append(Paragraph("d) Serviços Externos e Protocolos de Integração", style_h2))
    story.append(Paragraph(
        "• <b>Google Identity & Calendar:</b> Integração com o Google Identity Services (OAuth 2.0 Sign-In) para autenticação rápida e geração de links diretos via URL API do Google Calendar, possibilitando ao estudante salvar compromissos com um clique.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Padrão Universal iCalendar:</b> Geração automatizada de arquivos <code>.ics</code> (em conformidade com a RFC 5545), tornando o SIGOA interoperável com Outlook, Apple Calendar e qualquer software compatível.",
        style_bullet
    ))

    story.append(Paragraph("e) Ferramentas de Suporte, Testes e Inteligência Artificial", style_h2))
    story.append(Paragraph(
        "• <b>Inteligências Artificiais:</b> Google Gemini (Antigravity CLI) utilizado como IA gratuita de suporte à modelagem, estruturação do blueprint e refinamento técnico; GitHub Copilot aplicado no editor como apoio na escrita de código e asserções.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Garantia da Qualidade e Prototipação:</b> Suíte de 6 testes automatizados desenvolvidos com <code>unittest</code> (cobrindo login, isolamento multiusuário, CRUD e uploads) e protótipo interativo construído no Figma durante o ciclo do Design Sprint.",
        style_bullet
    ))

    # ==================== PÁGINA 3: MATRIZ DE DECISÕES ARQUITETURAIS ====================
    story.append(PageBreak())

    story.append(Paragraph("2. Matriz de Decisões Arquiteturais", style_h1))
    story.append(Paragraph(
        "A matriz a seguir consolida as escolhas arquiteturais fundamentais adotadas pela equipe para o desenvolvimento do Produto Mínimo Viável (MVP), confrontando as opções descartadas com as respectivas justificativas técnicas:",
        style_body
    ))
    story.append(Spacer(1, 4))

    # Tabela com formatação simples, limpa e acadêmica
    matriz_dados = [
        [
            Paragraph("<b>Decisão</b>", style_th),
            Paragraph("<b>Alternativas consideradas</b>", style_th),
            Paragraph("<b>Escolha da equipe</b>", style_th),
            Paragraph("<b>Justificativa técnica</b>", style_th)
        ],
        [
            Paragraph("Tipo de aplicação", style_td_bold),
            Paragraph("Web / Mobile Nativo / Desktop", style_td),
            Paragraph("<b>Web Responsiva</b>", style_td),
            Paragraph("Acesso universal e imediato pelos estudantes via navegador em qualquer sistema operacional, sem necessidade de download ou instalação.", style_td)
        ],
        [
            Paragraph("Arquitetura de software", style_td_bold),
            Paragraph("Monolítica em camadas / Microsserviços / Serverless", style_td),
            Paragraph("<b>Monolítica em camadas (MVC/REST)</b>", style_td),
            Paragraph("Simplicidade de manutenção, baixo acoplamento e altíssima viabilidade de entrega para a equipe de dois integrantes durante o semestre acadêmico.", style_td)
        ],
        [
            Paragraph("Frontend", style_td_bold),
            Paragraph("React / Vue.js / Angular / HTML-CSS-JS puro", style_td),
            Paragraph("<b>HTML5, Tailwind CSS e Vanilla JS (Jinja2)</b>", style_td),
            Paragraph("Interface rápida, responsiva e dinâmica sem overhead de build (Webpack/Vite), com curvas de carregamento quase instantâneas.", style_td)
        ],
        [
            Paragraph("Backend", style_td_bold),
            Paragraph("Node.js (Express) / Django / FastAPI / Flask", style_td),
            Paragraph("<b>Python 3.10+ com Flask</b>", style_td),
            Paragraph("Microframework leve, altamente legível, ágil para estruturação de endpoints RESTful e facilidade para manipulação de dados e arquivos.", style_td)
        ],
        [
            Paragraph("Banco de dados", style_td_bold),
            Paragraph("MySQL / PostgreSQL / MongoDB / SQLite", style_td),
            Paragraph("<b>SQLite3 (academico.db)</b>", style_td),
            Paragraph("SGBD relacional serverless, persistência ACID em arquivo local, custo zero de infraestrutura e suporte nativo a chaves estrangeiras.", style_td)
        ],
        [
            Paragraph("Armazenamento de arquivos", style_td_bold),
            Paragraph("Nuvem (AWS S3, Google Drive) / Armazenamento Local", style_td),
            Paragraph("<b>Diretório local seguro (uploads/)</b>", style_td),
            Paragraph("Armazenamento direto no servidor com isolamento por usuário, custo operacional nulo e controle simplificado para download e remoção.", style_td)
        ],
        [
            Paragraph("Comunicação entre camadas", style_td_bold),
            Paragraph("WebSockets / GraphQL / HTTP REST", style_td),
            Paragraph("<b>HTTP/HTTPS REST (JSON / Multipart)</b>", style_td),
            Paragraph("Padrão da indústria com consumo assíncrono via Fetch API, permitindo atualização fluida do calendário sem recarregamento de página.", style_td)
        ],
        [
            Paragraph("Autenticação e Segurança", style_td_bold),
            Paragraph("JWT Tokens / Sessões HTTP / OAuth 2.0 exclusivo", style_td),
            Paragraph("<b>Sessões Seguras (PBKDF2) + Google OAuth 2.0</b>", style_td),
            Paragraph("Hash seguro de senhas com salting Werkzeug, conformidade estrita com a LGPD e opção prática de login unificado com conta Google.", style_td)
        ],
        [
            Paragraph("Integrações externas", style_td_bold),
            Paragraph("Nenhuma / APIs proprietárias / Google Calendar & ICS", style_td),
            Paragraph("<b>Google Calendar API + iCalendar (.ics)</b>", style_td),
            Paragraph("Permite ao estudante sincronizar seus prazos com Google Agenda, Outlook e Apple Calendar em 1 clique sem custos de licença.", style_td)
        ],
        [
            Paragraph("Inteligência Artificial gratuita", style_td_bold),
            Paragraph("ChatGPT 3.5 / Claude Sonnet / Gemini CLI", style_td),
            Paragraph("<b>Google Gemini (Antigravity CLI)</b>", style_td),
            Paragraph("Auxílio gratuito e nativo no planejamento da arquitetura, geração de código-fonte, blueprints e documentação técnica.", style_td)
        ],
        [
            Paragraph("Inteligência Artificial paga / estudante", style_td_bold),
            Paragraph("ChatGPT Plus / Claude Pro / GitHub Copilot", style_td),
            Paragraph("<b>GitHub Copilot</b>", style_td),
            Paragraph("Assistência de código contextual em tempo real no editor, agilizando o desenvolvimento das rotas Flask e dos testes automatizados.", style_td)
        ],
        [
            Paragraph("Ferramentas de apoio e validação", style_td_bold),
            Paragraph("Miro / Trello / Figma e Google Forms", style_td),
            Paragraph("<b>Figma e Google Forms</b>", style_td),
            Paragraph("Prototipação de alta fidelidade das interfaces durante o Design Sprint e validação estruturada da usabilidade com estudantes reais.", style_td)
        ]
    ]

    col_widths = [105, 125, 125, 160] # 515 pt
    t_matriz = Table(matriz_dados, colWidths=col_widths, repeatRows=1)
    
    t_matriz.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#E5E7EB")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#9CA3AF")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
    ]))

    story.append(t_matriz)
    story.append(Spacer(1, 10))

    # ==================== PÁGINA 4: REFERÊNCIAS ABNT ====================
    story.append(PageBreak())

    story.append(Paragraph("3. Fontes e Referências Utilizadas", style_h1))
    story.append(Paragraph(
        "A seguir, relacionam-se as fontes bibliográficas, normativas técnicas, documentações oficiais e tecnologias consultadas para a concepção e implementação do projeto, padronizadas rigorosamente conforme a norma <b>ABNT NBR 6023:2018</b> (Informação e documentação — Referências — Elaboração), dispostas em estrita ordem alfabética:",
        style_body
    ))
    story.append(Spacer(1, 8))

    referencias_abnt = [
        "BRASIL. <b>Lei nº 13.709, de 14 de agosto de 2018</b>. Dispõe sobre a proteção de dados pessoais e altera a Lei nº 12.965, de 23 de abril de 2014 (Marco Civil da Internet). Brasília, DF: Presidência da República, 2018. Disponível em: &lt;http://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm&gt;. Acesso em: 17 set. 2026.",
        
        "DESRUISSEAUX, Bernard (ed.). <b>RFC 5545: Internet Calendaring and Scheduling Core Object Specification (iCalendar)</b>. Reston: Internet Engineering Task Force (IETF), 2009. Disponível em: &lt;https://datatracker.ietf.org/doc/html/rfc5545&gt;. Acesso em: 17 set. 2026.",
        
        "FIGMA INC. <b>Figma: collaborative interface design tool</b>. San Francisco: Figma Inc., 2024. Disponível em: &lt;https://www.figma.com/&gt;. Acesso em: 17 set. 2026.",
        
        "GITHUB. <b>GitHub Copilot: your AI pair programmer</b>. San Francisco: GitHub Inc., 2024. Disponível em: &lt;https://github.com/features/copilot&gt;. Acesso em: 17 set. 2026.",
        
        "GOOGLE LLC. <b>Gemini: large language models for advanced reasoning and coding assistance</b>. Mountain View: Google AI, 2024. Disponível em: &lt;https://gemini.google.com/&gt;. Acesso em: 17 set. 2026.",
        
        "GOOGLE LLC. <b>Google Calendar API &amp; Identity Services Documentation</b>. Mountain View: Google Developers, 2024. Disponível em: &lt;https://developers.google.com/calendar&gt;. Acesso em: 17 set. 2026.",
        
        "HIPP, D. Richard et al. <b>SQLite Database Engine</b>. Charlotte: SQLite Development Team, 2024. Disponível em: &lt;https://www.sqlite.org/docs.html&gt;. Acesso em: 17 set. 2026.",
        
        "KNAPP, Jake; ZERATSKY, John; KOWITZ, Braden. <b>Sprint: como testar novas ideias e resolver grandes problemas em apenas cinco dias</b>. Tradução de Cássio de Arantes Leite. 1. ed. Rio de Janeiro: Intrínseca, 2017.",
        
        "PALLETS PROJECTS. <b>Flask: a Python microframework</b>. Versão 3.0.x. 2024. Disponível em: &lt;https://flask.palletsprojects.com/&gt;. Acesso em: 17 set. 2026.",
        
        "PALLETS PROJECTS. <b>Werkzeug: the comprehensive WSGI web application library</b>. 2024. Disponível em: &lt;https://palletsprojects.com/p/werkzeug/&gt;. Acesso em: 17 set. 2026.",
        
        "PRESSMAN, Roger S.; MAXIM, Bruce R. <b>Engenharia de software: uma abordagem profissional</b>. 8. ed. Porto Alegre: AMGH, 2016.",
        
        "PYTHON SOFTWARE FOUNDATION. <b>Python Language Reference: release 3.10</b>. Beaverton: Python Software Foundation, 2023. Disponível em: &lt;https://www.python.org/doc/&gt;. Acesso em: 17 set. 2026.",
        
        "SOMMERVILLE, Ian. <b>Engenharia de software</b>. 10. ed. São Paulo: Pearson Education do Brasil, 2019.",
        
        "TAILWIND LABS. <b>Tailwind CSS: a utility-first CSS framework for rapid UI development</b>. Versão 3.4. 2024. Disponível em: &lt;https://tailwindcss.com/docs&gt;. Acesso em: 17 set. 2026.",
        
        "UNIVERSIDADE DO ESTADO DE MATO GROSSO (UNEMAT). <b>Plano de ação MVP: gerenciamento acadêmico - Design Sprint em 7 dias</b>. Tangará da Serra: Laboratório de Engenharia de Software, 2024.",
        
        "WORLD WIDE WEB CONSORTIUM (W3C). <b>HTML5: a vocabulary and associated APIs for HTML and XHTML</b>. W3C Recommendation. 2014. Disponível em: &lt;https://www.w3.org/TR/html5/&gt;. Acesso em: 17 set. 2026."
    ]

    for ref in referencias_abnt:
        story.append(Paragraph(ref, style_ref))

    doc.build(story, canvasmaker=SimpleNumberedCanvas)
    print(f"Sucesso! PDF reconstruído com alta organização em: {output_pdf}")

if __name__ == "__main__":
    gerar_pdf()
