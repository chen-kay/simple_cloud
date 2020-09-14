"""
Django settings for cloud_ky project.

Generated by 'django-admin startproject' using Django 3.0.5.

For more information on this file, see
https://docs.djangoproject.com/en/3.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.0/ref/settings/
"""

import os

import environ

env = environ.Env()
# env = ENV
env.read_env('envs/%s.env' % os.getenv('DJANGO_ENV', 'local'))

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'h=ckzz%klqe@=l-ht2ysmtp6jpfx_!!paz@igdqo%9h5wg$y7_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*'])
CSRF_HEADER_NAME = 'CSRF_COOKIE'
LOGIN_URL = '/basis/login'
LOGOUT_URL = '/basis/logout'

CACHES = {'default': env.cache()}

DATABASES = {'default': env.db()}

BASE_LOG_DIR = os.path.join(BASE_DIR, "logs")
LOGGING = {
    # version 值只能为1
    'version': 1,
    # True 表示禁用loggers
    'disable_existing_loggers': False,
    # < 格式化 >
    'formatters': {
        # 详细的日志格式
        'standard': {
            'format':
            '[%(asctime)s][%(threadName)s:%(thread)d][task_id:%(name)s][%(filename)s:%(lineno)d]'  # noqa
            '[%(levelname)s][%(message)s]'
        },
        # 简单的日志格式
        'simple': {
            'format':
            '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]%(message)s'
        },
    },
    # 过滤器
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    # < 处理信息 >
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],  # 只有在Django debug为True时才在屏幕打印日志
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        # 默认的
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "info.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 3,  # 最多备份几个
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
        # 专门用来记错误日志
        'error': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件，自动切
            'filename': os.path.join(BASE_LOG_DIR, "error.log"),  # 日志文件
            'maxBytes': 1024 * 1024 * 50,  # 日志大小 50M
            'backupCount': 5,
            'formatter': 'standard',
            'encoding': 'utf-8',
        },
    },
    'loggers': {
        # 默认的logger应用如下配置
        'logs': {
            'handlers': ['default', 'console', 'error'],  # 上线之后可以把'console'移除
            'level': 'DEBUG',
            'propagate': True,  # 向不向更高级别的logger传递
        },
    },
}

FS_FRAMEWORK = {
    'DEFAULT_EXT_SIP_IP': env.str('DEFAULT_EXT_SIP_IP', 'auto-nat'),
    'DEFAULT_EXT_RTP_IP': env.str('DEFAULT_EXT_RTP_IP', 'auto-nat'),
    'DEFAULT_INTERNAL_SIP_PORT': env.str('DEFAULT_INTERNAL_SIP_PORT', '5060'),
    'DEFAULT_EXTERNAL_SIP_PORT': env.str('DEFAULT_EXTERNAL_SIP_PORT', '5080'),
    'DEFAULT_WS_BINDING': env.str('DEFAULT_WS_BINDING', ':5066'),
    'DEFAULT_WSS_BINDING': env.str('DEFAULT_WSS_BINDING', ':7443'),
    'DEFAULT_LISTEN_PORT': env.str('DEFAULT_LISTEN_PORT', '8021'),
    'DEFAULT_EVENT_IP': env.str('DEFAULT_EVENT_IP', '192.168.66.111'),
    'DEFAULT_EVENT_PORT': env.str('DEFAULT_EVENT_PORT', '8021'),
    'DEFAULT_RECORDING_PATH': env.str('DEFAULT_RECORDING_PATH', '/home'),
}

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'django_filters',
    'drf_yasg',
    'django_redis',
    'cloud.fs',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ],
}

ROOT_URLCONF = 'cloud_ky.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'cloud_ky.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")
