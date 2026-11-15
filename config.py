import os
import secrets

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

APP_ENV = os.environ.get('APP_ENV', 'development').strip().lower()
if APP_ENV == 'prod':
    APP_ENV = 'production'
SECRET_KEY = os.environ.get('SECRET_KEY')
if APP_ENV == 'production' and not SECRET_KEY:
    raise RuntimeError('Defina SECRET_KEY no ambiente de produção.')
SECRET_KEY = SECRET_KEY or secrets.token_hex(32)
ALLOW_GOOGLE_DEMO = os.environ.get('ALLOW_GOOGLE_DEMO', 'false').lower() == 'true'
SESSION_COOKIE_SECURE = APP_ENV == 'production'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB

ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx',
    'txt', 'md', 'zip', 'rar', '7z', 'png', 'jpg', 'jpeg'
}

# Google API Configurations
GOOGLE_CLIENT_ID = os.environ.get('GOOGLE_CLIENT_ID', '')
GOOGLE_CLIENT_SECRET = os.environ.get('GOOGLE_CLIENT_SECRET', '')
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

# SMTP opcional para envio seguro do link de redefinição de senha.
MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
MAIL_FROM = os.environ.get('MAIL_FROM', MAIL_USERNAME or 'no-reply@localhost')
PUBLIC_BASE_URL = os.environ.get('PUBLIC_BASE_URL', 'http://127.0.0.1:5000')
PASSWORD_RESET_MAX_AGE = 3600

ALLOWED_REMINDER_TYPES = {'none', 'at_time', '1h', '1d', '2d', '1w'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
