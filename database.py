import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), 'academico.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT,
            google_id TEXT UNIQUE,
            avatar TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Tabela de Eventos / Compromissos Acadêmicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            discipline TEXT,
            event_type TEXT NOT NULL DEFAULT 'aula',
            color TEXT NOT NULL DEFAULT '#2563eb',
            event_date TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            reminder_type TEXT DEFAULT 'none',
            is_completed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
        )
    ''')

    # Tabela de Arquivos do Usuário
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            event_id INTEGER,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL,
            file_size INTEGER NOT NULL,
            file_type TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (event_id) REFERENCES events (id) ON DELETE SET NULL
        )
    ''')

    conn.commit()
    conn.close()

# --- USUÁRIOS ---
def create_user(name, email, password_hash=None, google_id=None, avatar=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, google_id, avatar)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, email, password_hash, google_id, avatar))
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE LOWER(email) = LOWER(?)', (email.strip(),)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_google_id(google_id):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE google_id = ?', (google_id,)).fetchone()
    conn.close()
    return dict(user) if user else None

def update_user_password(user_id, new_password_hash):
    conn = get_db_connection()
    conn.execute('UPDATE users SET password_hash = ? WHERE id = ?', (new_password_hash, user_id))
    conn.commit()
    conn.close()

def delete_user_account(user_id):
    """Atende ao Direito de Eliminação / Esquecimento da LGPD (Art. 18, VI da Lei 13.709/2018)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Busca arquivos físicos associados para remoção
    files = cursor.execute('SELECT stored_filename FROM user_files WHERE user_id = ?', (user_id,)).fetchall()
    
    # Exclusão no banco (ON DELETE CASCADE cuidará de events e user_files)
    cursor.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    return [dict(f)['stored_filename'] for f in files]

# --- EVENTOS ---
def create_event(user_id, title, description, discipline, event_type, color, event_date, start_time=None, end_time=None, reminder_type='none'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO events (user_id, title, description, discipline, event_type, color, event_date, start_time, end_time, reminder_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, title, description, discipline, event_type, color, event_date, start_time, end_time, reminder_type))
    conn.commit()
    event_id = cursor.lastrowid
    conn.close()
    return event_id

def update_event(event_id, user_id, title, description, discipline, event_type, color, event_date, start_time, end_time, reminder_type, is_completed=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE events
        SET title = ?, description = ?, discipline = ?, event_type = ?, color = ?,
            event_date = ?, start_time = ?, end_time = ?, reminder_type = ?, is_completed = ?
        WHERE id = ? AND user_id = ?
    ''', (title, description, discipline, event_type, color, event_date, start_time, end_time, reminder_type, is_completed, event_id, user_id))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def delete_event(event_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM events WHERE id = ? AND user_id = ?', (event_id, user_id))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

def get_events_by_user(user_id, start_date=None, end_date=None):
    conn = get_db_connection()
    query = '''
        SELECT e.*, 
               (SELECT COUNT(*) FROM user_files f WHERE f.event_id = e.id) as files_count
        FROM events e
        WHERE e.user_id = ?
    '''
    params = [user_id]
    
    if start_date and end_date:
        query += ' AND e.event_date BETWEEN ? AND ?'
        params.extend([start_date, end_date])
        
    query += ' ORDER BY e.event_date ASC, e.start_time ASC'
    
    events = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in events]

def get_event_by_id(event_id, user_id):
    conn = get_db_connection()
    event = conn.execute('''
        SELECT e.*, 
               (SELECT COUNT(*) FROM user_files f WHERE f.event_id = e.id) as files_count
        FROM events e
        WHERE e.id = ? AND e.user_id = ?
    ''', (event_id, user_id)).fetchone()
    conn.close()
    return dict(event) if event else None

# --- ARQUIVOS ---
def save_file_record(user_id, original_filename, stored_filename, file_size, file_type, event_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO user_files (user_id, event_id, original_filename, stored_filename, file_size, file_type)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, event_id, original_filename, stored_filename, file_size, file_type))
    conn.commit()
    file_id = cursor.lastrowid
    conn.close()
    return file_id

def get_files_by_user(user_id):
    conn = get_db_connection()
    files = conn.execute('''
        SELECT f.*, e.title as event_title, e.discipline as event_discipline
        FROM user_files f
        LEFT JOIN events e ON f.event_id = e.id
        WHERE f.user_id = ?
        ORDER BY f.uploaded_at DESC
    ''', (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in files]

def get_files_by_event(event_id, user_id):
    conn = get_db_connection()
    files = conn.execute('''
        SELECT * FROM user_files
        WHERE event_id = ? AND user_id = ?
        ORDER BY uploaded_at DESC
    ''', (event_id, user_id)).fetchall()
    conn.close()
    return [dict(row) for row in files]

def get_file_by_id(file_id, user_id):
    conn = get_db_connection()
    file_row = conn.execute('''
        SELECT * FROM user_files WHERE id = ? AND user_id = ?
    ''', (file_id, user_id)).fetchone()
    conn.close()
    return dict(file_row) if file_row else None

def delete_file_record(file_id, user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_files WHERE id = ? AND user_id = ?', (file_id, user_id))
    conn.commit()
    rows = cursor.rowcount
    conn.close()
    return rows > 0

# --- SEED DE DEMOSTRAÇÃO CONFORME O PDF DO DESIGN SPRINT ---
def seed_demo_data(user_id):
    """Insere exemplos reais de compromissos acadêmicos baseados no PDF do projeto"""
    conn = get_db_connection()
    count = conn.execute('SELECT COUNT(*) as c FROM events WHERE user_id = ?', (user_id,)).fetchone()['c']
    if count == 0:
        today = datetime.now()
        year = today.year
        month = today.month
        
        # Datas de exemplo no mês corrente
        d1 = datetime(year, month, min(10, 28)).strftime('%Y-%m-%d')
        d2 = datetime(year, month, min(15, 28)).strftime('%Y-%m-%d')
        d3 = datetime(year, month, min(18, 28)).strftime('%Y-%m-%d')
        d4 = datetime(year, month, min(24, 28)).strftime('%Y-%m-%d')

        demo_events = [
            (
                user_id,
                'Prova de Arquitetura de Computadores',
                'Prova bimestral: Pipeline, Hierarquia de Memória e Conjuntos de Instruções.',
                'Arquitetura de Computadores',
                'prova',
                '#dc2626', # Vermelho conforme especificado no PDF
                d1,
                '08:00',
                '10:00',
                '1d'
            ),
            (
                user_id,
                'Trabalho de Modelagem de Banco de Dados Relacional',
                'Entrega do DER, Modelo Lógico e script SQL de criação das tabelas e chaves estrangeiras.',
                'Modelagem de Banco de Dados',
                'entrega',
                '#16a34a', # Verde
                d2,
                '23:59',
                '23:59',
                '2d'
            ),
            (
                user_id,
                'Aula Prática de Laboratório de Engenharia',
                'Apresentação do protótipo funcional MVP do Sistema de Gerenciamento Acadêmico.',
                'Laboratório de Engenharia',
                'aula',
                '#2563eb', # Azul conforme especificado no PDF
                d3,
                '14:00',
                '17:30',
                '1h'
            ),
            (
                user_id,
                'Seminário de Engenharia de Software',
                'Discussão sobre microsserviços vs monólitos e boas práticas ágeis.',
                'Engenharia de Software',
                'trabalho',
                '#9333ea', # Roxo
                d4,
                '10:30',
                '12:00',
                'none'
            )
        ]

        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO events (user_id, title, description, discipline, event_type, color, event_date, start_time, end_time, reminder_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', demo_events)
        conn.commit()
    conn.close()
