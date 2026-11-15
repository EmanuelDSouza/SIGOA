# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

def criar_blueprint():
    fig, ax = plt.subplots(figsize=(16, 11), dpi=240)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Fundo geral branco
    fig.patch.set_facecolor('#FFFFFF')
    ax.set_facecolor('#FFFFFF')

    # Tipografia limpa e legível
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Helvetica']

    # ==================== TÍTULO SUPERIOR ====================
    ax.text(50, 96.6, "SIGOA — Blueprint da Arquitetura do Sistema",
            ha='center', va='center', fontsize=20, fontweight='bold', color='#111827')
    ax.text(50, 93.3, "Sistema de Gerenciamento de Organização Acadêmica | UNEMAT",
            ha='center', va='center', fontsize=12.5, color='#4B5563')

    # Função auxiliar para desenhar cards limpos
    def draw_card(x, y, w, h, title, items, border_color, bg_color):
        bbox = FancyBboxPatch((x, y), w, h,
                              boxstyle="round,pad=0.4,rounding_size=1.6",
                              linewidth=1.8, edgecolor=border_color,
                              facecolor=bg_color, zorder=2)
        ax.add_patch(bbox)

        # Cabeçalho do Card
        ax.text(x + 2.5, y + h - 3.2, title,
                fontsize=12.5, fontweight='bold', color=border_color, va='center', zorder=4)

        # Divisória interna elegante
        ax.plot([x + 2, x + w - 2], [y + h - 5.5, y + h - 5.5],
                color=border_color, linewidth=0.8, alpha=0.35, zorder=3)

        # Itens listados com espaçamento proporcional
        n = len(items)
        available_height = h - 7.5
        spacing = available_height / max(n, 1)
        
        for i, item in enumerate(items):
            item_y = (y + h - 7.8) - (i * spacing)
            ax.text(x + 2.8, item_y, "•", fontsize=13, fontweight='bold', color=border_color, va='center', zorder=4)
            ax.text(x + 4.5, item_y, item, fontsize=10.2, color='#1F2937', va='center', zorder=4)

    # 1. CAMADA DE APRESENTAÇÃO (FRONTEND)
    draw_card(
        x=4, y=59.0, w=43.5, h=30.5,
        title="CAMADA DE APRESENTAÇÃO (FRONTEND)",
        items=[
            "Tipo: Aplicação Web Responsiva (Desktop / Mobile)",
            "Templates Jinja2 (HTML5) + Tailwind CSS + CSS3",
            "Vanilla JavaScript ES6+ (app.js assíncrono / Fetch API)",
            "Lucide Icons (Ícones vetoriais modernos)",
            "Visões: Mês, Semana, Dia + Modais CRUD + Notificações"
        ],
        border_color="#2563EB", bg_color="#F8FAFC"
    )

    # 2. SERVIÇOS EXTERNOS & INTEGRAÇÕES
    draw_card(
        x=52.5, y=59.0, w=43.5, h=30.5,
        title="SERVIÇOS EXTERNOS & INTEGRAÇÕES",
        items=[
            "Google Identity Services (OAuth 2.0 Sign-In)",
            "Google Calendar (Sincronização 1-clique via URL API)",
            "Exportador Universal iCalendar (.ics - RFC 5545)",
            "Google Forms (Coleta de Feedback e Validação MVP)",
            "Suporte Apple Calendar, Outlook e Google Agenda"
        ],
        border_color="#D97706", bg_color="#FFFBEB"
    )

    # 3. CAMADA DE APLICAÇÃO & NEGÓCIO (BACKEND REST)
    draw_card(
        x=4, y=29.5, w=92.0, h=21.0,
        title="CAMADA DE APLICAÇÃO & NEGÓCIO (BACKEND REST)",
        items=[
            "Servidor Web: Python 3.10+ com Flask Microframework (app.py)",
            "Segurança & Sessões: Werkzeug Security (PBKDF2/SHA-256 Salted Hashing, Cookies HTTP)",
            "API RESTful: Endpoints JSON (/api/events, /api/files, /api/stats, /auth/google, /auth/forgot-password)",
            "Módulo LGPD: Minimização de dados, Portabilidade JSON (/api/user/export-data), Direito ao Esquecimento"
        ],
        border_color="#7C3AED", bg_color="#FAF5FF"
    )

    # 4. BANCO DE DADOS & ARMAZENAMENTO
    draw_card(
        x=4, y=2.2, w=43.5, h=19.0,
        title="BANCO DE DADOS & ARMAZENAMENTO",
        items=[
            "SGBD: SQLite3 Relacional (academico.db)",
            "Integridade: PRAGMA foreign_keys = ON (Cascade)",
            "Tabelas: users, events, user_files (Isoladas por user_id)",
            "Sistema de Arquivos: Diretório seguro /uploads/"
        ],
        border_color="#059669", bg_color="#F0FDF4"
    )

    # 5. FERRAMENTAS & INTELIGÊNCIAS ARTIFICIAIS
    draw_card(
        x=52.5, y=2.2, w=43.5, h=19.0,
        title="FERRAMENTAS & INTELIGÊNCIAS ARTIFICIAIS",
        items=[
            "IAs Utilizadas: Gemini (Antigravity CLI), Copilot, Claude",
            "Categorias: Gratuitas (Gemini CLI) e Pagas/Student (Copilot)",
            "Prototipação & Design: Figma (Design Sprint)",
            "Garantia de Qualidade: 6 Testes Automatizados (unittest)"
        ],
        border_color="#E11D48", bg_color="#FFF1F2"
    )

    # ==================== CONECTORES COM MÁSCARA LIMPA ====================
    def draw_connector(x_center, y_bottom_pos, y_top_pos, label, color):
        # Seta vertical bidirecional contínua
        arrow = FancyArrowPatch(
            (x_center, y_bottom_pos + 0.3),
            (x_center, y_top_pos - 0.3),
            arrowstyle='<->', mutation_scale=14,
            color=color, linewidth=2.0, zorder=5
        )
        ax.add_patch(arrow)

        # Pílula de texto centralizada com máscara branca garantindo zero sobreposição
        y_mid = (y_bottom_pos + y_top_pos) / 2
        bbox_props = dict(boxstyle="round,pad=0.45,rounding_size=0.8",
                          fc="#FFFFFF", ec=color, lw=1.4, zorder=6)
        
        ax.text(x_center, y_mid, f"  {label}  ",
                ha='center', va='center', fontsize=9.2, fontweight='bold',
                color=color, bbox=bbox_props, zorder=7)

    # Conector 1: Frontend <-> Backend
    draw_connector(
        x_center=25.75,
        y_bottom_pos=50.5,
        y_top_pos=59.0,
        label="HTTP / HTTPS (REST JSON + Multipart Form)",
        color="#2563EB"
    )

    # Conector 2: Serviços Externos <-> Backend
    draw_connector(
        x_center=74.25,
        y_bottom_pos=50.5,
        y_top_pos=59.0,
        label="OAuth 2.0 / Google URL API / RFC 5545 ICS",
        color="#D97706"
    )

    # Conector 3: Backend <-> Banco de Dados
    draw_connector(
        x_center=25.75,
        y_bottom_pos=21.2,
        y_top_pos=29.5,
        label="SQL Queries Parametrizadas / File I/O",
        color="#059669"
    )

    # Conector 4: Backend <-> Ferramentas & IA
    draw_connector(
        x_center=74.25,
        y_bottom_pos=21.2,
        y_top_pos=29.5,
        label="Suporte ao Ciclo de Vida / Pair Programming",
        color="#E11D48"
    )

    plt.tight_layout()
    output_path = "blueprint_arquitetura.png"
    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0.15)
    plt.close()
    print(f"Blueprint reconstruído com perfeição em: {output_path}")

if __name__ == "__main__":
    criar_blueprint()
