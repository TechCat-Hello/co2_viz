from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url  

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')    # 環境変数から取得
if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY is not set in the environment.")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG') == 'True'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS').split(',')
if '' in ALLOWED_HOSTS:  # 環境変数が設定されていない場合のデフォルト値を調整
    ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]']

# セッションのセキュリティ設定
SESSION_COOKIE_SECURE = True  # セッションIDをHTTPS経由でのみ送信

# CSRFトークンのセキュリティ設定
CSRF_COOKIE_SECURE = True  # CSRFトークンをHTTPS経由でのみ送信

#HTTPSを強制
SECURE_SSL_REDIRECT = True  # HTTPでアクセスするとHTTPSにリダイレクトされる

SECURE_HSTS_SECONDS = 31536000  # 1年間のHSTS有効期限
SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # サブドメインにもHSTSを適用
SECURE_HSTS_PRELOAD = True  # HSTSプリロードリストに追加

#ベースディレクトリにstaticfilesフォルダを作成、静的ファイルを保存
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'weatherco2app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'weatherco2project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS':  [BASE_DIR / 'templates'],    
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'weatherco2project.wsgi.application'


# もしHeroku環境であればPostgreSQLを使用し、ローカル開発環境であればSQLiteを使用
if os.getenv('DJANGO_ENV') == 'production':
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in the environment.")
    
    DATABASES = {
        'default': dj_database_url.config(default=DATABASE_URL)
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'C:/path/to/django/errors.log', 
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}
