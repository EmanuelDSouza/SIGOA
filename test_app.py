import unittest
import os
import json
import io
import shutil
import tempfile
from unittest.mock import patch
from werkzeug.security import generate_password_hash, check_password_hash
from app import app
import app as app_module
import database as db
import config

class SIGOATestCase(unittest.TestCase):
    def setUp(self):
        # Usa banco exclusivo de testes para jamais interferir no banco de produção
        fd, self.test_db_path = tempfile.mkstemp(prefix='sigoa-test-', suffix='.db')
        os.close(fd)
        db.DB_PATH = self.test_db_path
        self.previous_upload_folder = app.config['UPLOAD_FOLDER']
        self.upload_dir = tempfile.mkdtemp(prefix='sigoa-uploads-test-')
        app.config['UPLOAD_FOLDER'] = self.upload_dir
        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-key'
        self.previous_demo_setting = config.ALLOW_GOOGLE_DEMO
        self.previous_app_env = config.APP_ENV
        config.ALLOW_GOOGLE_DEMO = False
        config.APP_ENV = 'development'
        self.client = app.test_client()
        db.init_db()
        conn = db.get_db_connection()
        conn.execute('DELETE FROM user_files')
        conn.execute('DELETE FROM events')
        conn.execute('DELETE FROM users')
        conn.commit()
        conn.close()

    def tearDown(self):
        # Restaura DB_PATH
        db.DB_PATH = os.path.join(os.path.dirname(__file__), 'academico.db')
        config.ALLOW_GOOGLE_DEMO = self.previous_demo_setting
        config.APP_ENV = self.previous_app_env
        app.config['UPLOAD_FOLDER'] = self.previous_upload_folder
        shutil.rmtree(self.upload_dir, ignore_errors=True)
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)

    def test_auth_and_registration(self):
        weak = self.client.post('/register', data={
            'name': 'Aluno Senha Fraca', 'email': 'fraca@faculdade.edu.br',
            'password': '1234567', 'confirm_password': '1234567'
        })
        self.assertEqual(weak.status_code, 200)
        self.assertIsNone(db.get_user_by_email('fraca@faculdade.edu.br'))

        # 1. Registrar novo estudante
        res = self.client.post('/register', data={
            'name': 'Aluno Teste',
            'email': 'teste@faculdade.edu.br',
            'password': 'senha123',
            'confirm_password': 'senha123'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 2. Verificar se usuário existe no banco
        user = db.get_user_by_email('teste@faculdade.edu.br')
        self.assertIsNotNone(user)
        self.assertEqual(user['name'], 'Aluno Teste')
        self.assertNotEqual(user['password_hash'], 'senha123')
        self.assertTrue(check_password_hash(user['password_hash'], 'senha123'))
        self.assertEqual(db.get_events_by_user(user['id']), [])
        self.assertEqual(db.get_files_by_user(user['id']), [])

    def test_events_crud_and_google_url(self):
        # Cria usuário e loga via sessão
        with self.client.session_transaction() as sess:
            user_id = db.create_user('Yuri Dev', 'yuri@dev.com', 'hash123')
            sess['user_id'] = user_id
            sess['user_name'] = 'Yuri Dev'
            sess['user_email'] = 'yuri@dev.com'

        # 1. Criar Evento Acadêmico (Prova de Arquitetura de Computadores)
        res = self.client.post('/api/events', json={
            'title': 'Prova de Arquitetura de Computadores',
            'description': 'Estudar pipeline e cache',
            'discipline': 'Arquitetura de Computadores',
            'event_type': 'prova',
            'color': '#dc2626',
            'event_date': '2026-09-15',
            'start_time': '08:00',
            'end_time': '10:00',
            'reminder_type': '1d'
        })
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        event_id = data['id']
        self.assertIn('google_calendar_url', data)
        self.assertIn('calendar.google.com', data['google_calendar_url'])

        invalid_reminder = self.client.post('/api/events', json={
            'title': 'Lembrete inválido', 'event_date': '2026-09-15',
            'reminder_type': '10m'
        })
        self.assertEqual(invalid_reminder.status_code, 400)

        # 2. Listar Eventos
        res = self.client.get('/api/events')
        self.assertEqual(res.status_code, 200)
        events = res.get_json()
        self.assertTrue(any(e['id'] == event_id for e in events))

        # 3. Atualizar Evento
        res = self.client.post(f'/api/events/{event_id}', json={
            'title': 'Prova de Arquitetura (Alterada)',
            'event_date': '2026-09-16',
            'event_type': 'prova',
            'color': '#dc2626',
            'is_completed': 1
        })
        self.assertEqual(res.status_code, 200)
        updated = res.get_json()
        self.assertEqual(updated['title'], 'Prova de Arquitetura (Alterada)')
        self.assertEqual(updated['is_completed'], 1)

        # 4. Deletar Evento
        res = self.client.delete(f'/api/events/{event_id}')
        self.assertEqual(res.status_code, 200)

    def test_file_upload_per_user(self):
        # Usuário autenticado
        with self.client.session_transaction() as sess:
            user_id = db.create_user('Maria Silva', 'maria@faculdade.edu.br', 'hash123')
            sess['user_id'] = user_id
            sess['user_name'] = 'Maria Silva'
            sess['user_email'] = 'maria@faculdade.edu.br'

        # Upload de arquivo acadêmico
        test_file_data = io.BytesIO(b"Conteudo do trabalho de Engenharia de Software")
        res = self.client.post('/api/files/upload', data={
            'file': (test_file_data, 'trabalho_laboratorio.pdf')
        }, content_type='multipart/form-data')
        self.assertEqual(res.status_code, 201)
        file_info = res.get_json()
        file_id = file_info['id']

        # Listar arquivos do usuário
        res = self.client.get('/api/files')
        self.assertEqual(res.status_code, 200)
        files = res.get_json()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0]['original_filename'], 'trabalho_laboratorio.pdf')

        # Download do arquivo
        res = self.client.get(f'/api/files/{file_id}/download')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b"Conteudo do trabalho de Engenharia de Software")
        res.close()

        # Excluir arquivo
        file_record = db.get_file_by_id(file_id, user_id)
        stored_path = os.path.join(app.config['UPLOAD_FOLDER'], file_record['stored_filename'])
        self.assertTrue(os.path.exists(stored_path))
        res = self.client.delete(f'/api/files/{file_id}')
        self.assertEqual(res.status_code, 200)
        self.assertFalse(os.path.exists(stored_path))

    def test_multi_user_isolation(self):
        # Usuário 1 cria evento e envia arquivo
        u1_id = db.create_user('Usuario 1', 'u1@faculdade.edu.br', 'senha1')
        u1_ev_id = db.create_event(u1_id, 'Evento Privado U1', '', 'Calculo 1', 'prova', '#dc2626', '2026-09-20')
        u1_file_id = db.save_file_record(u1_id, 'gabarito_privado.pdf', 'stored_u1.pdf', 1024, 'pdf', u1_ev_id)

        # Usuário 2 faz login
        u2_id = db.create_user('Usuario 2', 'u2@faculdade.edu.br', 'senha2')
        with self.client.session_transaction() as sess:
            sess['user_id'] = u2_id
            sess['user_name'] = 'Usuario 2'
            sess['user_email'] = 'u2@faculdade.edu.br'

        # Usuário 2 consulta eventos - não deve ver o evento do U1
        res = self.client.get('/api/events')
        events = res.get_json()
        self.assertFalse(any(e['id'] == u1_ev_id for e in events))

        # Usuário 2 consulta arquivos - não deve ver o arquivo do U1
        res = self.client.get('/api/files')
        files = res.get_json()
        self.assertFalse(any(f['id'] == u1_file_id for f in files))

        # Usuário 2 tenta baixar o arquivo do U1 - deve receber 404
        res = self.client.get(f'/api/files/{u1_file_id}/download')
        self.assertEqual(res.status_code, 404)

    def test_google_auth_and_forgot_password(self):
        # Teste de login Google Demo
        self.assertNotIn('Entrar com conta de demonstração', self.client.get('/login').get_data(as_text=True))
        config.ALLOW_GOOGLE_DEMO = True
        self.assertIn('Entrar com conta de demonstração', self.client.get('/login').get_data(as_text=True))
        res = self.client.post('/auth/google', json={
            'demo': True,
            'email': 'estudante.google@faculdade.edu.br',
            'name': 'Estudante Google Test'
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data['success'])
        demo_user = db.get_user_by_email('estudante.google@faculdade.edu.br')
        self.assertEqual(db.get_events_by_user(demo_user['id']), [])
        self.assertEqual(db.get_files_by_user(demo_user['id']), [])

        # Recuperação não revela se o endereço existe nem troca a senha sem token.
        forgot = self.client.post('/auth/forgot-password', json={
            'email': 'estudante.google@faculdade.edu.br'
        })
        self.assertEqual(forgot.status_code, 503)
        self.assertIn('serviço de e-mail não configurado', forgot.get_json()['message'])
        self.assertIsNone(db.get_user_by_email('estudante.google@faculdade.edu.br')['password_hash'])

    def test_google_demo_rejected_when_disabled(self):
        res = self.client.post('/auth/google', json={
            'demo': True, 'email': 'nao-autorizado@example.edu', 'name': 'Teste'
        })
        self.assertEqual(res.status_code, 403)
        self.assertIsNone(db.get_user_by_email('nao-autorizado@example.edu'))

    def test_password_reset_token_is_single_use_and_response_is_neutral(self):
        reset_page = self.client.get('/reset-password?token=exemplo')
        self.assertEqual(reset_page.status_code, 200)
        self.assertEqual(reset_page.headers['Cache-Control'], 'no-store')
        self.assertEqual(reset_page.headers['Referrer-Policy'], 'no-referrer')
        user_id = db.create_user(
            'Aluno Senha', 'senha@faculdade.edu.br', generate_password_hash('SenhaAntiga123')
        )
        user = db.get_user_by_id(user_id)
        captured_tokens = []
        with patch.object(config, 'MAIL_SERVER', 'smtp.example.edu'), \
             patch.object(app_module, 'send_password_reset_email',
                          side_effect=lambda account, token: captured_tokens.append(token)):
            known = self.client.post('/auth/forgot-password', json={'email': user['email']})
            unknown = self.client.post('/auth/forgot-password', json={'email': 'ausente@example.edu'})

        self.assertEqual(known.status_code, 202)
        self.assertEqual(known.get_json()['message'], unknown.get_json()['message'])
        self.assertEqual(len(captured_tokens), 1)
        token = captured_tokens[0]
        with patch.object(config, 'MAIL_SERVER', 'smtp.example.edu'), \
             patch.object(app_module, 'send_password_reset_email', side_effect=OSError('SMTP offline')):
            with self.assertLogs(app_module.app.logger, level='ERROR'):
                failed_delivery = self.client.post('/auth/forgot-password', json={'email': user['email']})
                absent_delivery = self.client.post('/auth/forgot-password', json={'email': 'ausente2@example.edu'})
        self.assertEqual(failed_delivery.status_code, absent_delivery.status_code)
        self.assertEqual(failed_delivery.get_json()['message'], absent_delivery.get_json()['message'])

        too_short = self.client.post('/auth/reset-password', json={
            'token': token, 'password': 'curta', 'confirm_password': 'curta'
        })
        self.assertEqual(too_short.status_code, 400)
        with patch.object(config, 'PASSWORD_RESET_MAX_AGE', -1):
            expired = self.client.post('/auth/reset-password', json={
                'token': token, 'password': 'SenhaValida123', 'confirm_password': 'SenhaValida123'
            })
        self.assertEqual(expired.status_code, 400)
        reset = self.client.post('/auth/reset-password', json={
            'token': token, 'password': 'NovaSenha123', 'confirm_password': 'NovaSenha123'
        })
        self.assertEqual(reset.status_code, 200)
        self.assertTrue(check_password_hash(db.get_user_by_id(user_id)['password_hash'], 'NovaSenha123'))
        replay = self.client.post('/auth/reset-password', json={
            'token': token, 'password': 'OutraSenha123', 'confirm_password': 'OutraSenha123'
        })
        self.assertEqual(replay.status_code, 400)

    def test_lgpd_compliance(self):
        # Cria usuário para teste LGPD
        u_id = db.create_user('Aluno LGPD', 'lgpd@faculdade.edu.br', 'senha_forte')
        db.create_event(u_id, 'Evento LGPD', '', 'Direito Digital', 'aula', '#2563eb', '2026-09-22')
        stored_name = 'lgpd_test_attachment.pdf'
        stored_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_name)
        with open(stored_path, 'wb') as attachment:
            attachment.write(b'anexo de teste')
        db.save_file_record(u_id, 'anexo.pdf', stored_name, 14, 'pdf')
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = u_id
            sess['user_name'] = 'Aluno LGPD'
            sess['user_email'] = 'lgpd@faculdade.edu.br'

        # 1. Teste de Portabilidade (Art. 18, V)
        res = self.client.get('/api/user/export-data')
        self.assertEqual(res.status_code, 200)
        exported = res.get_json()
        self.assertEqual(exported['perfil']['email'], 'lgpd@faculdade.edu.br')
        self.assertEqual(len(exported['compromissos_academicos']), 1)

        # 2. Teste de Eliminação / Direito ao Esquecimento (Art. 18, VI)
        res = self.client.post('/api/user/delete-account')
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(db.get_user_by_id(u_id))
        self.assertEqual(len(db.get_events_by_user(u_id)), 0)
        self.assertFalse(os.path.exists(stored_path))

if __name__ == '__main__':
    unittest.main()
