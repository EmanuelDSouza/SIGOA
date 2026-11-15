# SIGOA - Sistema de Gerenciamento de Organização Acadêmica
> **Projeto desenvolvido com base no documento oficial "Design Sprint: MVP em 7 Dias"**  
> Laboratório de Engenharia • Semestre Acadêmico

Este projeto é uma aplicação web completa desenvolvida para resolver os problemas de esquecimento e descentralização de prazos e materiais acadêmicos enfrentados por estudantes universitários.

---

## 🎯 Funcionalidades Implementadas

### 1. Requisitos do MVP (Design Sprint)
- **Autenticação Segura de Alunos**:
  - Cadastro completo (`Nome`, `E-mail`, `Senha` criptografada com hash Werkzeug, `Confirmação de Senha`).
  - Login com e-mail e senha.
  - Recuperação por link de uso único enviado por e-mail, válido por 1 hora (requer SMTP configurado).
- **Agenda Acadêmica Interativa (RF04)**:
  - Navegação entre meses, semanas e dias com botão de retorno rápido para "Hoje".
  - Seletor de visualização completo (**Dia / Semana / Mês**).
  - Grade mensal responsiva com **marcadores e pílulas coloridas** para cada compromisso.
  - **Legenda de Cores oficial**:
    - 🔴 **Vermelho**: Provas e Avaliações Bimestrais
    - 🔵 **Azul**: Aulas e Laboratórios
    - 🟢 **Verde**: Entregas de Trabalhos e Projetos
    - 🟣 **Roxo**: Seminários e Apresentações
    - 🟠 **Âmbar**: Outros Compromissos
- **Gestão de Eventos / CRUD Completo (RF02)**:
  - Criação rápida clicando em qualquer dia do calendário ou no botão "+ Adicionar Evento".
  - Modal de edição e detalhes com dados pré-preenchidos.
  - Exclusão com confirmação.
  - Alertas e lembretes internos (no horário, 1h antes, 1 dia antes, 2 dias antes).
  - Banner dinâmico de aviso no topo para compromissos urgentes das próximas 48 horas.
  - Sininho de notificações com lista suspensa de alertas pendentes.

### 2. Gerenciamento e Registro de Arquivos por Usuário (DB Dedicado)
- Banco de dados relacional **SQLite (`academico.db`)** com isolamento total entre usuários.
- Upload de materiais de aula, slides, enunciados de projetos e comprovantes de entrega (PDF, DOCX, Imagens, ZIP).
- Os arquivos podem ser anexados a um evento específico ou salvos na biblioteca geral de "Meus Arquivos".
- Download direto e exclusão segura tanto no banco quanto no armazenamento em disco (`uploads/`).

### 3. Integração com a API do Google
- **Sincronização Direta com o Google Agenda (Google Calendar)**:
  - Botão presente em cada evento que gera a URL oficial de inclusão direta na agenda do Google do estudante.
  - Exportação em massa de todos os compromissos em formato `.ics` (iCalendar), compatível com Google Calendar, Outlook e Apple Calendar.
- **Autenticação com Google (Google Identity Services / OAuth 2.0)**:
  - Suporte ao Google Sign-In oficial via Google OAuth 2.0.
  - Modo de demonstração desativado por padrão; habilite apenas em ambiente local com ALLOW_GOOGLE_DEMO=true.

### 4. Conformidade com a LGPD (Lei nº 13.709/2018)
- **Princípio da Minimização de Dados (Art. 6º, III)**: Apenas os dados estritamente necessários (Nome, E-mail e Senha) são coletados. Nenhum dado sensível é requisitado.
- **Segurança da Informação (Art. 46)**: Senhas com salting criptográfico robusto e isolamento de banco de dados (`WHERE user_id = ?`).
- **Consentimento Explícito (Art. 7º, I e Art. 8º)**: Termo e modal explicativo no momento do cadastro do estudante.
- **Direito à Portabilidade (Art. 18, V)**: Exportação completa dos dados cadastrais, eventos e arquivos em formato `.json` padronizado.
- **Direito à Eliminação / Esquecimento (Art. 18, VI)**: Opção de exclusão permanente da conta, removendo registros do SQLite e arquivos físicos do disco em efeito cascata.

---

## 🏗️ Estrutura do Projeto

```
laboratorio de engenharia/
├── app.py                     # Servidor Flask e rotas da API REST / Sessões
├── database.py                # Camada de banco de dados SQLite e consultas
├── google_service.py          # Integração com Google Agenda, OAuth e exportação ICS
├── config.py                  # Configurações do sistema e upload
├── requirements.txt           # Dependências Python (Flask, Werkzeug, requests)
├── test_app.py                # Suíte de testes automatizados unitários e de integração
├── .env.example               # Exemplo de configuração de variáveis de ambiente
├── README_DATABASE.md         # Documentação do Banco de Dados e Dicionário de Dados
├── templates/
│   ├── index.html             # Painel principal (Calendário Mês/Semana/Dia, Modais e Arquivos)
│   ├── login.html             # Tela de login e autenticação Google
│   └── register.html          # Tela de cadastro com validação
├── static/
│   ├── css/
│   │   └── style.css          # Estilos customizados da grade e animações
│   └── js/
│       └── app.js             # Lógica cliente, renderização do calendário e chamadas REST
├── uploads/                   # Diretório de armazenamento seguro dos arquivos dos alunos
└── Plano de Ação MVP - Gerenciamento Acadêmico (Final) (2).pdf # Documento base do Design Sprint
```

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.10+ instalado no computador.

### Passo 1: Instalar as Dependências (caso necessário)
```bash
pip install -r requirements.txt
```

### Configuração de segurança
- Em desenvolvimento, o SIGOA gera uma chave de sessão aleatória ao iniciar. Para produção, defina `APP_ENV=production` e configure `SECRET_KEY` aleatória antes de iniciar.
- O login Google de demonstração fica desativado por padrão. Para uma demonstração local isolada, defina `ALLOW_GOOGLE_DEMO=true`; não habilite essa opção em produção.
- A recuperação de senha envia um link de uso único e requer `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM` e `PUBLIC_BASE_URL`. Sem SMTP, a tela informa que a recuperação está indisponível.
- `.env.example` documenta as variáveis; o projeto não carrega arquivos `.env` automaticamente. Configure-as no ambiente do processo.

### Passo 2: Executar o Servidor Web
```bash
python app.py
```

O sistema iniciará automaticamente e estará acessível em:
👉 **`http://localhost:5000`** ou **`http://127.0.0.1:5000`**

### Passo 3: Executar a Suíte de Testes Automatizados
```bash
python test_app.py
```
*(A suíte atual contém 8 testes automatizados cobrindo cadastro, eventos, anexos, isolamento, modo Demo, redefinição de senha e operações LGPD.)*

---

## 🔑 Acesso e Teste Imediato

1. Acesse `http://localhost:5000/register` para criar sua conta. O login Google aparece quando OAuth está configurado ou quando a demonstração local foi habilitada explicitamente.
2. Contas novas começam sem eventos ou arquivos. Cadastre seus próprios compromissos pelo botão de adicionar evento; os dados de demonstração do projeto não são inseridos automaticamente.
