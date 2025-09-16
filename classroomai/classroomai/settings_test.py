# Django测试配置文件
import os
from .settings import *

# 测试数据库配置 - 使用SQLite内存数据库加速测试
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# 禁用缓存
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 简化密码验证器以加速测试
AUTH_PASSWORD_VALIDATORS = []

# 禁用日志记录以减少测试输出
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'null': {
            'class': 'logging.NullHandler',
        },
    },
    'root': {
        'handlers': ['null'],
    },
}

# 测试时使用本地时区
USE_TZ = False

# 禁用调试工具栏
if 'debug_toolbar' in INSTALLED_APPS:
    INSTALLED_APPS.remove('debug_toolbar')

if 'debug_toolbar.middleware.DebugToolbarMiddleware' in MIDDLEWARE:
    MIDDLEWARE.remove('debug_toolbar.middleware.DebugToolbarMiddleware')

# 静态文件设置
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# 邮件后端设置为控制台输出
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# 测试文件上传目录
import tempfile
MEDIA_ROOT = tempfile.mkdtemp()

# 加速测试的一些设置
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# 禁用迁移检查
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

# 在CI环境中禁用迁移
if os.environ.get('CI'):
    MIGRATION_MODULES = DisableMigrations()

# 测试特定设置
TEST_RUNNER = 'django.test.runner.DiscoverRunner'

# 覆盖某些设置以确保测试稳定性
SECRET_KEY = 'test-secret-key-only-for-testing'
DEBUG = False
ALLOWED_HOSTS = ['testserver', 'localhost', '127.0.0.1']

# REST Framework测试设置
REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {}

# Celery设置 - 在测试中同步执行任务
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

print("🧪 使用测试配置运行")