import os
from pathlib import Path
import pymysql
import dj_database_url
from datetime import timedelta
pymysql.install_as_MySQLdb()

# Batasi jumlah thread BLAS/numpy (OpenBLAS/MKL) sebelum pandas ter-import.
# Di shared hosting, satu worker yang me-spawn puluhan thread bisa membanjiri
# CPU host dan membuat proses lain (termasuk sshd) gagal fork.
for _v in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS',
           'NUMEXPR_NUM_THREADS', 'VECLIB_MAXIMUM_THREADS'):
    os.environ.setdefault(_v, '1')

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 'django-insecure-_!6+r_5f(%pb6hbz3onm@0*j+(frmx1p@_w2gd!vef&mpwymik')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get(
    'ALLOWED_HOSTS', 'localhost,192.168.0.13,127.0.0.1').split(',')


def _env_bool(name, default='False'):
    """Baca boolean dari env: hanya literal 'True' yang dianggap benar."""
    return os.environ.get(name, default) == 'True'


# Keamanan produksi (memenuhi `manage.py check --deploy`).
# LiteSpeed mengakhiri TLS di depan aplikasi; skema asli dikirim lewat header
# X-Forwarded-Proto bila ada, dan jika tidak Django fallback ke wsgi.url_scheme.
# Semua saklar dikendalikan lewat env di .htaccess (SetEnv), jadi aman dimatikan
# lagi tanpa menyentuh kode.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = _env_bool('SECURE_SSL_REDIRECT')
SESSION_COOKIE_SECURE = _env_bool('SESSION_COOKIE_SECURE')
CSRF_COOKIE_SECURE = _env_bool('CSRF_COOKIE_SECURE')
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))
# HSTS hanya masuk akal bila > 0; subdomain/preload mengikuti saklarnya.
SECURE_HSTS_INCLUDE_SUBDOMAINS = SECURE_HSTS_SECONDS > 0 and _env_bool(
    'SECURE_HSTS_INCLUDE_SUBDOMAINS')
SECURE_HSTS_PRELOAD = SECURE_HSTS_SECONDS > 0 and _env_bool(
    'SECURE_HSTS_PRELOAD')

# Catatan: mengaktifkan SECURE_HSTS_PRELOAD hanya menandai situs *layak*
# preload (directif `; preload` di header). Pendaftaran ke daftar preload
# browser tetap langkah manual di https://hstspreload.org dan butuh waktu
# berhari-hari untuk dicabut — jadi hanya lakukan bila yakin HTTPS permanen.

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'apps',
    'phonenumber_field',
    'mathfilters',
    'tinymce',
    'django_user_agents',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'crum.CurrentRequestUserMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_auto_logout.middleware.auto_logout',
]

ROOT_URLCONF = 'core.urls'
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'
TEMPLATE_DIR = os.path.join(BASE_DIR, 'apps/templates')

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django_auto_logout.context_processors.auto_logout_client',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'sql_mode': 'traditional',
        },
        'NAME': os.environ.get('DB_NAME', 'integrated_system'),
        'USER': os.environ.get('DB_USER', 'root'),
        'PASSWORD': os.environ.get('DB_PASSWORD', ''),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}
if os.environ.get('DATABASE_URL'):
    DATABASES['default'] = dj_database_url.config(conn_max_age=600)

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Jakarta'

DATE_INPUT_FORMATS = ('%d/%m/%Y')

USE_I18N = True

USE_TZ = False

USE_L10N = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'apps/staticfiles/')
STATICFILES_DIRS = os.path.join(BASE_DIR, 'apps/static/'),
STATIC_URL = '/apps/static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/apps/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'apps/media/')

AUTH_USER_MODEL = 'apps.User'

AUTO_LOGOUT = {
    'IDLE_TIME': timedelta(minutes=15),
    'REDIRECT_TO_LOGIN_IMMEDIATELY': True,
    'MESSAGE': 'The session has expired. Please login again to continue.',
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.ksisolusi.com'
EMAIL_PORT = 465
EMAIL_HOST_USER = 'abc_is@ksisolusi.com'
EMAIL_HOST_NAME = 'ABC Integrated System'
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True

TINYMCE_DEFAULT_CONFIG = {
    "entity_encoding": "raw",
    "menubar": "file edit view insert format tools",
    "plugins": 'print preview paste importcss searchreplace autolink autosave save code visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists wordcount imagetools textpattern noneditable help charmap emoticons quickbars',
    "toolbar": "fullscreen preview | undo redo | bold italic forecolor backcolor | formatselect | image link | "
    "alignleft aligncenter alignright alignjustify | outdent indent |  numlist bullist checklist | fontsizeselect "
    "emoticons | ",
    "custom_undo_redo_levels": 50,
    "quickbars_insert_toolbar": False,
    "file_picker_callback": """function (cb, value, meta) {
        var input = document.createElement("input");
        input.setAttribute("type", "file");
        if (meta.filetype == "image") {
            input.setAttribute("accept", "image/*");
        }
        if (meta.filetype == "media") {
            input.setAttribute("accept", "video/*");
        }

        input.onchange = function () {
            var file = this.files[0];
            var reader = new FileReader();
            reader.onload = function () {
                var id = "blobid" + (new Date()).getTime();
                var blobCache = tinymce.activeEditor.editorUpload.blobCache;
                var base64 = reader.result.split(",")[1];
                var blobInfo = blobCache.create(id, file, base64);
                blobCache.add(blobInfo);
                cb(blobInfo.blobUri(), { title: file.name });
            };
            reader.readAsDataURL(file);
        };
        input.click();
    }""",
    "content_style": "body { font-family:Helvetica,Arial,sans-serif; font-size:14px }",
    "statusbar": False,
    "width": "75%",
}
