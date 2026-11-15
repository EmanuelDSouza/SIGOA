# -*- coding: utf-8 -*-
"""Gera o relatório de validação e qualidade do SIGOA (Fase 4)."""
from pathlib import Path
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                TableStyle, PageBreak, KeepTogether, HRFlowable)
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'Relatorio_Validacao_Qualidade_SIGOA.pdf'
# Use the PDF base fonts to avoid font-substitution and line-metric differences
# between viewers on the recipient's machine.
_FONT_DIR = Path(reportlab.__file__).resolve().parent / 'fonts'
pdfmetrics.registerFont(TTFont('SIGOAVera', str(_FONT_DIR / 'Vera.ttf'))) 
pdfmetrics.registerFont(TTFont('SIGOAVera-Bold', str(_FONT_DIR / 'VeraBd.ttf'))) 
FONT, BOLD = 'SIGOAVera', 'SIGOAVera-Bold'

NAVY = colors.HexColor('#132A43')
BLUE = colors.HexColor('#2457A7')
TEAL = colors.HexColor('#0F8B8D')
PALE = colors.HexColor('#F1F5F9')
INK = colors.HexColor('#243447')
MUTED = colors.HexColor('#5B6B7D')
RED = colors.HexColor('#A93232')
GOLD = colors.HexColor('#986A13')
GREEN = colors.HexColor('#26734D')

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='CoverTitle', fontName=BOLD, fontSize=29, leading=35,
                          textColor=NAVY, alignment=TA_LEFT, spaceAfter=14))
styles.add(ParagraphStyle(name='CoverSub', fontName=FONT, fontSize=12, leading=18,
                          textColor=MUTED, spaceAfter=8))
styles.add(ParagraphStyle(name='H1x', fontName=BOLD, fontSize=17, leading=22,
                          textColor=NAVY, backColor=PALE, borderColor=PALE, borderWidth=0.5,
                          borderPadding=(5, 8, 5, 8), spaceBefore=4, spaceAfter=11, keepWithNext=True))
styles.add(ParagraphStyle(name='H2x', fontName=BOLD, fontSize=11.5, leading=15,
                          textColor=TEAL, spaceBefore=9, spaceAfter=5, keepWithNext=True))
styles.add(ParagraphStyle(name='Bodyx', fontName=FONT, fontSize=9.5, leading=14.5,
                          textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name='Smallx', fontName=FONT, fontSize=8.1, leading=11.3,
                          textColor=INK))
styles.add(ParagraphStyle(name='Tinyx', fontName=FONT, fontSize=7.7, leading=10.7,
                          textColor=INK))
styles.add(ParagraphStyle(name='CellHead', fontName=BOLD, fontSize=8, leading=10.5,
                          textColor=colors.white))
styles.add(ParagraphStyle(name='Callout', fontName=BOLD, fontSize=10, leading=15,
                          textColor=NAVY, backColor=colors.HexColor('#E8F4F4'), borderColor=TEAL,
                          borderWidth=0.7, borderPadding=10, spaceBefore=4, spaceAfter=9))
styles.add(ParagraphStyle(name='CoverMeta', fontName=FONT, fontSize=10, leading=16,
                          textColor=INK))
styles.add(ParagraphStyle(name='StepNumber', fontName=BOLD, fontSize=17, leading=20,
                          textColor=BLUE, alignment=TA_CENTER))

def P(text, style='Bodyx'):
    return Paragraph(text, styles[style])

def table(rows, widths, font='Smallx', header=True, padding=5, aligns=None):
    cooked=[]
    for ri,row in enumerate(rows):
        st='CellHead' if header and ri==0 else font
        cooked.append([P(str(x),st) for x in row])
    t=Table(cooked, colWidths=widths, repeatRows=1 if header else 0, hAlign='LEFT')
    cmds=[('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),padding),
          ('RIGHTPADDING',(0,0),(-1,-1),padding+1),('TOPPADDING',(0,0),(-1,-1),padding+1),
          ('BOTTOMPADDING',(0,0),(-1,-1),padding+1),('BOX',(0,0),(-1,-1),.55,colors.HexColor('#D7DFE8')),
          ('INNERGRID',(0,0),(-1,-1),.25,colors.HexColor('#E0E7EF')),
          ('ROWBACKGROUNDS',(0,1 if header else 0),(-1,-1),[colors.white,PALE])]
    if header: cmds.append(('LINEBELOW',(0,0),(-1,0),1.4,TEAL))
    if header: cmds.append(('BACKGROUND',(0,0),(-1,0),NAVY))
    if aligns:
        for col,align in aligns.items(): cmds.append(('ALIGN',(col,0),(col,-1),align))
    t.setStyle(TableStyle(cmds))
    return t

def step_card(number, title, body):
    t = Table([[P(number, 'StepNumber'), P(f'<b>{title}</b><br/>{body}', 'Bodyx')]],
              colWidths=[15*mm, 155*mm], hAlign='LEFT')
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),PALE),
        ('BOX',(0,0),(-1,-1),.5,colors.HexColor('#D7DFE8')),
        ('LINEBEFORE',(0,0),(0,-1),3,TEAL),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),
        ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ]))
    return KeepTogether([t, Spacer(1,5)])

def footer(c, doc):
    c.saveState()
    w, h = A4
    if doc.page == 1:
        c.setFillColor(NAVY)
        c.rect(0, h - 13*mm, w, 13*mm, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(0, h - 13*mm, 48*mm, 1.8*mm, stroke=0, fill=1)
    else:
        c.setStrokeColor(colors.HexColor('#D8E0E9'))
        c.line(20*mm, h-16*mm, w-20*mm, h-16*mm)
        c.setFont(BOLD, 7.5)
        c.setFillColor(NAVY)
        c.drawString(20*mm, h-12.8*mm, 'SIGOA  |  RELATORIO DE VALIDACAO E QUALIDADE')
    c.setStrokeColor(colors.HexColor('#D8E0E9'))
    c.line(20*mm, 15*mm, w-20*mm, 15*mm)
    c.setFont(FONT, 7.5)
    c.setFillColor(MUTED)
    c.drawString(20*mm, 10*mm, 'UNEMAT  |  Laboratorio de Engenharia de Software  |  2026')
    c.setFillColor(NAVY)
    c.roundRect(w-27*mm, 7.2*mm, 7*mm, 7*mm, 1.5*mm, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.setFont(BOLD, 7.5)
    c.drawCentredString(w-23.5*mm, 9.4*mm, str(doc.page))
    c.restoreState()

story=[]
# Capa
story += [Spacer(1,28*mm), P('FASE 4  •  QUALIDADE E ENTREGA','H2x'),
          HRFlowable(width='100%', thickness=3, color=TEAL, spaceBefore=5, spaceAfter=18),
          P('Relatório de Validação<br/>e Qualidade do Produto','CoverTitle'),
          P('SIGOA — Sistema de Gerenciamento de Organização Acadêmica','CoverSub'),
          Spacer(1,13*mm),
          P('<b>Objetivo</b><br/>Avaliar, com evidências rastreáveis, a qualidade do MVP, os testes executados, os riscos observados e as validações necessárias antes da apresentação.','Callout'),
          Spacer(1,25*mm),
          P('<b>Integrantes</b>  Yuri Sardinha Milani • Emanuel Faria<br/><b>Instituição</b>  Universidade do Estado de Mato Grosso (UNEMAT)<br/><b>Disciplina</b>  Laboratório de Engenharia de Software<br/><b>Data da avaliação</b>  12 de novembro de 2026','CoverMeta'),
          Spacer(1,22*mm), P('Documento preparado para apresentação e defesa do MVP.','CoverSub'), PageBreak()]

# Sumário executivo
story += [P('1. Síntese da avaliação','H1x'),
 P('O SIGOA inclui cadastro e autenticacao, agenda academica, CRUD de compromissos, anexos, exportacao de calendario, portabilidade e exclusao de dados. A importacao de aulas por PDF esta implementada, mas o parser e o fluxo completo ainda precisam de testes. A redefinicao de senha permanece como achado aberto (D-01). Esta avaliacao combina leitura do enunciado do Trabalho Final, inspecao do codigo e resultados registrados da suite automatizada existente.'),
 P('Resultado atualizado: os oito testes automatizados passaram. Quatro achados foram corrigidos; D-01 (redefinicao de senha) permanece aberto. D-02 e D-05 receberam reteste automatizado, e D-03/D-04 foram conferidos por inspecao de codigo. Isso nao demonstra usabilidade com estudantes nem substitui teste real de SMTP, OAuth ou navegador.'),
 table([['Indicador','Resultado observado'],
        ['Testes automatizados','8 executados • 8 aprovados • 0 falhas • 0 erros'],
        ['Cobertura qualitativa','Cadastro, senha minima, CRUD, lembretes, anexos, isolamento, Demo, teste isolado de token com e-mail simulado e LGPD'],
        ['Testes de usabilidade','Não há evidência de sessão com usuários reais'],
        ['Defeitos/riscos registrados nesta analise','4 achados corrigidos; D-01 (redefinicao de senha) continua aberto'],
        ['Parecer do MVP','Demonstravel com ressalvas; redefinicao de senha, SMTP real, OAuth real, navegador e usabilidade ainda exigem validacao']], [45*mm,125*mm]),
 P('Escopo e fontes','H2x'),
 P('O PDF “TRABALHO FINAL — LABORATÓRIO DE ENGENHARIA DE SOFTWARE” orienta a seção de qualidade e validação (seção 8) e a defesa do projeto (seção 16). A análise foi cruzada com o código-fonte atual, test_app.py, README.md e documentos técnicos anteriores do SIGOA. O material anterior descreve a evolução planejada, mas as afirmações deste relatório sobre resultados atuais se baseiam no repositório e na execução realizada nesta avaliação.'),
 P('2. Qualidade, verificação e validação','H1x'),
 P('<b>Qualidade de software</b> é o grau em que o produto atende requisitos explícitos e necessidades de uso, mantendo comportamento confiável, seguro, compreensível e adequado ao contexto. Para este MVP, os atributos prioritários são correção funcional, controle de acesso e isolamento de dados, integridade dos registros, facilidade de uso e clareza dos feedbacks.'),
 P('<b>Verificação:</b> “o produto foi construído conforme a especificação?” Foi abordada por inspeção do código, critérios rastreáveis e testes automatizados de rotas e persistência. <b>Validação:</b> “o produto resolve a necessidade do estudante?” Ainda é parcial: a solução corresponde ao problema de centralizar prazos e materiais, mas não foi apresentada evidência de avaliação com usuários representativos.'),
 P('Princípios aplicados: critérios observáveis; evidência reproduzível; registro de limitações; e distinção entre teste executado, inspeção estática e validação ainda pendente.'), PageBreak()]

# Aceitação e rastreabilidade
story += [P('3. Critérios de aceitação e MVP','H1x'),
 P('Os critérios abaixo traduzem as necessidades centrais descritas no backlog e nos documentos do projeto em resultados observáveis. “Coberto” significa que existe um teste automatizado relacionado; não equivale a cobertura exaustiva da funcionalidade.'),
 table([['Requisito / critério de aceitação','Evidência disponível','Situação'],
 ['Cadastro: dados válidos criam conta vazia, senha com hash e mínimo de 8 caracteres.','test_auth_and_registration confirma zero eventos/arquivos e rejeita senha curta.','Coberto no backend'],
 ['Agenda: usuário autenticado cria, consulta, edita e remove compromissos próprios.','test_events_crud_and_google_url percorre o ciclo CRUD e URL de agenda.','Coberto no backend'],
 ['Importacao de horarios por PDF: envio do calendario e da grade, escolha de fase e aulas nos dias letivos.','Leitura manual dos PDFs de referencia: periodo 2026/2, 105 dias letivos e fases 1-8. Parser sem teste automatizado; fluxo no navegador nao validado.','Implementado; validacao parcial'],
 ['Privacidade: usuário não consulta nem baixa dados de outro usuário.','test_multi_user_isolation verifica eventos, arquivos e download (404).','Coberto no cenário testado'],
 ['Arquivos: usuário autenticado envia, lista, baixa e exclui anexos permitidos.','test_file_upload_per_user confere arquivo no disco e sua remoção física; isolamento testado.','Coberto nos fluxos testados'],
 ['Integração: modo Demo é explicitamente configurável e OAuth real valida token.','Testes cobrem Demo ligado/desligado; não há teste de token OAuth real nem de importação ICS externa.','Parcial'],
 ['Direitos LGPD: exportar dados e excluir conta remove registros e arquivos.','test_lgpd_compliance verifica JSON, conta/eventos e arquivo físico removidos.','Coberto no cenário testado'],
 ['Usabilidade: estudante localiza prazo, cria evento e configura lembrete sem ajuda.','Sem teste observado com usuários.','Pendente'],
 ['Lembretes: opções válidas incluem 1 semana e alertas respeitam tipo escolhido.','Servidor valida os seis valores permitidos; JavaScript calcula prazo e exclui “Sem lembrete”. Teste de calendário real ainda pendente.','Backend coberto; navegador pendente']], [55*mm,81*mm,34*mm], font='Tinyx', padding=4),
 Spacer(1,5), P('MVP planejado × implementado','H2x'),
 P('O nucleo (conta, agenda, gestao de eventos e arquivos) esta implementado. D-01 permanece aberto: ha rotas e teste automatizado isolado para token, mas a redefinicao nao foi confirmada como resolvida no fluxo do produto. O teste usa envio de e-mail simulado; SMTP real, OAuth real, importacao em calendario externo e interface no navegador ainda precisam de validacao ponta a ponta.'),
 PageBreak()]

# plano e execução
story += [P('4. Planejamento e execução dos testes','H1x'),
 P('Abordagem usada: testes funcionais automatizados de endpoints usando unittest e cliente de teste do Flask; inspeção estática de configurações e interfaces; análise de rastreabilidade com os critérios do MVP. A suíte foi executada em 12/11/2026. Cada caso cria banco e diretório de uploads temporários e os remove ao final, sem alterar os dados locais do projeto.'),
 P('Critérios de saída para a apresentação','H2x'),
 P('O criterio dos testes automatizados foi alcancado. A correcao dos achados permanece parcial enquanto a redefinicao de senha (D-01) nao estiver resolvida. Os demais itens abaixo continuam pendentes.'),
 table([['Criterio','Status e evidencias'],
 ['1. Oito testes automatizados aprovados','ALCANCADO - 8 testes de backend aprovados em 12/11/2026. O leitor de PDFs e a interface no navegador nao estao cobertos por essa suite.'],
 ['2. Achados corrigidos e retestados nos fluxos disponiveis','PARCIAL / PENDENTE - D-01, redefinicao de senha, continua aberto. Os demais achados e retestes estao discriminados na secao 5.'],
 ['3. Execucao guiada de fluxo completo com dados ficticios','PENDENTE - executar no navegador, incluindo importacao dos PDFs.'],
 ['4. Usabilidade com pelo menos tres estudantes','PENDENTE - observar estudantes usando os fluxos principais e registrar resultados.'],
 ['5. SMTP para provar envio real do link','PENDENTE - configurar SMTP e confirmar o recebimento do link de recuperacao.'],
 ['6. Configuracao segura, sem segredo padrao nem Demo aberto em producao','PENDENTE - conferir SECRET_KEY segura, APP_ENV=production e Demo desabilitado no ambiente de implantacao.']], [65*mm,105*mm], font='Smallx', padding=5),
 Spacer(1,5), P('Execução automatizada','H2x'),
 table([['Caso executado','O que verifica','Resultado'],
 ['Cadastro e senha','Conta inicia vazia; persistência/hash e rejeição de senha curta.','APROVADO'],
 ['CRUD de eventos','Criar/listar/editar/excluir evento; rejeitar lembrete inválido.','APROVADO'],
 ['Arquivos por usuário','Upload, listagem, download e remoção do arquivo físico.','APROVADO'],
 ['Isolamento multiusuário','Bloqueia consulta e download de dados alheios.','APROVADO'],
 ['Google Demo e recuperação','Demo permitido por flag; recuperação indisponível sem SMTP.','APROVADO'],
 ['Demo desabilitado','Bloqueia login quando a flag está desligada.','APROVADO'],
 ['Redefinicao por token','Resposta neutra; tokens expirados/reutilizados e senha curta rejeitados.','APROVADO no teste isolado; e-mail simulado; D-01 aberto'],
 ['Direitos LGPD','Exportação JSON e exclusão da conta/eventos/anexo físico.','APROVADO']], [51*mm,91*mm,28*mm], font='Tinyx', padding=4),
 Spacer(1,6), P('Resumo da execução','H2x'),
 P('<b>Ran 8 tests — OK.</b> A sintaxe de app.js também passou pela análise do motor Chromium; os fluxos interativos, temporização e DOM não foram exercitados em navegador. A suíte não mede responsividade, acessibilidade, carga, concorrência, SMTP de verdade ou Google OAuth real. O envio e recebimento de e-mail precisam de SMTP e validação ponta a ponta.'),
 P('Plano complementar recomendado','H2x'),
 table([['Tipo','Cenários prioritários','Evidência a guardar'],
 ['Funcional / integração','Campos inválidos; datas/horários; operações sem sessão (401); ID inexistente (404); anexar arquivo a evento de outro usuário; exclusão física; exportação ICS.','Roteiro, request/response, resultado e versão do código.'],
 ['Usabilidade','3–5 estudantes: cadastrar-se, localizar prazo, criar prova com lembrete, anexar PDF, marcar conclusão e exportar calendário. Observar sem instruir.','Taxa de conclusão, tempo aproximado, erros, comentários e ajustes.'],
 ['Compatibilidade / acessibilidade','Chrome/Firefox, largura móvel/desktop, teclado, foco, contraste e mensagens de erro.','Capturas datadas e lista de achados.'],
 ['Seguranca basica','Segredo de sessao, modo Demo, recuperacao, autorizacao por usuario, tipos/tamanho de arquivo e sessao/logout.','Checklist repetivel; reteste de cada defeito.']], [31*mm,101*mm,38*mm], font='Tinyx', padding=4),
 P('No reteste, executar primeiro o caso que reproduziu o defeito, depois a suite completa, registrar resultado e atualizar o status. D-01 continua aberto: o teste automatizado de token usa envio de e-mail simulado e nao reproduz o fluxo completo em que o problema foi observado. SMTP real tambem nao foi executado.'), PageBreak()]

# defeitos
story += [P('5. Defeitos e riscos identificados','H1x'),
 P('Classificacao usada na inspecao inicial: P0 bloqueador; P1 alto; P2 moderado; P3 baixo. Quatro achados foram corrigidos; D-01 (redefinicao de senha) permanece aberto conforme relato de falha no fluxo do produto. Os fluxos cobertos por testes foram retestados; alteracoes de interface foram revisadas por inspecao estatica. Nao houve varredura independente.'),
 table([['D-01 • P1 alto — recuperação de senha'],
  ['<b>Estado:</b> ABERTO. A falha de redefinicao relatada continua sem correcao confirmada. O teste automatizado isolado de token usa SMTP simulado e nao valida o fluxo real; envio de e-mail tambem pendente.'],
 ['D-02 • P1 alto em implantação — modo Google Demo'],
 ['/auth/google só aceita Demo com ALLOW_GOOGLE_DEMO=true fora de produção; flag desligada rejeita a tentativa. Sem credenciais Google e sem Demo, login externo retorna indisponível.<br/><b>Reteste:</b> Demo permitido em teste isolado e rejeitado com flag desligada. OAuth real não executado. <b>Estado:</b> corrigido e parcialmente retestado.'],
 ['D-03 • P2 moderado — chave de sessão'],
 ['<b>Achado:</b> chave padrão fixa e cookie de sessão sem política explícita.<br/><b>Correção:</b> chave aleatória em desenvolvimento; produção falha ao iniciar sem SECRET_KEY. Cookies HttpOnly/SameSite=Lax e Secure em produção; servidor local usa loopback e desativa debug em produção. <b>Estado:</b> corrigido por inspeção; configuração de implantação ainda precisa ser verificada.'],
 ['D-04 • P2 moderado — conteúdo HTML nos alertas'],
 ['<b>Achado:</b> dados dinâmicos de eventos/arquivos eram interpolados sem escape em HTML.<br/><b>Correção:</b> escapeHtml para texto, validação de cor, textContent e criação segura dos itens do lembrete; links externos usam rel=noopener noreferrer. <b>Estado:</b> corrigido por inspeção estática; teste em navegador pendente.'],
 ['D-05 • P2 moderado — lembretes'],
 ['<b>Achado:</b> lembretes ignoravam a opção, e 1 semana não estava disponível.<br/><b>Correção:</b> opções alinhadas; backend rejeita valores fora da lista; painel calcula o prazo escolhido e ignora eventos concluídos/“Sem lembrete”.<br/><b>Reteste:</b> tipo inválido rejeitado por teste automatizado; temporização visual revisada estaticamente. <b>Estado:</b> corrigido; teste real de navegador pendente.']], [170*mm], font='Smallx', header=False, padding=7),
 Spacer(1,5), P('Observação sobre classificação','H2x'),
 P('D-01 permanece aberto. D-02 e D-05 tem retestes automatizados relacionados; D-03 e D-04 foram verificados por inspecao do codigo. Permanecem pendentes a configuracao segura do ambiente de implantacao e o reteste da interface em navegador. SMTP real e OAuth real nao foram exercitados.'),
 P('Defeitos detectados pela suíte','H2x'),
 P('A execução não encontrou falhas nos oito cenários implementados. Esse resultado se limita aos casos e ambiente testados; não prova ausência de bugs nem substitui a validação com usuários, a integração real de e-mail/OAuth ou testes de navegador.'), PageBreak()]

# avaliação qualidade e demo
story += [P('6. Avaliação do MVP e limitações','H1x'),
 table([['Dimensão','Avaliação','Justificativa'],
 ['Funcionalidade essencial','Boa evidência no núcleo','CRUD de eventos e cadastro passam em teste automatizado; isolamento multiusuário e ciclo de arquivos têm cenários positivos.'],
 ['Integração','Parcial','Google Demo e URL são exercitados; OAuth real, importação ICS em calendário externo e fluxo ponta a ponta não.'],
 ['Usabilidade','Ainda não validada','Interface e calendário existem, mas não há observação de usuários nem métricas de conclusão.'],
 ['Seguranca','Parcial; sem auditoria de producao','Correcoes de Demo, chave de sessao e escaping implementadas; D-01 (redefinicao de senha) continua aberto. Faltam revisao do ambiente real e teste independente.'],
 ['Confiabilidade / operação','Não medida','Sem testes de carga, disponibilidade, recuperação de backup ou concorrência.'],
 ['Privacidade / dados','Coberta nos fluxos testados','Exportação e exclusão de conta/eventos/anexo físico verificadas em teste automatizado.']], [37*mm,43*mm,90*mm], font='Tinyx', padding=4),
 P('Limitações conhecidas a comunicar','H2x'),
 P('Importacao de horarios por PDF conferida manualmente com os arquivos de referencia; exige PDFs pesquisaveis em formatos compativeis. O parser automatizado e o fluxo completo no navegador ainda nao foram testados.'),
 P('MVP academico, sem evidencia de implantacao monitorada, carga ou escala.<br/>Painel de lembretes e visual e so atualiza quando a aplicacao carrega/atualiza eventos; nao envia push/e-mail.<br/>Modo Google Demo continua sendo simulacao e so deve ser habilitado em ambiente local isolado; OAuth real nao foi testado.<br/>D-01: redefinicao de senha segue aberta. O teste de token usa SMTP simulado; envio real e fluxo completo nao foram validados.<br/>Testes automatizados cobrem backend; nao ha evidencia de execucao em navegador nem teste de usabilidade com estudantes.<br/>Producao requer SECRET_KEY segura, APP_ENV=production e configuracao de SMTP/OAuth conforme os recursos usados.'),
 PageBreak(), P('7. Roteiro para apresentação e defesa','H1x'),
 P('Sequência sugerida para explicar o problema, demonstrar o MVP e defender as evidências de qualidade. Use uma conta e dados fictícios durante a demonstração.','Bodyx'),
 step_card('01','Problema e objetivo','<b>Mostre:</b> a dispersão de prazos e materiais que motivou o SIGOA. <b>Explique:</b> o MVP centraliza compromissos acadêmicos e arquivos em uma agenda por estudante.'),
 step_card('02','Demonstração do fluxo principal','<b>Mostre:</b> crie um evento de prova, escolha um lembrete, anexe um arquivo de teste, edite o compromisso e marque-o como concluído. <b>Explique:</b> as alterações são persistidas e os dados ficam isolados por usuário.'),
 step_card('03','Como a qualidade foi verificada','<b>Mostre:</b> os oito testes aprovados e alguns casos concretos: isolamento de dados, rejeição de senha fraca, token de redefinição e exclusão física de anexo. <b>Explique:</b> os testes cobrem rotas e persistência; não equivalem a teste com usuários.'),
  step_card('04','Achados e correcoes','<b>Explique:</b> a inspecao inicial encontrou cinco problemas; quatro foram corrigidos e D-01 (redefinicao de senha) permanece aberto. O envio por SMTP ainda precisa ser validado. O login Google de demonstracao fica desligado por padrao.'),
 step_card('05','Limites e próximos passos','<b>Informe:</b> ainda faltam validar envio real de e-mail, OAuth real, interação em navegador e usabilidade com estudantes. Proponha teste guiado com três a cinco estudantes e registro de conclusão, erros e comentários.'),
 P('Fechamento sugerido','H2x'), Spacer(1,8),
  P('Quatro achados foram corrigidos; D-01, sobre redefinicao de senha, segue aberto. Os oito testes automatizados passaram nos cenarios cobertos, mas nao substituem a verificacao do fluxo completo. Ainda precisamos validar integracoes reais e observar estudantes usando a interface.','Callout'), PageBreak()]

# referências e apêndice
story += [P('8. Evidências e referências','H1x'),
 P('Fontes analisadas','H2x'),
 P('1. TRABALHO FINAL — LABORATÓRIO DE ENGENHARIA DE SOFTWARE.pdf, 16 p. Enunciado da entrega; seção 8 (Qualidade e Validação), seção 16 (Entrega Final) e seção 17 (Critério Geral de Avaliação).<br/>2. Código do SIGOA: app.py, schedule_pdf.py, config.py, database.py, google_service.py, static/js/app.js e telas de autenticação/agenda.<br/>3. test_app.py: suíte unittest com oito casos; usa banco e uploads temporários por caso.<br/>4. README.md, .env.example e documentos técnicos anteriores do SIGOA.'),
 P('Registro reproduzível da execução','H2x'),
 P('Comando executado: <font name="Courier">python -m unittest test_app.SIGOATestCase -v</font>. Resultado observado: 8 testes aprovados, 0 falhas e 0 erros. Cada caso cria e remove seu banco e pasta de upload temporários.'),
 P('Matriz breve de rastreabilidade','H2x'),
 table([['Conteúdo exigido pela Fase 4','Seção deste relatório'],
 ['Conceito de qualidade; verificação e validação','Seção 2'],
 ['Critérios de aceitação; testes funcionais e de integração','Seções 3 e 4'],
 ['Usabilidade e evidências','Seções 3, 4 e 6'],
 ['Identificação/classificação de defeitos; correção e reteste','Seção 5'],
 ['Planejamento, execução, MVP, limitações e riscos','Seções 1, 4, 5 e 6'],
 ['Preparação para apresentação','Seção 7']], [95*mm,75*mm], font='Smallx'),
 Spacer(1,10), HRFlowable(width='100%', thickness=1, color=TEAL), Spacer(1,8),
 P('Conclusão','H2x'),
 P('O SIGOA inclui cadastro e autenticacao, agenda academica, CRUD de compromissos, anexos, exportacao de calendario, portabilidade e exclusao de dados. A importacao de aulas por PDF esta implementada, mas o parser e o fluxo completo ainda precisam de testes. A redefinicao de senha permanece como achado aberto (D-01). Esta avaliacao combina leitura do enunciado do Trabalho Final, inspecao do codigo e resultados registrados da suite automatizada existente.'),
 Spacer(1,6), P('UNEMAT • Cáceres — MT • 2026','Smallx')]

doc=SimpleDocTemplate(str(OUT), pagesize=A4, rightMargin=20*mm, leftMargin=20*mm,
                      topMargin=22*mm, bottomMargin=21*mm,
                      title='Relatório de Validação e Qualidade do Produto — SIGOA',
                      author='Yuri Sardinha Milani e Emanuel Faria',
                      subject='Fase 4 — Qualidade e Entrega')
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
