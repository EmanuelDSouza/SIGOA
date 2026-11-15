import os
import json
import uuid
import smtplib
import hmac
import hashlib
from datetime import datetime
from email.message import EmailMessage
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, send_from_directory, flash, Response
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

import config
import database as db
import google_service

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH
app.config['SESSION_COOKIE_SECURE'] = config.SESSION_COOKIE_SECURE
app.config['SESSION_COOKIE_HTTPONLY'] = config.SESSION_COOKIE_HTTPONLY
app.config['SESSION_COOKIE_SAMESITE'] = config.SESSION_COOKIE_SAMESITE

PASSWORD_RESET_SALT = 'sigoa-password-reset-v1'

def password_reset_serializer():
    return URLSafeTimedSerializer(app.config['SECRET_KEY'])

def password_reset_fingerprint(email, password_hash):
    message = f'{email}:{password_hash}'.encode('utf-8')
    return hmac.new(app.config['SECRET_KEY'].encode('utf-8'), message, hashlib.sha256).hexdigest()

def send_password_reset_email(user, token):
    """Envia o link de redefinição; sem SMTP configurado, não emite token."""
    if not config.MAIL_SERVER:
        return False
    reset_url = f"{config.PUBLIC_BASE_URL.rstrip('/')}{url_for('reset_password_page')}?token={token}"
    message = EmailMessage()
    message['Subject'] = 'Redefinição de senha do SIGOA'
    message['From'] = config.MAIL_FROM
    message['To'] = user['email']
    message.set_content(
        f"Olá, {user['name']}. Use o link abaixo para redefinir sua senha. "
        f"O link expira em 1 hora e pode ser usado uma única vez.\n\n{reset_url}\n"
    )
    with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT, timeout=10) as smtp:
        if config.MAIL_USE_TLS:
            smtp.starttls()
        if config.MAIL_USERNAME:
            smtp.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
        smtp.send_message(message)
    return True

# Inicializa o banco de dados SQLite
db.init_db()

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Não autorizado. Faça login primeiro.'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROTAS DE AUTENTICAÇÃO ====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        user = db.get_user_by_email(email)
        if user and user['password_hash'] and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            session['user_avatar'] = user.get('avatar')
            return redirect(url_for('index'))
        else:
            error = 'E-mail ou senha incorretos. Verifique suas credenciais.'
            
    return render_template(
        'login.html', error=error, google_client_id=config.GOOGLE_CLIENT_ID,
        google_demo_enabled=config.ALLOW_GOOGLE_DEMO and config.APP_ENV != 'production'
    )

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not name or not email or not password:
            error = 'Por favor, preencha todos os campos obrigatórios.'
        elif len(password) < 8:
            error = 'A senha deve conter no mínimo 8 caracteres.'
        elif password != confirm_password:
            error = 'As senhas não coincidem. Digite novamente.'
        elif db.get_user_by_email(email):
            error = 'Já existe uma conta registrada com este e-mail.'
        else:
            pwd_hash = generate_password_hash(password)
            user_id = db.create_user(name, email, password_hash=pwd_hash)
            if user_id:
                session['user_id'] = user_id
                session['user_name'] = name
                session['user_email'] = email
                session['user_avatar'] = None
                return redirect(url_for('index'))
            else:
                error = 'Erro ao registrar usuário. Tente novamente.'
                
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/auth/google', methods=['POST'])
def auth_google():
    data = request.get_json() or {}
    token = data.get('credential') or data.get('id_token')
    is_demo = data.get('demo', False)
    
    # Se for login de demonstração rápida da API do Google ou token real
    if is_demo:
        if not config.ALLOW_GOOGLE_DEMO or config.APP_ENV == 'production':
            return jsonify({'success': False, 'error': 'Modo de demonstração desabilitado.'}), 403
        # Usuário de teste integrado do Google
        demo_email = data.get('email', 'aluno.academico@gmail.com')
        demo_name = data.get('name', 'Estudante Google')
        demo_avatar = 'https://lh3.googleusercontent.com/a/default-user=s96-c'
        
        user = db.get_user_by_email(demo_email)
        if not user:
            user_id = db.create_user(demo_name, demo_email, google_id='demo-google-id', avatar=demo_avatar)
        else:
            user_id = user['id']
            demo_name = user['name']
            
        session['user_id'] = user_id
        session['user_name'] = demo_name
        session['user_email'] = demo_email
        session['user_avatar'] = demo_avatar
        return jsonify({'success': True, 'redirect': url_for('index')})

    if not config.GOOGLE_CLIENT_ID:
        return jsonify({'success': False, 'error': 'Autenticação Google não configurada.'}), 503
        
    # Verificação oficial de token Google OAuth
    google_user = google_service.verify_google_id_token(token)
    if not google_user:
        return jsonify({'success': False, 'error': 'Token Google inválido ou expirado.'}), 400
        
    user = db.get_user_by_email(google_user['email'])
    if not user:
        user_id = db.create_user(
            name=google_user['name'],
            email=google_user['email'],
            google_id=google_user['google_id'],
            avatar=google_user['avatar']
        )
    else:
        user_id = user['id']
        
    session['user_id'] = user_id
    session['user_name'] = google_user['name']
    session['user_email'] = google_user['email']
    session['user_avatar'] = google_user['avatar']
    return jsonify({'success': True, 'redirect': url_for('index')})

@app.route('/auth/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    if not config.MAIL_SERVER:
        return jsonify({
            'success': False,
            'message': 'Redefinição indisponível: serviço de e-mail não configurado.'
        }), 503
    user = db.get_user_by_email(email)
    # Resposta neutra evita revelar se o e-mail possui cadastro.
    if user and user.get('password_hash') and config.MAIL_SERVER:
        token = password_reset_serializer().dumps(
            {'email': user['email'], 'fingerprint': password_reset_fingerprint(user['email'], user['password_hash'])},
            salt=PASSWORD_RESET_SALT
        )
        try:
            send_password_reset_email(user, token)
        except (OSError, smtplib.SMTPException) as exc:
            app.logger.error('Falha ao enviar link de redefinição: %s', exc)
    return jsonify({
        'success': True,
        'message': 'Se o e-mail estiver cadastrado, enviaremos instruções para redefinir a senha.'
    }), 202

@app.route('/reset-password')
def reset_password_page():
    response = app.make_response(render_template('reset_password.html', token=request.args.get('token', '')))
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Referrer-Policy'] = 'no-referrer'
    return response

@app.route('/auth/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or request.form
    token = (data.get('token') or '').strip()
    password = data.get('password') or ''
    confirm_password = data.get('confirm_password') or ''
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'A senha deve conter no mínimo 8 caracteres.'}), 400
    if password != confirm_password:
        return jsonify({'success': False, 'error': 'As senhas não coincidem.'}), 400
    try:
        payload = password_reset_serializer().loads(
            token, salt=PASSWORD_RESET_SALT, max_age=config.PASSWORD_RESET_MAX_AGE
        )
    except SignatureExpired:
        return jsonify({'success': False, 'error': 'Link expirado. Solicite uma nova redefinição.'}), 400
    except (BadSignature, TypeError):
        return jsonify({'success': False, 'error': 'Link de redefinição inválido.'}), 400
    user = db.get_user_by_email(payload.get('email', ''))
    if (not user or not user.get('password_hash') or
            not hmac.compare_digest(
                password_reset_fingerprint(user['email'], user['password_hash']),
                payload.get('fingerprint', '')
            )):
        return jsonify({'success': False, 'error': 'Link inválido ou já utilizado.'}), 400
    db.update_user_password(user['id'], generate_password_hash(password))
    return jsonify({'success': True, 'message': 'Senha redefinida. Você já pode entrar no SIGOA.'})
# ==================== ROTAS DE CONFORMIDADE LGPD ====================

@app.route('/api/user/export-data', methods=['GET'])
@api_login_required
def export_user_data_lgpd():
    """Direito à Portabilidade de Dados (Art. 18, V da LGPD)"""
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    events = db.get_events_by_user(user_id)
    files = db.get_files_by_user(user_id)
    
    user_data = {
        'lgpd_export_date': datetime.now().isoformat(),
        'perfil': {
            'nome': user['name'],
            'email': user['email'],
            'criado_em': user['created_at']
        },
        'compromissos_academicos': events,
        'arquivos_registrados': files
    }
    
    return Response(
        json.dumps(user_data, indent=2, ensure_ascii=False),
        mimetype="application/json",
        headers={"Content-Disposition": "attachment; filename=meus_dados_lgpd.json"}
    )

@app.route('/api/user/delete-account', methods=['POST'])
@api_login_required
def delete_account_lgpd():
    """Direito à Eliminação dos Dados / Esquecimento (Art. 18, VI da LGPD)"""
    user_id = session['user_id']
    
    # Remove fisicamente os arquivos do usuário
    stored_filenames = db.delete_user_account(user_id)
    for fname in stored_filenames:
        try:
            p = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            if os.path.exists(p):
                os.remove(p)
        except Exception as e:
            print(f"Erro ao remover arquivo na exclusão de conta: {e}")
            
    session.clear()
    return jsonify({'success': True, 'message': 'Sua conta e todos os seus dados e arquivos foram permanentemente excluídos.'})

# ==================== ROTAS PRINCIPAIS ====================

@app.route('/')
@login_required
def index():
    user = db.get_user_by_id(session['user_id'])
    return render_template(
        'index.html',
        user=user,
        google_client_id=config.GOOGLE_CLIENT_ID
    )

# ==================== API DE EVENTOS ====================

@app.route('/api/events', methods=['GET'])
@api_login_required
def get_events():
    user_id = session['user_id']
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    events = db.get_events_by_user(user_id, start_date, end_date)
    # Adiciona a URL do Google Calendar para cada evento retornado
    for ev in events:
        ev['google_calendar_url'] = google_service.generate_google_calendar_url(ev)
    response = jsonify(events)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.route('/api/events/inspect-schedule', methods=['POST'])
@api_login_required
def inspect_schedule_pdfs():
    """Valida os PDFs primeiro e s? ent?o oferece as fases encontradas."""
    from schedule_pdf import read_academic_calendar, read_course_schedule, read_course_semester

    calendar_file = request.files.get('calendar_pdf')
    schedule_file = request.files.get('schedule_pdf')
    if not calendar_file or not schedule_file:
        return jsonify({'error': 'Envie o calendario academico e o horario do curso em PDF.'}), 400
    if not calendar_file.filename.lower().endswith('.pdf') or not schedule_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Os dois arquivos precisam estar no formato PDF.'}), 400
    try:
        semester = read_course_semester(schedule_file.stream)
        period, teaching_dates = read_academic_calendar(calendar_file.stream, semester)
        phases = []
        for phase in range(1, 9):
            schedule_file.stream.seek(0)
            try:
                if read_course_schedule(schedule_file.stream, phase):
                    phases.append(phase)
            except ValueError:
                continue
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 422
    except Exception:
        app.logger.exception('Falha ao ler PDFs para importacao')
        return jsonify({'error': 'Nao consegui ler os PDFs. Confira se sao PDFs com texto selecionavel.'}), 422
    if not phases:
        return jsonify({'error': 'Nao encontrei fases no horario enviado.'}), 422
    return jsonify({
        'success': True, 'phases': phases,
        'start_date': period[0].isoformat(), 'end_date': period[1].isoformat(),
        'teaching_days': len(teaching_dates)
    })

@app.route('/api/events/import-schedule', methods=['POST'])
@api_login_required
def import_schedule():
    """Le o calendario academico e a grade do curso enviados pelo aluno."""
    from datetime import date, timedelta
    from schedule_pdf import read_academic_calendar, read_course_schedule, read_course_semester

    calendar_file = request.files.get('calendar_pdf')
    schedule_file = request.files.get('schedule_pdf')
    try:
        phase = int(request.form.get('phase', ''))
    except (TypeError, ValueError):
        return jsonify({'error': 'Informe sua fase (1 a 8).'}), 400
    if phase not in range(1, 9):
        return jsonify({'error': 'A fase deve estar entre 1 e 8.'}), 400
    if not calendar_file or not schedule_file:
        return jsonify({'error': 'Envie o calendario academico e o horario do curso em PDF.'}), 400
    if not calendar_file.filename.lower().endswith('.pdf') or not schedule_file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Os dois arquivos precisam estar no formato PDF.'}), 400

    try:
        semester = read_course_semester(schedule_file.stream)
        period, teaching_dates = read_academic_calendar(calendar_file.stream, semester)
        schedule_file.stream.seek(0)
        classes = read_course_schedule(schedule_file.stream, phase)
    except ValueError as exc:
        return jsonify({'error': str(exc)}), 422
    except Exception:
        app.logger.exception('Falha ao interpretar PDFs de horario')
        return jsonify({'error': 'Nao consegui ler os PDFs. Confira se sao PDFs com texto selecionavel e tente novamente.'}), 422

    if not classes:
        return jsonify({'error': f'Nao encontrei aulas para a {phase}a fase no horario enviado.'}), 422

    user_id = session['user_id']
    created = skipped = 0
    current = period[0]
    end_date = period[1]
    while current <= end_date:
        day_text = current.isoformat()
        if day_text in teaching_dates:
            existing = db.get_events_by_user(user_id, day_text, day_text)
            for item in classes:
                if item['weekday'] != current.weekday():
                    continue
                if any(ev.get('start_time') == item['start'] and (
                       (ev.get('discipline') or '').casefold() == item['discipline'].casefold()
                       or (ev.get('title') or '').startswith(item['code'] + ' -')
                       or (ev.get('title') or '').startswith(item['code'] + ' ' + chr(8212))
                       ) for ev in existing):
                    skipped += 1
                    continue
                db.create_event(
                    user_id, f"{item['code']} - {item['discipline']}",
                    f"SIGOA_IMPORT:phase-{phase}:{item['room']} - Importado dos PDFs academicos.",
                    item['discipline'], 'aula', '#2563eb', day_text,
                    item['start'], item['end'], 'none'
                )
                created += 1
        current += timedelta(days=1)

    return jsonify({
        'success': True, 'created': created, 'skipped': skipped,
        'phase': phase, 'start_date': period[0].isoformat(),
        'end_date': end_date.isoformat(), 'teaching_days': len(teaching_dates)
    }), 200

@app.route('/api/events', methods=['POST'])
@api_login_required
def create_event():
    user_id = session['user_id']
    
    # Suporta JSON e Form com Upload simultâneo
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
        
    title = data.get('title', '').strip()
    event_date = data.get('event_date', '').strip()
    
    if not title or not event_date:
        return jsonify({'error': 'Título e data do evento são obrigatórios.'}), 400
        
    description = data.get('description', '').strip()
    discipline = data.get('discipline', '').strip()
    event_type = data.get('event_type', 'aula').strip()
    color = data.get('color', '#2563eb').strip()
    start_time = data.get('start_time') or None
    end_time = data.get('end_time') or None
    reminder_type = data.get('reminder_type', 'none').strip()
    if reminder_type not in config.ALLOWED_REMINDER_TYPES:
        return jsonify({'error': 'Tipo de lembrete inválido.'}), 400
    
    event_id = db.create_event(
        user_id=user_id,
        title=title,
        description=description,
        discipline=discipline,
        event_type=event_type,
        color=color,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        reminder_type=reminder_type
    )
    
    # Processa upload de arquivo atrelado ao evento (se houver)
    file_uploaded = None
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            orig_name = secure_filename(file.filename)
            ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else ''
            stored_name = f"user_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            file_id = db.save_file_record(
                user_id=user_id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_size=file_size,
                file_type=ext,
                event_id=event_id
            )
            file_uploaded = {'id': file_id, 'filename': orig_name}
            
    event = db.get_event_by_id(event_id, user_id)
    event['google_calendar_url'] = google_service.generate_google_calendar_url(event)
    event['attached_file'] = file_uploaded
    
    return jsonify(event), 201

@app.route('/api/events/<int:event_id>', methods=['GET'])
@api_login_required
def get_single_event(event_id):
    user_id = session['user_id']
    event = db.get_event_by_id(event_id, user_id)
    if not event:
        return jsonify({'error': 'Evento não encontrado.'}), 404
        
    event['google_calendar_url'] = google_service.generate_google_calendar_url(event)
    event['files'] = db.get_files_by_event(event_id, user_id)
    return jsonify(event)

@app.route('/api/events/<int:event_id>', methods=['PUT', 'POST'])
@api_login_required
def update_event(event_id):
    user_id = session['user_id']
    event = db.get_event_by_id(event_id, user_id)
    if not event:
        return jsonify({'error': 'Evento não encontrado.'}), 404
        
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()
        
    title = data.get('title', event['title']).strip()
    event_date = data.get('event_date', event['event_date']).strip()
    description = data.get('description', event['description'] or '').strip()
    discipline = data.get('discipline', event['discipline'] or '').strip()
    event_type = data.get('event_type', event['event_type']).strip()
    color = data.get('color', event['color']).strip()
    start_time = data.get('start_time', event['start_time']) or None
    end_time = data.get('end_time', event['end_time']) or None
    reminder_type = data.get('reminder_type', event['reminder_type']).strip()
    if reminder_type not in config.ALLOWED_REMINDER_TYPES:
        return jsonify({'error': 'Tipo de lembrete inválido.'}), 400
    is_completed = int(data.get('is_completed', event['is_completed']))
    
    updated = db.update_event(
        event_id=event_id,
        user_id=user_id,
        title=title,
        description=description,
        discipline=discipline,
        event_type=event_type,
        color=color,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        reminder_type=reminder_type,
        is_completed=is_completed
    )
    
    # Processa novo arquivo atrelado se houver no FormData
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '' and allowed_file(file.filename):
            orig_name = secure_filename(file.filename)
            ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else ''
            stored_name = f"user_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}.{ext}"
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
            file.save(file_path)
            file_size = os.path.getsize(file_path)
            
            db.save_file_record(
                user_id=user_id,
                original_filename=orig_name,
                stored_filename=stored_name,
                file_size=file_size,
                file_type=ext,
                event_id=event_id
            )
            
    updated_event = db.get_event_by_id(event_id, user_id)
    updated_event['google_calendar_url'] = google_service.generate_google_calendar_url(updated_event)
    updated_event['files'] = db.get_files_by_event(event_id, user_id)
    
    return jsonify(updated_event)

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
@api_login_required
def delete_event(event_id):
    user_id = session['user_id']
    success = db.delete_event(event_id, user_id)
    if success:
        return jsonify({'message': 'Evento excluído com sucesso.'})
    return jsonify({'error': 'Evento não encontrado ou permissão negada.'}), 404

@app.route('/api/events/<int:event_id>/google-url', methods=['GET'])
@api_login_required
def get_event_google_url(event_id):
    user_id = session['user_id']
    event = db.get_event_by_id(event_id, user_id)
    if not event:
        return jsonify({'error': 'Evento não encontrado.'}), 404
        
    url = google_service.generate_google_calendar_url(event)
    return jsonify({'google_calendar_url': url})

@app.route('/api/events/export/ics', methods=['GET'])
@api_login_required
def export_calendar_ics():
    user_id = session['user_id']
    events = db.get_events_by_user(user_id)
    ics_content = google_service.generate_ics_calendar(events)
    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": "attachment; filename=calendario_academico.ics"}
    )

# ==================== API DE ARQUIVOS POR USUÁRIO ====================

@app.route('/api/files', methods=['GET'])
@api_login_required
def list_files():
    user_id = session['user_id']
    files = db.get_files_by_user(user_id)
    return jsonify(files)

@app.route('/api/files/upload', methods=['POST'])
@api_login_required
def upload_file():
    user_id = session['user_id']
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado.'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado.'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'Tipo de arquivo não suportado.'}), 400
        
    event_id = request.form.get('event_id')
    if event_id:
        try:
            event_id = int(event_id)
        except ValueError:
            event_id = None
            
    orig_name = secure_filename(file.filename)
    ext = orig_name.rsplit('.', 1)[1].lower() if '.' in orig_name else ''
    stored_name = f"user_{user_id}_{int(datetime.now().timestamp())}_{uuid.uuid4().hex[:8]}.{ext}"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
    file.save(file_path)
    file_size = os.path.getsize(file_path)
    
    file_id = db.save_file_record(
        user_id=user_id,
        original_filename=orig_name,
        stored_filename=stored_name,
        file_size=file_size,
        file_type=ext,
        event_id=event_id
    )
    
    return jsonify({
        'id': file_id,
        'original_filename': orig_name,
        'file_size': file_size,
        'file_type': ext,
        'message': 'Arquivo registrado com sucesso para o seu usuário.'
    }), 201

@app.route('/api/files/<int:file_id>/download', methods=['GET'])
@api_login_required
def download_file(file_id):
    user_id = session['user_id']
    file_record = db.get_file_by_id(file_id, user_id)
    if not file_record:
        return jsonify({'error': 'Arquivo não encontrado.'}), 404
        
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        file_record['stored_filename'],
        as_attachment=True,
        download_name=file_record['original_filename']
    )

@app.route('/api/files/<int:file_id>', methods=['DELETE'])
@api_login_required
def delete_file(file_id):
    user_id = session['user_id']
    file_record = db.get_file_by_id(file_id, user_id)
    if not file_record:
        return jsonify({'error': 'Arquivo não encontrado.'}), 404
        
    # Remove fisicamente o arquivo
    try:
        path = os.path.join(app.config['UPLOAD_FOLDER'], file_record['stored_filename'])
        if os.path.exists(path):
            os.remove(path)
    except Exception as e:
        print(f"Erro ao remover arquivo físico: {e}")
        
    db.delete_file_record(file_id, user_id)
    return jsonify({'message': 'Arquivo excluído com sucesso.'})

@app.route('/api/stats', methods=['GET'])
@api_login_required
def get_stats():
    user_id = session['user_id']
    events = db.get_events_by_user(user_id)
    files = db.get_files_by_user(user_id)
    
    today_str = datetime.now().strftime('%Y-%m-%d')
    provas_count = sum(1 for e in events if e['event_type'] == 'prova' and e['event_date'] >= today_str)
    entregas_count = sum(1 for e in events if e['event_type'] in ['trabalho', 'entrega'] and not e['is_completed'])
    total_eventos = len(events)
    total_arquivos = len(files)
    
    return jsonify({
        'provas_pendentes': provas_count,
        'entregas_pendentes': entregas_count,
        'total_eventos': total_eventos,
        'total_arquivos': total_arquivos
    })

if __name__ == '__main__':
    print("Iniciando Sistema de Gerenciamento de Organização Acadêmica na porta 5000...")
    app.run(host='127.0.0.1', port=5000, debug=config.APP_ENV != 'production')
