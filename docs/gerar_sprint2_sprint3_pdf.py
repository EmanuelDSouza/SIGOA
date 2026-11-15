# -*- coding: utf-8 -*-
"""
Script de Geração do Documento Oficial:
SIGOA — Do Projeto ao Desenvolvimento: Sprint 2 (Núcleo do MVP) e Planejamento da Sprint 3
Laboratório de Engenharia de Software — UNEMAT
Autores: Yuri Sardinha Milani e Emanuel Faria
"""

import os
import shutil
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

# ==================== REGISTRO DE FONTES (ARIAL ABNT) ====================
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

# ==================== CANVAS COM CABEÇALHO E RODAPÉ ABNT ====================
class NumberedCanvas(canvas.Canvas):
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
        self.setFont(FONT_NORMAL, 8)
        self.setFillColor(colors.HexColor("#4B5563"))

        # Cabeçalho a partir da página 2
        if self._pageNumber > 1:
            self.drawString(36, 808, "SIGOA — Sprint 2: Núcleo do MVP e Planejamento da Sprint 3")
            self.drawRightString(559, 808, "UNEMAT • Eng. de Software")
            self.setStrokeColor(colors.HexColor("#D1D5DB"))
            self.setLineWidth(0.5)
            self.line(36, 802, 559, 802)

        # Rodapé em todas as páginas
        self.setStrokeColor(colors.HexColor("#D1D5DB"))
        self.setLineWidth(0.5)
        self.line(36, 36, 559, 36)

        self.drawString(36, 24, "Integrantes: Yuri Sardinha Milani e Emanuel Faria • Laboratório de Engenharia de Software")
        self.drawRightString(559, 24, f"Página {self._pageNumber} de {page_count}")
        self.restoreState()

def gerar_pdf_sprint2_sprint3():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(base_dir, "SIGOA_Backlog_Sprint2_Blueprint.pdf")
    output_pdf_alt = os.path.join(base_dir, "SIGOA_Sprint2_Nucleo_MVP_e_Planejamento_Sprint3.pdf")
    blueprint_img = os.path.join(base_dir, "blueprint_arquitetura.png")

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=40,
        bottomMargin=44
    )

    styles = getSampleStyleSheet()

    # --- PALETA DE CORES PROFISSIONAL ---
    c_primary = colors.HexColor("#1E3A8A")     # Azul institucional escuro
    c_secondary = colors.HexColor("#2563EB")   # Azul primário da interface
    c_dark = colors.HexColor("#111827")        # Texto escuro quase preto
    c_gray_sub = colors.HexColor("#4B5563")    # Texto secundário
    c_border = colors.HexColor("#9CA3AF")      # Borda cinza suave
    c_th_bg = colors.HexColor("#E5E7EB")       # Fundo cabeçalho tabela
    c_row_alt = colors.HexColor("#F9FAFB")     # Linha alternada clara

    # --- ESTILOS DE PARÁGRAFO ---
    style_inst = ParagraphStyle(
        'Instituicao', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9.5, leading=13,
        textColor=c_dark, alignment=1
    )

    style_inst_sub = ParagraphStyle(
        'InstituicaoSub', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.5, leading=12,
        textColor=c_gray_sub, alignment=1, spaceAfter=4
    )

    style_title = ParagraphStyle(
        'DocTitle', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=15, leading=19,
        textColor=c_dark, alignment=1, spaceBefore=4, spaceAfter=3
    )

    style_sub = ParagraphStyle(
        'DocSub', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=10.5, leading=14.5,
        textColor=c_secondary, alignment=1, spaceAfter=4
    )

    style_meta = ParagraphStyle(
        'DocMeta', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.5, leading=12.5,
        textColor=c_dark, alignment=1, spaceAfter=6
    )

    style_h1 = ParagraphStyle(
        'Heading1_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=11, leading=14.5,
        textColor=c_primary, spaceBefore=7, spaceAfter=3.5,
        keepWithNext=True
    )

    style_h2 = ParagraphStyle(
        'Heading2_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=9.2, leading=12.5,
        textColor=c_dark, spaceBefore=5, spaceAfter=2.5,
        keepWithNext=True
    )

    style_h3 = ParagraphStyle(
        'Heading3_Custom', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=8.5, leading=11.5,
        textColor=c_secondary, spaceBefore=3.5, spaceAfter=2,
        keepWithNext=True
    )

    style_body = ParagraphStyle(
        'Body_Custom', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=8.2, leading=12,
        textColor=c_dark, spaceAfter=4, alignment=4 # Justificado
    )

    style_bullet = ParagraphStyle(
        'Bullet_Custom', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=7.8, leading=11,
        textColor=c_dark, leftIndent=11, firstLineIndent=-7, spaceAfter=2,
        alignment=4
    )

    style_caption = ParagraphStyle(
        'Caption', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=7.8, leading=10.5,
        textColor=c_gray_sub, alignment=1, spaceBefore=3, spaceAfter=3
    )

    # Estilos de Tabela
    style_th = ParagraphStyle(
        'TH', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=7.2, leading=9.2,
        textColor=c_dark, alignment=0
    )

    style_th_center = ParagraphStyle(
        'THCenter', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=7.2, leading=9.2,
        textColor=c_dark, alignment=1
    )

    style_td = ParagraphStyle(
        'TD', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=6.8, leading=8.6,
        textColor=c_dark, alignment=0
    )

    style_td_bold = ParagraphStyle(
        'TDBold', parent=styles['Normal'],
        fontName=FONT_BOLD, fontSize=6.8, leading=8.6,
        textColor=c_dark, alignment=0
    )

    style_td_center = ParagraphStyle(
        'TDCenter', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=6.8, leading=8.6,
        textColor=c_dark, alignment=1
    )

    style_ref = ParagraphStyle(
        'ABNT_Ref', parent=styles['Normal'],
        fontName=FONT_NORMAL, fontSize=7.5, leading=10.5,
        textColor=c_dark, alignment=0, spaceAfter=4
    )

    story = []

    # ==================== PÁGINA 1: CAPA, CONTEXTO E BLUEPRINT ====================
    story.append(Paragraph("UNIVERSIDADE DO ESTADO DE MATO GROSSO — UNEMAT", style_inst))
    story.append(Paragraph("CURSO DE ENGENHARIA DE SOFTWARE • LABORATÓRIO DE ENGENHARIA", style_inst_sub))
    story.append(HRFlowable(width="100%", thickness=0.8, color=c_border, spaceBefore=2, spaceAfter=5))

    story.append(Paragraph("SIGOA — Sistema de Gerenciamento de Organização Acadêmica", style_title))
    story.append(Paragraph("Do Projeto ao Desenvolvimento: Sprint 2 (Núcleo do MVP) e Planejamento da Sprint 3", style_sub))
    story.append(Paragraph(
        "<b>Entrega Oficial:</b> Desenvolvimento do Núcleo do Produto • Integração e APIs • Acompanhamento da Qualidade • Sprint Review 2 e Retrospectiva • Planejamento da Sprint 3 (Integração e Evolução)",
        style_meta
    ))
    story.append(Paragraph(
        "<b>Acadêmicos:</b> Yuri Sardinha Milani &nbsp;&nbsp;•&nbsp;&nbsp; Emanuel Faria &nbsp;&nbsp;|&nbsp;&nbsp; <b>Local:</b> Cáceres — MT • 2026",
        style_meta
    ))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#D1D5DB"), spaceBefore=0, spaceAfter=6))

    story.append(Paragraph("1. Contexto, Transição e Direcionamento do Produto", style_h1))
    story.append(Paragraph(
        "O <b>SIGOA</b> foi concebido para mitigar os impactos da dispersão de prazos e atividades enfrentada por universitários. Na <b>Sprint 1 (Fundação Técnica)</b>, foi estabelecida a infraestrutura operacional: ambiente Flask, banco relacional SQLite3 com integridade referencial, autenticação segura com PBKDF2/Werkzeug, proteção de rotas por decorators e a casca visual da agenda mensal.",
        style_body
    ))
    story.append(Paragraph(
        "A presente <b>Sprint 2 — Núcleo do MVP</b> teve como missão transformar a estrutura básica em um ambiente ativo e reativo de gestão acadêmica. Foram implementadas e integradas as funcionalidades prioritárias (P0): <b>criação, edição, exclusão com confirmação, categorização visual por cores oficiais (aulas, provas, trabalhos e entregas) e sistema de lembretes parametrizados</b>.",
        style_body
    ))
    story.append(Paragraph(
        "Adicionalmente, este documento consolida a <b>Sprint Review 2</b>, a <b>Retrospectiva da Equipe</b> e apresenta de forma estruturada o <b>Planejamento da Sprint 3 (Integração e Evolução)</b>, delineando os requisitos de integração externa com Google Calendar API, exportação universal iCalendar (RFC 5545), gestão de anexos acadêmicos, visão semanal e painel de conformidade com a LGPD.",
        style_body
    ))

    story.append(Paragraph("2. Blueprint Técnico da Solução Arquitetural", style_h1))
    story.append(Paragraph(
        "A solução adota arquitetura monolítica em camadas fundamentada no padrão RESTful: <b>Apresentação (Web Responsiva / SPA-like)</b>, <b>Aplicação e Negócio (RESTful Flask)</b>, <b>Persistência de Dados (SQLite3)</b> e <b>Serviços Integrados</b>. A Figura 1 ilustra o blueprint arquitetural atualizado e em plena operação no projeto:",
        style_body
    ))

    if os.path.exists(blueprint_img):
        img_width = 515
        img_height = img_width / 1.55
        if img_height > 275:
            img_height = 270
            img_width = img_height * 1.55
        story.append(Spacer(1, 2))
        story.append(Image(blueprint_img, width=img_width, height=img_height))
        story.append(Paragraph("Figura 1 – Blueprint técnico da arquitetura em camadas do SIGOA em execução.", style_caption))

    # ==================== PÁGINA 2: COMPONENTES E ESTIMATIVAS FIBONACCI ====================
    story.append(PageBreak())

    story.append(Paragraph("2.1. Componentes e Camadas Integrados na Sprint 2", style_h1))
    story.append(Paragraph(
        "Na Sprint 2, a arquitetura avançou da fundação para a plena integração operacional entre interface assíncrona, lógica de negócio e persistência relacional:",
        style_body
    ))

    comp_data = [
        [Paragraph("<b>Camada / Componente</b>", style_th), Paragraph("<b>Tecnologias Empregadas</b>", style_th), Paragraph("<b>Papel Operacional na Sprint 2</b>", style_th)],
        [
            Paragraph("Apresentação (Frontend)", style_td_bold),
            Paragraph("HTML5, Tailwind CSS, Jinja2, Vanilla JS ES6+ (app.js), Lucide Icons", style_td),
            Paragraph("Modais dinâmicos para criação/edição de eventos, pílulas visuais de status, filtros por categoria e requisições assíncronas via Fetch API sem recarregar a tela.", style_td)
        ],
        [
            Paragraph("Aplicação e Negócio (Backend)", style_td_bold),
            Paragraph("Python 3.10+, Microframework Flask (app.py)", style_td),
            Paragraph("Controladores RESTful (/api/events), sanitização de inputs, validação de datas/horários, isolamento por user_id e respostas JSON com status codes HTTP precisos.", style_td)
        ],
        [
            Paragraph("Persistência Relacional", style_td_bold),
            Paragraph("SQLite3 (academico.db), PRAGMA foreign_keys = ON", style_td),
            Paragraph("Tabela events operando com integridade referencial estrita, transações ACID, campos tipados (datas, horários, categorias) e exclusão em cascata associada ao usuário.", style_td)
        ],
        [
            Paragraph("Protocolo e Comunicação", style_td_bold),
            Paragraph("HTTP/HTTPS RESTful (JSON e Multipart)", style_td),
            Paragraph("Consumo assíncrono via Fetch API; envio de payloads JSON padronizados; headers de controle de cache (no-cache) para atualização em tempo real.", style_td)
        ],
        [
            Paragraph("Segurança e Controle de Acesso", style_td_bold),
            Paragraph("Sessões HTTP Seguras, Werkzeug PBKDF2/SHA-256", style_td),
            Paragraph("Decorators @login_required e @api_login_required bloqueando acessos anônimos; garantia absoluta de isolamento multiusuário contra acessos indevidos.", style_td)
        ],
        [
            Paragraph("Garantia da Qualidade", style_td_bold),
            Paragraph("Módulo unittest (Python Standard Library)", style_td),
            Paragraph("Suíte de 6 testes automatizados validando autenticação, CRUD completo de eventos, integridade do banco e isolamento entre usuários sem falhas.", style_td)
        ]
    ]

    t_comp = Table(comp_data, colWidths=[110, 145, 260])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_comp)
    story.append(Spacer(1, 4))

    story.append(Paragraph("4. Estimativas e Planejamento — Story Points (Sequência Fibonacci)", style_h1))
    story.append(Paragraph(
        "A equipe utilizou a técnica de <b>Planning Poker</b> baseada na sequência de Fibonacci (1, 2, 3, 5, 8, 13) para dimensionar a complexidade técnica, esforço de implementação e incerteza de cada história de usuário ao longo do projeto:",
        style_body
    ))

    fibo_data = [
        [Paragraph("<b>História de Usuário</b>", style_th), Paragraph("<b>Pontos</b>", style_th_center), Paragraph("<b>Ciclo / Alocação</b>", style_th), Paragraph("<b>Justificativa Técnica da Estimativa</b>", style_th)],
        [Paragraph("US-SG01 — Cadastro de Usuário", style_td_bold), Paragraph("3", style_td_center), Paragraph("Sprint 1 (Fundação)", style_td), Paragraph("Validação de campos obrigatórios, unicidade de e-mail e hash PBKDF2.", style_td)],
        [Paragraph("US-SG02 — Login e Sessão", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 1 (Fundação)", style_td), Paragraph("Mecanismo central de segurança, proteção contra brute force e controle de sessão.", style_td)],
        [Paragraph("US-SG03 — Logout Seguro", style_td_bold), Paragraph("2", style_td_center), Paragraph("Sprint 1 (Fundação)", style_td), Paragraph("Invalidação atômica de sessão e redirecionamento obrigatório para login.", style_td)],
        [Paragraph("US-SG04 — Agenda Mensal (Visualização)", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 1 (Fundação)", style_td), Paragraph("Cálculo de matriz de calendário, virada de mês e layout responsivo Tailwind.", style_td)],
        [Paragraph("US-SG05 — Criação de Evento Acadêmico", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 2 (Núcleo MVP)", style_td), Paragraph("Modal interativo, validação de datas, endpoint POST /api/events e inserção SQLite.", style_td)],
        [Paragraph("US-SG06 — Edição de Compromisso", style_td_bold), Paragraph("3", style_td_center), Paragraph("Sprint 2 (Núcleo MVP)", style_td), Paragraph("Carregamento prévio de dados, endpoint PUT e atualização atômica de campos.", style_td)],
        [Paragraph("US-SG07 — Exclusão de Evento", style_td_bold), Paragraph("2", style_td_center), Paragraph("Sprint 2 (Núcleo MVP)", style_td), Paragraph("Confirmação em diálogo, endpoint DELETE e remoção física do registro.", style_td)],
        [Paragraph("US-SG08 — Categorização e Cores Oficiais", style_td_bold), Paragraph("3", style_td_center), Paragraph("Sprint 2 (Núcleo MVP)", style_td), Paragraph("Paleta oficial por modalidade (prova, aula, trabalho, entrega) e estilização de badges.", style_td)],
        [Paragraph("US-SG09 — Lembretes Antecipados", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 2 (Núcleo MVP)", style_td), Paragraph("Tratamento de offsets temporais (1h, 1d, 2d, 1w), persistência e sinalização visual.", style_td)],
        [Paragraph("US-SG10 — Google Calendar & Exportação ICS", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 3 (Integração)", style_td), Paragraph("Formatação de URLs web da Google Calendar API e montagem de arquivo RFC 5545.", style_td)],
        [Paragraph("US-SG11 — Visão Semanal e Diária", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 3 (Integração)", style_td), Paragraph("Algoritmo de cálculo de slots de 7 dias e visualização horária detalhada.", style_td)],
        [Paragraph("US-SG12 — Pesquisa e Filtros Dinâmicos", style_td_bold), Paragraph("3", style_td_center), Paragraph("Sprint 3 (Integração)", style_td), Paragraph("Filtragem no cliente via JavaScript sobre a matriz de eventos carregados.", style_td)],
        [Paragraph("US-SG14 — Upload e Gestão de Anexos", style_td_bold), Paragraph("5", style_td_center), Paragraph("Sprint 3 (Integração)", style_td), Paragraph("Upload multipart/form-data, storage seguro com nomes únicos e isolamento por usuário.", style_td)],
        [Paragraph("US-SG15 — Dashboard de Métricas & LGPD", style_td_bold), Paragraph("3", style_td_center), Paragraph("Sprint 3 (Integração)", style_td), Paragraph("Agregações SQL, cards estatísticos, exportação de dados (Art. 18 V) e expurgo de conta.", style_td)]
    ]

    t_fibo = Table(fibo_data, colWidths=[160, 36, 115, 204])
    t_fibo.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 1.8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_fibo)
    story.append(Spacer(1, 3))

    story.append(Paragraph(
        "<b>Balanço de Capacidade da Equipe:</b> Total estimado do Backlog essencial: <b>54 pontos</b>. Sprint 1 realizada: <b>15 pontos</b> (100% entregue). Sprint 2 realizada: <b>18 pontos</b> (100% entregue). Sprint 3 planejada: <b>21 pontos</b>. A velocidade média estável de 16,5 a 18 pontos por ciclo confirma a viabilidade plena das entregas no semestre letivo.",
        style_body
    ))

    # ==================== PÁGINA 3: PRODUCT BACKLOG E SPRINT BACKLOG 2 ====================
    story.append(PageBreak())

    story.append(Paragraph("3. Product Backlog Consolidado e Rastreamento de Status", style_h1))
    story.append(Paragraph(
        "O Product Backlog consolidado organiza todas as necessidades do SIGOA em épicos rastreáveis, indicando as histórias concluídas na Sprint 1, entregues na Sprint 2 (Núcleo do MVP) e planejadas para a Sprint 3:",
        style_body
    ))

    backlog_data = [
        [
            Paragraph("<b>ID</b>", style_th_center),
            Paragraph("<b>Épico / História de Usuário</b>", style_th),
            Paragraph("<b>Prio.</b>", style_th_center),
            Paragraph("<b>Critério de Aceitação Principal</b>", style_th),
            Paragraph("<b>Sprint</b>", style_th_center),
            Paragraph("<b>Status</b>", style_th_center)
        ],
        [
            Paragraph("US-SG01", style_td_center),
            Paragraph("<b>Cadastro:</b> Criar conta com nome, e-mail e senha segura.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Validação de e-mail único, hash PBKDF2 e inserção no SQLite.", style_td),
            Paragraph("Sprint 1", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG02", style_td_center),
            Paragraph("<b>Login:</b> Autenticar credenciais para acessar a agenda.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Verificação de hash, sessão segura e bloqueio de acessos inválidos.", style_td),
            Paragraph("Sprint 1", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG03", style_td_center),
            Paragraph("<b>Logout:</b> Encerrar a sessão para impedir acessos indevidos.", style_td),
            Paragraph("P1", style_td_center),
            Paragraph("Invalidação da sessão HTTP e redirecionamento para /login.", style_td),
            Paragraph("Sprint 1", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG04", style_td_center),
            Paragraph("<b>Agenda Mensal:</b> Consultar calendário com compromissos.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Renderização matricial do mês atual com navegação anterior/próximo.", style_td),
            Paragraph("Sprint 1", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG05", style_td_center),
            Paragraph("<b>Criar Evento:</b> Cadastrar provas, aulas, trabalhos e seminários.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Modal com título, data, horários, tipo e descrição persistidos no SQLite.", style_td),
            Paragraph("Sprint 2", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG06", style_td_center),
            Paragraph("<b>Editar Evento:</b> Alterar dados de eventos cadastrados.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Carregamento prévio no modal e atualização atômica via PUT.", style_td),
            Paragraph("Sprint 2", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG07", style_td_center),
            Paragraph("<b>Excluir Evento:</b> Remover compromissos desnecessários.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Confirmação de exclusão, remoção física via DELETE e atualização visual.", style_td),
            Paragraph("Sprint 2", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG08", style_td_center),
            Paragraph("<b>Categorização:</b> Identificar tipos de atividades por cores.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Pílulas coloridas: prova (vermelho), aula (azul), trabalho (roxo), entrega (verde).", style_td),
            Paragraph("Sprint 2", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG09", style_td_center),
            Paragraph("<b>Lembretes:</b> Definir alertas antecipados de prazos.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Parametrização (1h, 1d, 2d, 1w) gravada no evento e destacada com sino.", style_td),
            Paragraph("Sprint 2", style_td_center),
            Paragraph("<font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG10", style_td_center),
            Paragraph("<b>Google & ICS:</b> Sincronizar com Google Agenda e iCalendar.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Geração de URL direta do Google Calendar e download .ics RFC 5545.", style_td),
            Paragraph("Sprint 3", style_td_center),
            Paragraph("<font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG11", style_td_center),
            Paragraph("<b>Visão Semanal:</b> Visualizar agenda em detalhe de horas.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Alternância entre mês, semana e dia com horários de início e término.", style_td),
            Paragraph("Sprint 3", style_td_center),
            Paragraph("<font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG12", style_td_center),
            Paragraph("<b>Pesquisa:</b> Filtrar compromissos por disciplina ou tipo.", style_td),
            Paragraph("P1", style_td_center),
            Paragraph("Busca dinâmica no cliente sem recarregamento da tela.", style_td),
            Paragraph("Sprint 3", style_td_center),
            Paragraph("<font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG14", style_td_center),
            Paragraph("<b>Gestão de Anexos:</b> Fazer upload de slides e PDFs nos eventos.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("Upload multipart em uploads/ e download direto autenticado.", style_td),
            Paragraph("Sprint 3", style_td_center),
            Paragraph("<font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG15", style_td_center),
            Paragraph("<b>Dashboard & LGPD:</b> Métricas acadêmicas e direitos LGPD.", style_td),
            Paragraph("P1", style_td_center),
            Paragraph("Cards com contadores e rotas de exportação/eliminação total de conta.", style_td),
            Paragraph("Sprint 3", style_td_center),
            Paragraph("<font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ]
    ]

    t_backlog = Table(backlog_data, colWidths=[38, 142, 30, 185, 48, 72])
    t_backlog.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 1.8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_backlog)
    story.append(Spacer(1, 4))

    story.append(Paragraph("5. Sprint Planning — Sprint 2 (Núcleo do MVP)", style_h1))
    story.append(Paragraph(
        "<b>Meta da Sprint 2:</b> Disponibilizar de ponta a ponta o Núcleo Operacional do MVP do SIGOA, permitindo ao estudante criar, visualizar, editar, excluir e categorizar compromissos acadêmicos com lembretes na agenda mensal interativa, com persistência relacional consistente e qualidade assegurada por testes automatizados.",
        style_body
    ))

    tarefas_data = [
        [Paragraph("<b>História / Área</b>", style_th), Paragraph("<b>Tarefa Técnica</b>", style_th), Paragraph("<b>Responsável Técnico</b>", style_th), Paragraph("<b>Status</b>", style_th_center)],
        [Paragraph("US-SG05 / Backend", style_td_bold), Paragraph("Criar rota POST /api/events com validação de campos obrigatórios e sanitização.", style_td), Paragraph("Yuri Milani", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG05 / Frontend", style_td_bold), Paragraph("Desenvolver modal responsivo de cadastro de eventos com formulário dinâmico.", style_td), Paragraph("Emanuel Faria", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG06 / Backend", style_td_bold), Paragraph("Criar rota PUT/POST /api/events/&lt;id&gt; com checagem de propriedade do usuário.", style_td), Paragraph("Yuri Milani", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG06 / Frontend", style_td_bold), Paragraph("Implementar preenchimento prévio do formulário ao clicar no evento da agenda.", style_td), Paragraph("Emanuel Faria", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG07 / Backend", style_td_bold), Paragraph("Criar rota DELETE /api/events/&lt;id&gt; com exclusão física no SQLite3.", style_td), Paragraph("Yuri Milani", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG07 / Frontend", style_td_bold), Paragraph("Adicionar diálogo de confirmação visual antes de confirmar a exclusão.", style_td), Paragraph("Emanuel Faria", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG08 / UI-UX", style_td_bold), Paragraph("Mapear paleta de cores oficial (vermelho, azul, roxo, verde) e aplicar badges.", style_td), Paragraph("Emanuel Faria", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("US-SG09 / Banco", style_td_bold), Paragraph("Definir campo reminder_type na tabela events e tratar opções (1h, 1d, 2d, 1w).", style_td), Paragraph("Yuri Milani", style_td), Paragraph("Concluído", style_td_center)],
        [Paragraph("Qualidade / Testes", style_td_bold), Paragraph("Escrever testes unitários em test_app.py cobrindo todo o ciclo de CRUD de eventos.", style_td), Paragraph("Yuri Milani", style_td), Paragraph("Concluído", style_td_center)]
    ]

    t_tarefas = Table(tarefas_data, colWidths=[95, 235, 110, 75])
    t_tarefas.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_tarefas)

    # ==================== PÁGINA 4: SPRINT 2 - DESENVOLVIMENTO DO NÚCLEO DO PRODUTO ====================
    story.append(PageBreak())

    story.append(Paragraph("6. SPRINT 2 — NÚCLEO DO MVP", style_h1))
    story.append(Paragraph("Sprint 2: Desenvolvimento do Núcleo do Produto", style_h2))
    story.append(Paragraph(
        "O desenvolvimento da Sprint 2 materializou as funcionalidades mais críticas para o sucesso do SIGOA como ferramenta de apoio ao estudante universitário. Esta seção documenta a implementação prática das histórias prioritárias, a integração harmoniosa entre interface, lógica e dados, a estratégia de desenvolvimento incremental e o acompanhamento rigoroso da qualidade.",
        style_body
    ))

    story.append(Paragraph("6.1. Implementação das Funcionalidades Prioritárias", style_h3))
    story.append(Paragraph(
        "• <b>US-SG05 — Criação de Eventos Acadêmicos:</b> O estudante aciona o botão '+ Novo Compromisso' na interface ou clica diretamente em um dia específico do calendário. O modal dinâmico captura título (obrigatório), data do compromisso (obrigatória), tipo de atividade, horários de início e término, cor de identificação, disciplina e observações complementares. Ao submeter, o cliente dispara requisição POST assíncrona para <code>/api/events</code>, os dados são validados no backend e persistidos na base relacional.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>US-SG06 — Edição e Atualização de Compromissos:</b> Ao clicar sobre qualquer compromisso existente na grade do calendário, o sistema efetua uma busca imediata (<code>GET /api/events/&lt;id&gt;</code>) e preenche o formulário do modal com os valores vigentes. O usuário pode alterar data, transferir horários, reclassificar o tipo de atividade ou marcar o evento como concluído. A submissão via <code>PUT /api/events/&lt;id&gt;</code> executa uma atualização atômica no banco, refletindo na interface sem necessidade de reload.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>US-SG07 — Exclusão de Eventos com Confirmação:</b> Para prevenir remoções acidentais de registros acadêmicos vitais, a ação de exclusão exige confirmação explícita do usuário em caixa de diálogo. Confirmada a operação, uma chamada <code>DELETE /api/events/&lt;id&gt;</code> remove o registro fisicamente no SQLite e o elemento correspondente é removido do DOM em tempo real.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>US-SG08 — Categorização Visual Oficial:</b> Para proporcionar reconhecimento visual instantâneo pelo estudante no painel da agenda, foi implementada uma convenção cromática padronizada: <b>Provas</b> (vermelho <code>#dc2626</code>), <b>Aulas</b> (azul <code>#2563eb</code>), <b>Trabalhos</b> (roxo <code>#9333ea</code>), <b>Entregas</b> (verde <code>#16a34a</code>) e <b>Outros</b> (âmbar <code>#f59e0b</code>).",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>US-SG09 — Parametrização de Lembretes:</b> Cada compromisso permite configurar um horizonte temporal de alerta: sem lembrete (<code>none</code>), 1 hora antes (<code>1h</code>), 1 dia antes (<code>1d</code>), 2 dias antes (<code>2d</code>) ou 1 semana antes (<code>1w</code>), gravado na coluna <code>reminder_type</code> e exibido com ícone de sino indicador.",
        style_bullet
    ))

    story.append(Paragraph("6.2. Integração entre Interface, Lógica e Dados", style_h3))
    story.append(Paragraph(
        "A harmonia entre as camadas da solução foi viabilizada pelo seguinte ciclo de integração contínua:",
        style_body
    ))
    story.append(Paragraph(
        "1. <b>Interface do Usuário (Jinja2 / Tailwind CSS):</b> Componentes de tela declarativos e semânticos que respondem imediatamente às ações do estudante, exibindo modais com transições suaves e pílulas de identificação coloridas.",
        style_bullet
    ))
    story.append(Paragraph(
        "2. <b>Lógica do Cliente (Vanilla JS / Fetch API):</b> O arquivo <code>app.js</code> intercepta eventos de clique e submissões de formulário, formata payloads JSON padronizados, despacha chamadas assíncronas e renderiza o resultado sem recarregamento da página (comportamento SPA-like).",
        style_bullet
    ))
    story.append(Paragraph(
        "3. <b>Controladores de Negócio (Flask / app.py):</b> As rotas RESTful validam a autenticação do usuário na sessão (<code>session['user_id']</code>), sanitizam dados de entrada, aplicam regras de consistência temporal e delegam a persistência para o módulo de dados.",
        style_bullet
    ))
    story.append(Paragraph(
        "4. <b>Camada de Persistência (SQLite3 / database.py):</b> Consultas SQL parametrizadas garantem execução segura com integridade relacional, isolando estritamente os compromissos de cada estudante.",
        style_bullet
    ))

    story.append(Paragraph("6.3. Desenvolvimento Incremental do MVP", style_h3))
    story.append(Paragraph(
        "O projeto seguiu a filosofia ágil de construção incremental: na Sprint 1, o estudante apenas navegava pela grade vazia de um mês após logar; na Sprint 2, esse mesmo estudante passou a cadastrar dinamicamente sua rotina, visualizar pílulas coloridas nas datas exatas, atualizar prazos e gerenciar o ciclo de vida completo de seus compromissos. O software manteve-se executável e estável a cada commit.",
        style_body
    ))

    story.append(Paragraph("6.4. Acompanhamento da Qualidade e Testes Automatizados", style_h3))
    story.append(Paragraph(
        "A qualidade foi acompanhada de maneira contínua através da suíte de testes unitários desenvolvida em <code>test_app.py</code> utilizando o framework <code>unittest</code>. O teste específico <code>test_events_crud_and_google_url</code> valida em isolamento:",
        style_body
    ))
    story.append(Paragraph("• Criação bem-sucedida de evento de Prova retornando código HTTP 201 Created e ID gerado.", style_bullet))
    story.append(Paragraph("• Consulta e listagem contendo o evento recém-criado na coleção do usuário logado (código 200 OK).", style_bullet))
    story.append(Paragraph("• Atualização de campos de data, título e conclusão persistidos com integridade (código 200 OK).", style_bullet))
    story.append(Paragraph("• Exclusão física com remoção do banco e retorno de status 200 OK.", style_bullet))
    story.append(Paragraph("• Cobertura estrita de isolamento multiusuário (um usuário não tem acesso aos eventos do outro).", style_bullet))
    story.append(Paragraph(
        "<b>Resultado da Execução:</b> 100% de aprovação (6 suites de testes executadas em 0.235s com zero falhas).",
        style_body
    ))

    # ==================== PÁGINA 5: SPRINT 2 - DESENVOLVIMENTO E INTEGRAÇÃO DO SISTEMA ====================
    story.append(PageBreak())

    story.append(Paragraph("Sprint 2: Desenvolvimento e Integração do Sistema", style_h1))
    story.append(Paragraph(
        "Esta seção detalha os aspectos técnicos da continuidade do desenvolvimento, a integração entre componentes de software, as APIs RESTful construídas, os mecanismos de persistência relacional, a arquitetura de tratamento de erros e a revisão analítica das histórias implementadas.",
        style_body
    ))

    story.append(Paragraph("7.1. Continuidade do Desenvolvimento e Evolução Arquitetural", style_h2))
    story.append(Paragraph(
        "A Sprint 2 manteve perfeita compatibilidade com a fundação estabelecida na Sprint 1. O código-fonte permaneceu modularizado em <code>app.py</code> (controladores e rotas), <code>database.py</code> (operações com a base SQLite3), <code>templates/</code> (layouts Jinja2) e <code>static/js/app.js</code> (dinâmica cliente). A base de dados preservou o schema da tabela <code>users</code> e adicionou a tabela <code>events</code> com integridade referencial.",
        style_body
    ))

    story.append(Paragraph("7.2. Integração de Componentes do Sistema", style_h2))
    story.append(Paragraph(
        "A integração consolidou uma arquitetura desacoplada: a interface web consome a API através de requisições Fetch assíncronas utilizando payloads JSON padronizados. Quando o usuário executa qualquer operação na agenda, o backend processa a solicitação e retorna o registro manipulado em JSON, permitindo que a interface atualize a grade do calendário sem provocar recarregamento de página.",
        style_body
    ))

    story.append(Paragraph("7.3. Especificação dos Contratos das APIs RESTful", style_h2))
    story.append(Paragraph(
        "A tabela a seguir documenta formalmente os endpoints REST implementados e consolidados na Sprint 2:",
        style_body
    ))

    api_data = [
        [
            Paragraph("<b>Método</b>", style_th_center),
            Paragraph("<b>Endpoint</b>", style_th),
            Paragraph("<b>Payload / Parâmetros</b>", style_th),
            Paragraph("<b>Status Code</b>", style_th_center),
            Paragraph("<b>Descrição Operacional</b>", style_th)
        ],
        [
            Paragraph("GET", style_td_center),
            Paragraph("/api/events", style_td_bold),
            Paragraph("start_date, end_date (query strings opcionais)", style_td),
            Paragraph("200 OK<br/>401 Unauth", style_td_center),
            Paragraph("Retorna a lista ordenada de eventos do usuário logado no intervalo consultado.", style_td)
        ],
        [
            Paragraph("POST", style_td_center),
            Paragraph("/api/events", style_td_bold),
            Paragraph("JSON: {title, event_date, event_type, discipline, start_time, end_time, reminder_type}", style_td),
            Paragraph("201 Created<br/>400 Bad Req", style_td_center),
            Paragraph("Valida e cadastra novo compromisso acadêmico vinculado ao user_id da sessão.", style_td)
        ],
        [
            Paragraph("GET", style_td_center),
            Paragraph("/api/events/&lt;id&gt;", style_td_bold),
            Paragraph("id (parâmetro de rota inteiro)", style_td),
            Paragraph("200 OK<br/>404 Not Found", style_td_center),
            Paragraph("Obtém os detalhes completos de um evento específico pertencente ao usuário.", style_td)
        ],
        [
            Paragraph("PUT / POST", style_td_center),
            Paragraph("/api/events/&lt;id&gt;", style_td_bold),
            Paragraph("JSON: {title, event_date, event_type, discipline, reminder_type, is_completed}", style_td),
            Paragraph("200 OK<br/>404 Not Found", style_td_center),
            Paragraph("Atualiza atomicamente os dados do evento especificado na base de dados.", style_td)
        ],
        [
            Paragraph("DELETE", style_td_center),
            Paragraph("/api/events/&lt;id&gt;", style_td_bold),
            Paragraph("id (parâmetro de rota inteiro)", style_td),
            Paragraph("200 OK<br/>404 Not Found", style_td_center),
            Paragraph("Remove permanentemente o compromisso do banco de dados relacional.", style_td)
        ],
        [
            Paragraph("GET", style_td_center),
            Paragraph("/api/stats", style_td_bold),
            Paragraph("Nenhum (usa user_id da sessão)", style_td),
            Paragraph("200 OK<br/>401 Unauth", style_td_center),
            Paragraph("Gera contadores dinâmicos de provas e trabalhos pendentes para o painel.", style_td)
        ]
    ]

    t_api = Table(api_data, colWidths=[45, 95, 155, 65, 155])
    t_api.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_api)
    story.append(Spacer(1, 4))

    story.append(Paragraph("7.4. Persistência de Dados e Integridade Relacional", style_h2))
    story.append(Paragraph(
        "A integridade dos dados na base relacional SQLite3 (<code>academico.db</code>) é assegurada pela diretiva <code>PRAGMA foreign_keys = ON</code> executada em todas as conexões abertas pela função <code>get_db_connection()</code>. A tabela de eventos foi modelada conforme o schema DDL:",
        style_body
    ))
    story.append(Paragraph(
        "<code>CREATE TABLE events (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT, discipline TEXT, event_type TEXT NOT NULL DEFAULT 'aula', color TEXT NOT NULL DEFAULT '#2563eb', event_date TEXT NOT NULL, start_time TEXT, end_time TEXT, reminder_type TEXT DEFAULT 'none', is_completed INTEGER DEFAULT 0, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE);</code>",
        style_bullet
    ))
    story.append(Paragraph(
        "A cláusula <code>ON DELETE CASCADE</code> garante que, caso um estudante exerça seu direito de eliminação de conta, todos os seus compromissos sejam expurgados automaticamente, eliminando registros órfãos.",
        style_body
    ))

    story.append(Paragraph("7.5. Tratamento de Erros, Exceções e Resiliência", style_h2))
    story.append(Paragraph(
        "Para conferir robustez à aplicação contra entradas maliciosas ou falhas de conectividade, foram implementadas defesas em múltiplas camadas:",
        style_body
    ))
    story.append(Paragraph("• <b>Validação de Payloads:</b> Requisições de cadastro ou edição sem título ou sem data são rejeitadas imediatamente no backend com código HTTP 400 Bad Request e mensagem clara em JSON.", style_bullet))
    story.append(Paragraph("• <b>Proteção de Acesso Cruzado:</b> Todas as consultas e operações DML incluem a cláusula <code>WHERE id = ? AND user_id = ?</code>. Caso um usuário autenticado tente editar ou excluir o evento de outro, o servidor retorna 404 Not Found, impedindo vazamento de dados.", style_bullet))
    story.append(Paragraph("• <b>Feedback Visual Resiliente (Toasts):</b> A função <code>showToast()</code> no JavaScript intercepta retornos de erro da API e exibe notificações flutuantes na cor vermelha caso ocorra falha de rede ou validação, ou na cor verde em caso de sucesso.", style_bullet))

    story.append(Paragraph("7.6. Revisão das Histórias Implementadas vs. Critérios de Aceitação", style_h2))
    story.append(Paragraph(
        "Todas as histórias do escopo da Sprint 2 (US-SG05, US-SG06, US-SG07, US-SG08 e US-SG09) foram submetidas à rigorosa conferência dos critérios de aceitação definidos no Product Backlog. Nenhuma inconformidade funcional foi identificada, habilitando a equipe para a etapa formal de Sprint Review.",
        style_body
    ))

    # ==================== PÁGINA 6: SPRINT REVIEW 2 E RETROSPECTIVA ====================
    story.append(PageBreak())

    story.append(Paragraph("Sprint Review 2 e Retrospectiva", style_h1))
    story.append(Paragraph(
        "A Sprint Review 2 e a Retrospectiva da Equipe constituem marcos fundamentais da metodologia ágil Scrum, nos quais o incremento de software é demonstrado de forma executável, os critérios de aceitação são homologados, os resultados métricos são avaliados e o processo de desenvolvimento é continuamente aprimorado.",
        style_body
    ))

    story.append(Paragraph("8.1. Demonstração do Incremento Funcional", style_h2))
    story.append(Paragraph(
        "Durante a sessão de revisão, a equipe realizou a demonstração completa do fluxo de ponta a ponta em ambiente local ativo:",
        style_body
    ))
    story.append(Paragraph("1. <b>Autenticação e Acesso:</b> Login do estudante 'Yuri Dev' no sistema através de sessão segura.", style_bullet))
    story.append(Paragraph("2. <b>Abertura da Grade Mensal:</b> Apresentação da grade de dias com cálculo correto do mês de vigência e posicionamento temporal.", style_bullet))
    story.append(Paragraph("3. <b>Cadastro de Prova Acadêmica:</b> Abertura do modal, preenchimento de 'Prova de Engenharia de Software', tipo 'prova' (vermelho), horário das 08h00 às 10h00 e lembrete '1d'. Submissão e exibição imediata do badge na data.", style_bullet))
    story.append(Paragraph("4. <b>Edição Dinâmica:</b> Clique sobre o compromisso cadastrado, alteração do título para 'Prova Substitutiva' e prorrogação do horário. Persistência e atualização instantânea do card.", style_bullet))
    story.append(Paragraph("5. <b>Exclusão com Diálogo de Segurança:</b> Acionamento do botão 'Excluir', confirmação no diálogo e remoção do evento do calendário e do banco de dados relacional.", style_bullet))
    story.append(Paragraph("6. <b>Isolamento Multiusuário:</b> Login com outro usuário em janela anônima e comprovação de que os eventos do primeiro usuário permanecem estritamente isolados.", style_bullet))

    story.append(Paragraph("8.2. Validação das Funcionalidades e Critérios de Aceitação", style_h2))
    
    val_data = [
        [Paragraph("<b>História</b>", style_th_center), Paragraph("<b>Funcionalidade Avaliada</b>", style_th), Paragraph("<b>Critério de Aceitação Homologado</b>", style_th), Paragraph("<b>Resultado Observado</b>", style_th), Paragraph("<b>Parecer</b>", style_th_center)],
        [
            Paragraph("US-SG05", style_td_center),
            Paragraph("Criar Evento", style_td_bold),
            Paragraph("Título e data obrigatórios; evento associado ao user_id e persistido no SQLite.", style_td),
            Paragraph("Evento cadastrado com sucesso via POST e renderizado imediatamente.", style_td),
            Paragraph("<font color='#059669'><b>Aprovado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG06", style_td_center),
            Paragraph("Editar Evento", style_td_bold),
            Paragraph("Carregar dados no modal; persistir alterações válidas sem reload.", style_td),
            Paragraph("Formulário pré-preenchido e atualização atômica via PUT com 100% de sucesso.", style_td),
            Paragraph("<font color='#059669'><b>Aprovado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG07", style_td_center),
            Paragraph("Excluir Evento", style_td_bold),
            Paragraph("Exigir confirmação; remover registro do banco e do calendário.", style_td),
            Paragraph("Evento excluído com segurança e retirado da grade visual.", style_td),
            Paragraph("<font color='#059669'><b>Aprovado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG08", style_td_center),
            Paragraph("Categorização Visual", style_td_bold),
            Paragraph("Diferenciar visualmente por cores (aulas, provas, trabalhos, entregas).", style_td),
            Paragraph("Badges renderizadas com paleta oficial do Design Sprint.", style_td),
            Paragraph("<font color='#059669'><b>Aprovado</b></font>", style_td_center)
        ],
        [
            Paragraph("US-SG09", style_td_center),
            Paragraph("Lembretes", style_td_bold),
            Paragraph("Associar lembrete parametrizado (1h, 1d, 2d, 1w) ao compromisso.", style_td),
            Paragraph("Opções salvas no banco e sinalizadas com ícone indicador.", style_td),
            Paragraph("<font color='#059669'><b>Aprovado</b></font>", style_td_center)
        ]
    ]

    t_val = Table(val_data, colWidths=[48, 85, 155, 155, 72])
    t_val.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_val)
    story.append(Spacer(1, 4))

    story.append(Paragraph("8.3. Análise dos Resultados: Planejado × Realizado", style_h2))
    story.append(Paragraph(
        "A Sprint 2 atingiu <b>100% de precisão de entrega</b>: todos os 18 Story Points planejados foram implementados, testados e validados com sucesso. Somando com os 15 pontos da Sprint 1, o SIGOA acumula <b>33 Story Points de MVP plenamente operacionais</b>, consolidando o núcleo funcional prometido no plano de ação inicial.",
        style_body
    ))

    story.append(Paragraph("8.4. Feedback Obtido dos Usuários e Alinhamento Acadêmico", style_h2))
    story.append(Paragraph(
        "Durante a validação com estudantes e simulação de rotina acadêmica, foram destacados os seguintes pontos de feedback: <i>'A facilidade de visualizar provas em vermelho e aulas em azul reduz drasticamente o esforço cognitivo'</i>; <i>'A velocidade de abrir o modal e salvar sem a página recarregar passa uma sensação profissional comparável ao Google Agenda'</i>. Como oportunidade sugerida pelos usuários: <i>'Seria excelente ter visão semanal para ver o horário das aulas ao longo do dia e poder anexar o arquivo do trabalho'</i>.",
        style_body
    ))

    story.append(Paragraph("8.5. Retrospectiva da Equipe (Scrum Retrospective)", style_h2))
    
    retro_data = [
        [Paragraph("<b>Dimensão Analisada</b>", style_th), Paragraph("<b>Registro da Equipe e Aprendizados da Sprint 2</b>", style_th)],
        [
            Paragraph("O que funcionou muito bem (Pontos Fortes)", style_td_bold),
            Paragraph("• Adoção da Fetch API com rotas RESTful limpas no Flask, eliminando a sobrecarga de recarregamento de páginas.<br/>• Padronização antecipada da paleta de cores por categoria, evitando retrabalho no frontend.<br/>• Automação de testes com unittest garantindo refatorações seguras sem regressões no CRUD.", style_td)
        ],
        [
            Paragraph("O que podemos aprimorar (Oportunidades)", style_td_bold),
            Paragraph("• Detalhar os contratos de dados de uploads de arquivos antes de codificar os modais na próxima sprint.<br/>• Aprimorar a formatação de fusos horários locais para que a integração com agendas externas ocorra sem desvios.", style_td)
        ],
        [
            Paragraph("Plano de Ação para a Sprint 3", style_td_bold),
            Paragraph("• Estruturar biblioteca dedicada para formatação iCalendar RFC 5545 e Google Calendar URL.<br/>• Configurar storage seguro com limites estritos de tamanho de arquivo (max 16 MB) e validação de extensões permitidas.", style_td)
        ]
    ]

    t_retro = Table(retro_data, colWidths=[140, 375])
    t_retro.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2.5),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_retro)
    story.append(Spacer(1, 4))

    story.append(Paragraph("8.6. Ajustes no Backlog do Produto", style_h2))
    story.append(Paragraph(
        "Com a conclusão bem-sucedida do Núcleo do MVP na Sprint 2, os épicos de <b>Integração com Google Calendar</b>, <b>Visão Semanal</b>, <b>Gestão de Anexos Acadêmicos</b> e <b>Dashboard com Conformidade LGPD</b> foram promovidos para a Sprint 3, conformando um escopo evolutivo de alto valor agregado para os estudantes.",
        style_body
    ))

    # ==================== PÁGINA 7: SPRINT 3 - INTEGRAÇÃO E EVOLUÇÃO ====================
    story.append(PageBreak())

    story.append(Paragraph("Sprint 3: Integração e Evolução", style_h1))
    story.append(Paragraph("Planejamento da Sprint 3: Integração das Funcionalidades e Evolução do Produto", style_h2))
    story.append(Paragraph(
        "A <b>Sprint 3</b> tem como propósito transformar o SIGOA de uma ferramenta isolada em um <b>ecossistema acadêmico integrado, flexível e evoluído</b>. Nesta etapa, o núcleo do MVP estabelecido na Sprint 2 é potencializado com conectividade a serviços de nuvem consagrados, gestão de arquivos e interfaces especializadas de acompanhamento.",
        style_body
    ))

    story.append(Paragraph("9.1. Objetivo da Sprint 3", style_h3))
    story.append(Paragraph(
        "<b>Meta da Sprint 3:</b> Integrar o SIGOA com o ecossistema Google (sincronização direta com Google Calendar via URL API e Google Identity Services), disponibilizar exportação universal no formato iCalendar (RFC 5545), implementar repositório local seguro para upload e download de materiais acadêmicos anexados aos eventos, fornecer visualizações detalhadas por semana e dia, disponibilizar filtros rápidos de pesquisa e incorporar painel de métricas acadêmicas com conformidade integral à LGPD.",
        style_body
    ))

    story.append(Paragraph("9.2. Integração das Funcionalidades no Sistema", style_h3))
    story.append(Paragraph(
        "• <b>Sincronização com Google Calendar:</b> Implementação de serviço em <code>google_service.py</code> que constrói URLs canônicas da Google Calendar API (<code>https://calendar.google.com/calendar/render?action=TEMPLATE...</code>). Com um único clique no card do compromisso, o estudante abre o Google Agenda em nova aba com título, descrição, datas, horários e fuso pré-formatados.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Exportação Interoperável iCalendar (RFC 5545):</b> Criação do endpoint <code>/api/events/export/ics</code>, gerando arquivos <code>.ics</code> com especificação VCALENDAR/VEVENT padrão da Internet. Permite importação direta no Microsoft Outlook, Apple Calendar e qualquer cliente compatível.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Gestão e Repositório de Arquivos Acadêmicos:</b> Criação da tabela <code>user_files</code> no SQLite3 e estruturação do diretório <code>uploads/</code>. Estudantes poderão anexar PDFs, slides (PPTX) e documentos (DOCX) diretamente nos eventos, com validação de extensão e download protegido por sessão.",
        style_bullet
    ))

    story.append(Paragraph("9.3. Evolução do Produto", style_h3))
    story.append(Paragraph(
        "• <b>Visão Semanal e Diária:</b> Evolução da interface para além da visualização mensal tradicional. A visão semanal distribuirá os compromissos em colunas de Segunda a Domingo com marcação temporal, essencial para o acompanhamento da rotina horária de aulas universitárias.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Pesquisa e Filtros Rápidos:</b> Barra de busca dinâmica que filtra instantaneamente compromissos na grade por nome da disciplina, palavra-chave ou tipo de atividade, sem latência de rede.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Painel de Métricas Acadêmicas (/api/stats):</b> Cards dinâmicos no topo da interface exibindo contadores de 'Provas Pendentes', 'Trabalhos a Entregar' e 'Total de Materiais Anexados'.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Conformidade Plena com a LGPD:</b> Implementação dos direitos fundamentais do titular previstos na Lei nº 13.709/2018: <b>Direito à Portabilidade (Art. 18, V)</b> via download do arquivo estruturado <code>meus_dados_lgpd.json</code> e <b>Direito ao Esquecimento (Art. 18, VI)</b> com exclusão irreversível da conta e expurgo físico dos arquivos em disco.",
        style_bullet
    ))

    story.append(Paragraph("9.4. Identificação de Dependências Técnicas e Operacionais", style_h2))
    story.append(Paragraph(
        "Para mitigar riscos e assegurar a execução fluida da Sprint 3, a equipe mapeou as seguintes dependências técnicas:",
        style_body
    ))

    dep_data = [
        [Paragraph("<b>Dependência Mapeada</b>", style_th), Paragraph("<b>Natureza / Origem</b>", style_th), Paragraph("<b>Impacto na Solução</b>", style_th), Paragraph("<b>Estratégia de Mitigação / Solução</b>", style_th)],
        [
            Paragraph("Google Calendar & Identity API", style_td_bold),
            Paragraph("Externa (Google Cloud)", style_td),
            Paragraph("Necessidade de credenciais de OAuth 2.0 e conexão com servidores externos.", style_td),
            Paragraph("Implementação de fallback híbrido: sincronização via URL canônica sem autenticação prévia obrigatória e modo de demonstração local caso offline.", style_td)
        ],
        [
            Paragraph("Diretório de Uploads e Permissões", style_td_bold),
            Paragraph("Interna (Sistema de Arquivos)", style_td),
            Paragraph("Risco de arquivos sobrescritos ou falhas de gravação em diretório inexistente.", style_td),
            Paragraph("Geração de nomes com UUID hex e timestamp seguro (user_id_time_uuid.ext); criação automática da pasta uploads/ no startup do Flask.", style_td)
        ],
        [
            Paragraph("Validação de Arquivos e Malware", style_td_bold),
            Paragraph("Segurança / Infraestrutura", style_td),
            Paragraph("Submissão acidental ou maliciosa de executáveis (.exe, .bat, scripts).", style_td),
            Paragraph("Aplicação rigorosa de secure_filename(), whitelist estrita (pdf, doc, docx, ppt, pptx, txt, zip, png, jpg) e limite físico de 16 MB.", style_td)
        ],
        [
            Paragraph("Cálculo Algorítmico de Semanas", style_td_bold),
            Paragraph("Interna (Frontend JS)", style_td),
            Paragraph("Complexidade na virada de ano e semanas que cruzam dois meses.", style_td),
            Paragraph("Função utilitária getWeekStart() em app.js utilizando aritmética UTC padrão de Date do JavaScript.", style_td)
        ],
        [
            Paragraph("Integridade Transacional em Cascata", style_td_bold),
            Paragraph("Interna (Banco SQLite)", style_td),
            Paragraph("Arquivos órfãos no banco caso um evento associado seja removido.", style_td),
            Paragraph("Definição de FOREIGN KEY (event_id) REFERENCES events(id) ON DELETE SET NULL na tabela user_files.", style_td)
        ]
    ]

    t_dep = Table(dep_data, colWidths=[120, 95, 130, 170])
    t_dep.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    story.append(t_dep)

    # ==================== PÁGINA 8: PRIORIZAÇÃO DA SPRINT 3 E DESENVOLVIMENTO DO SISTEMA ====================
    story.append(PageBreak())

    story.append(Paragraph("9.5. Priorização das Próximas Entregas (Sprint 3 Backlog)", style_h2))
    story.append(Paragraph(
        "Aplicando a metodologia MoSCoW combinada com estimativas Fibonacci, as entregas da Sprint 3 foram priorizadas para maximizar o retorno ao usuário no semestre:",
        style_body
    ))

    sprint3_data = [
        [
            Paragraph("<b>ID</b>", style_th_center),
            Paragraph("<b>História de Usuário (Evolução)</b>", style_th),
            Paragraph("<b>Prio.</b>", style_th_center),
            Paragraph("<b>Pts</b>", style_th_center),
            Paragraph("<b>Critério de Aceitação da Sprint 3</b>", style_th),
            Paragraph("<b>Dependência</b>", style_th)
        ],
        [
            Paragraph("US-SG10", style_td_center),
            Paragraph("<b>Google Calendar e iCalendar:</b> Sincronizar eventos acadêmicos com serviços externos de calendário.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("5", style_td_center),
            Paragraph("Geração de link do Google Agenda com clique único e download do arquivo .ics em conformidade com a RFC 5545.", style_td),
            Paragraph("google_service.py", style_td)
        ],
        [
            Paragraph("US-SG11", style_td_center),
            Paragraph("<b>Visão Semanal e Diária:</b> Consultar atividades em visualização detalhada com horários de início e término.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("5", style_td_center),
            Paragraph("Alternância dinâmica entre Mês, Semana e Dia com preservação do estado no localStorage.", style_td),
            Paragraph("app.js / Layout", style_td)
        ],
        [
            Paragraph("US-SG12", style_td_center),
            Paragraph("<b>Pesquisa e Filtros Dinâmicos:</b> Localizar compromissos acadêmicos por texto e categoria em tempo real.", style_td),
            Paragraph("P1", style_td_center),
            Paragraph("3", style_td_center),
            Paragraph("Campo de pesquisa na barra superior filtrando eventos imediatamente sem requisições adicionais.", style_td),
            Paragraph("app.js", style_td)
        ],
        [
            Paragraph("US-SG14", style_td_center),
            Paragraph("<b>Upload e Gestão de Anexos:</b> Fazer upload e download de materiais didáticos atrelados a compromissos.", style_td),
            Paragraph("P0", style_td_center),
            Paragraph("5", style_td_center),
            Paragraph("Formulário multipart/form-data salvando arquivos em uploads/, registro no banco e download autenticado.", style_td),
            Paragraph("uploads/ dir", style_td)
        ],
        [
            Paragraph("US-SG15", style_td_center),
            Paragraph("<b>Dashboard de Métricas & LGPD:</b> Acompanhar contadores de atividades e exercer direitos da LGPD.", style_td),
            Paragraph("P1", style_td_center),
            Paragraph("3", style_td_center),
            Paragraph("Cards com métricas (/api/stats), exportação de dados em JSON (Art. 18 V) e exclusão irreversível de conta (Art. 18 VI).", style_td),
            Paragraph("database.py", style_td)
        ]
    ]

    t_s3 = Table(sprint3_data, colWidths=[40, 155, 30, 28, 182, 80])
    t_s3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_s3)
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>Capacidade Comprometida para a Sprint 3:</b> 21 Story Points distribuídos em 5 histórias de alto impacto.", style_body))

    story.append(Paragraph("Desenvolvimento e Integração do Sistema na Sprint 3", style_h1))
    story.append(Paragraph(
        "A metodologia de desenvolvimento e integração para a Sprint 3 segue as melhores práticas da Engenharia de Software Moderna:",
        style_body
    ))
    story.append(Paragraph(
        "• <b>Padrão de Integração RESTful e Multipart:</b> A rota <code>/api/files/upload</code> e a expansão de <code>/api/events</code> passam a aceitar tanto <code>application/json</code> quanto <code>multipart/form-data</code>, permitindo que a submissão de um evento acadêmico receba simultaneamente o upload de um arquivo complementar em uma única requisição atômica.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Segurança no Armazenamento de Arquivos:</b> Os arquivos físicos recebem nomes sanitizados através de <code>secure_filename()</code> e são prefixados com identificador criptográfico único (<code>user_{user_id}_{timestamp}_{uuid}.ext</code>), eliminando colisões de nomes e prevenindo ataques de Path Traversal.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Isolamento Estrito Multilocatário:</b> Os downloads só são liberados pela rota protegida <code>/api/files/&lt;id&gt;/download</code> após verificar que o <code>user_id</code> da sessão ativa é idêntico ao proprietário gravado no registro.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Interoperabilidade com Padrões Abertos:</b> A geração do arquivo <code>calendario_academico.ics</code> obedece rigorosamente às linhas de quebra CRLF, formatação de timestamps UTC (<code>YYYYMMDDTHHMMSSZ</code>) e tags VCALENDAR da RFC 5545.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Estratégia de Branching e Testes:</b> Cada funcionalidade da Sprint 3 é desenvolvida em branch feature dedicada (<code>feat/google-calendar</code>, <code>feat/file-uploads</code>, <code>feat/week-view</code>), submetida a revisão por pares e validada através de novos testes unitários adicionados em <code>test_app.py</code> antes da integração na branch principal.",
        style_bullet
    ))
    story.append(Paragraph(
        "• <b>Definition of Done (DoD) da Sprint 3:</b> Para ser considerada concluída na Sprint 3, cada história deverá: (1) estar integrada e executando sem erros; (2) possuir cobertura automatizada por testes unitários e de integração; (3) garantir isolamento multiusuário estrito; (4) ser demonstrada com sucesso na Sprint Review 3.",
        style_bullet
    ))

    # ==================== PÁGINA 9: RASTREABILIDADE, DOD E REFERÊNCIAS ====================
    story.append(PageBreak())

    story.append(Paragraph("10. Matriz de Rastreabilidade Técnica Consolidada", style_h1))
    story.append(Paragraph(
        "A matriz a seguir consolida a rastreabilidade vertical entre as decisões do Blueprint Arquitetural, as histórias do Product Backlog, os endpoints RESTful, a implementação em código-fonte e o status de entrega:",
        style_body
    ))

    rastreio_data = [
        [
            Paragraph("<b>Decisão Arquitetural</b>", style_th),
            Paragraph("<b>História / Épico</b>", style_th),
            Paragraph("<b>Endpoint / Protocolo</b>", style_th),
            Paragraph("<b>Módulos no Repositório</b>", style_th),
            Paragraph("<b>Sprint / Status</b>", style_th_center)
        ],
        [
            Paragraph("Web Responsiva (SPA-like)", style_td_bold),
            Paragraph("US-SG04, US-SG11<br/>Visualização da Agenda", style_td),
            Paragraph("GET / (HTML)<br/>Fetch API assíncrono", style_td),
            Paragraph("templates/index.html<br/>static/js/app.js", style_td),
            Paragraph("Sprint 1 e 2<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("Monolito em Camadas (Flask)", style_td_bold),
            Paragraph("Todas as histórias<br/>Controle e Negócio", style_td),
            Paragraph("HTTP/HTTPS REST<br/>JSON / Headers", style_td),
            Paragraph("app.py<br/>config.py", style_td),
            Paragraph("Sprint 1 e 2<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("Sessões Seguras (PBKDF2)", style_td_bold),
            Paragraph("US-SG01, US-SG02, US-SG03<br/>Autenticação e Sessão", style_td),
            Paragraph("POST /login<br/>POST /register", style_td),
            Paragraph("app.py (Werkzeug)<br/>templates/login.html", style_td),
            Paragraph("Sprint 1<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("Banco Relacional ACID", style_td_bold),
            Paragraph("US-SG05, US-SG06, US-SG07<br/>CRUD de Compromissos", style_td),
            Paragraph("GET, POST, PUT, DELETE<br/>/api/events", style_td),
            Paragraph("database.py (SQLite3)<br/>academico.db", style_td),
            Paragraph("Sprint 2<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("Categorização Cromática", style_td_bold),
            Paragraph("US-SG08, US-SG09<br/>Cores e Lembretes", style_td),
            Paragraph("Payload JSON com campos<br/>color e reminder_type", style_td),
            Paragraph("static/js/app.js<br/>templates/index.html", style_td),
            Paragraph("Sprint 2<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ],
        [
            Paragraph("Integração Google e ICS", style_td_bold),
            Paragraph("US-SG10<br/>Calendários Externos", style_td),
            Paragraph("GET /api/events/export/ics<br/>URL Google Calendar", style_td),
            Paragraph("google_service.py<br/>app.py", style_td),
            Paragraph("Sprint 3<br/><font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("Armazenamento Seguro Local", style_td_bold),
            Paragraph("US-SG14<br/>Anexos e Documentos", style_td),
            Paragraph("POST /api/files/upload<br/>GET /api/files/&lt;id&gt;/down", style_td),
            Paragraph("uploads/ dir<br/>database.py (user_files)", style_td),
            Paragraph("Sprint 3<br/><font color='#2563EB'><b>Planejado</b></font>", style_td_center)
        ],
        [
            Paragraph("Garantia da Qualidade", style_td_bold),
            Paragraph("Todas as histórias<br/>Testes de Regressão", style_td),
            Paragraph("Suíte automatizada com<br/>6 baterias completas", style_td),
            Paragraph("test_app.py<br/>test_academico.db", style_td),
            Paragraph("Sprint 1, 2 e 3<br/><font color='#059669'><b>Concluído</b></font>", style_td_center)
        ]
    ]

    t_rastreio = Table(rastreio_data, colWidths=[110, 115, 115, 110, 65])
    t_rastreio.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), c_th_bg),
        ('GRID', (0,0), (-1,-1), 0.5, c_border),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, c_row_alt]),
        ('PADDING', (0,0), (-1,-1), 2),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t_rastreio)
    story.append(Spacer(1, 3))

    story.append(Paragraph("11. Definition of Done (DoD) da Sprint 2", style_h1))
    story.append(Paragraph("Para que as histórias da Sprint 2 fossem declaradas 100% concluídas, foram verificados os seguintes critérios técnicos:", style_body))
    story.append(Paragraph("• <b>Implementação Completa:</b> Todas as funcionalidades da história desenvolvidas e aderentes à arquitetura do Blueprint.", style_bullet))
    story.append(Paragraph("• <b>Execução Local sem Erros:</b> Aplicação executando perfeitamente sem erros bloqueadores no console ou no terminal.", style_bullet))
    story.append(Paragraph("• <b>Persistência ACID:</b> Dados de eventos gravados e atualizados no SQLite com integridade referencial.", style_bullet))
    story.append(Paragraph("• <b>Controle de Segurança:</b> Rotas protegidas exigindo autenticação e bloqueando acesso cruzado entre usuários.", style_bullet))
    story.append(Paragraph("• <b>Cobertura por Testes:</b> Suíte de testes automatizados com 100% de aprovação e sem quebra de testes legados.", style_bullet))
    story.append(Paragraph("• <b>Demonstração Homologada:</b> Incremento funcional validado na Sprint Review com a equipe.", style_bullet))

    story.append(Paragraph("12. Fontes e Referências Utilizadas (ABNT NBR 6023:2018)", style_h1))
    
    referencias = [
        "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. <b>NBR 6023:2018</b>: Informação e documentação: referências: elaboração. Rio de Janeiro: ABNT, 2018.",
        "BRASIL. <b>Lei nº 13.709, de 14 de agosto de 2018</b>. Dispõe sobre a proteção de dados pessoais (Lei Geral de Proteção de Dados Pessoais - LGPD). Diário Oficial da União: seção 1, Brasília, DF, 15 ago. 2018.",
        "DESRUISSEAUX, Bernard (ed.). <b>RFC 5545: Internet Calendaring and Scheduling Core Object Specification (iCalendar)</b>. Reston: Internet Engineering Task Force (IETF), 2009. Disponível em: &lt;https://datatracker.ietf.org/doc/html/rfc5545&gt;. Acesso em: 15 out. 2026.",
        "GOOGLE LLC. <b>Google Calendar API Developer Guide</b>. Mountain View: Google LLC, 2024. Disponível em: &lt;https://developers.google.com/calendar&gt;. Acesso em: 15 out. 2026.",
        "HIPP, D. Richard et al. <b>SQLite Database Engine Documentation</b>. Versão 3.x. Charlotte: SQLite Team, 2024. Disponível em: &lt;https://www.sqlite.org/docs.html&gt;. Acesso em: 15 out. 2026.",
        "KNAPP, Jake; ZERATSKY, John; KOWITZ, Braden. <b>Sprint: como testar novas ideias e resolver grandes problemas em apenas cinco dias</b>. Tradução de Cássio de Arantes Leite. 1. ed. Rio de Janeiro: Intrínseca, 2017.",
        "PALLETS PROJECTS. <b>Flask: a Python microframework</b>. Versão 3.0.x. 2024. Disponível em: &lt;https://flask.palletsprojects.com/&gt;. Acesso em: 15 out. 2026.",
        "PRESSMAN, Roger S.; MAXIM, Bruce R. <b>Engenharia de software: uma abordagem profissional</b>. 8. ed. Porto Alegre: AMGH, 2016.",
        "SCHWABER, Ken; SUTHERLAND, Jeff. <b>The Scrum Guide: the definitive guide to Scrum: the rules of the game</b>. Scrum.org, 2020. Disponível em: &lt;https://scrumguides.org/&gt;. Acesso em: 15 out. 2026.",
        "SOMMERVILLE, Ian. <b>Engenharia de software</b>. 10. ed. São Paulo: Pearson Education do Brasil, 2019.",
        "TAILWIND LABS. <b>Tailwind CSS: a utility-first CSS framework for rapid UI development</b>. Versão 3.4. 2024. Disponível em: &lt;https://tailwindcss.com/docs&gt;. Acesso em: 15 out. 2026.",
        "UNIVERSIDADE DO ESTADO DE MATO GROSSO (UNEMAT). <b>SIGOA: Backlog da Sprint 1 e Blueprint da Arquitetura</b>. Cáceres: Laboratório de Engenharia de Software, 2026."
    ]

    for ref in referencias:
        story.append(Paragraph(ref, style_ref))

    doc.build(story, canvasmaker=NumberedCanvas)
    
    # Cria cópia também com o nome alternativo descritivo
    shutil.copyfile(output_pdf, output_pdf_alt)
    print(f"Sucesso! PDF da Sprint 2 e Planejamento da Sprint 3 gerado em:\n -> {output_pdf}\n -> {output_pdf_alt}")

if __name__ == "__main__":
    gerar_pdf_sprint2_sprint3()
