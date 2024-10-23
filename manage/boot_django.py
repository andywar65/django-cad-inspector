# File sets up the django environment, used by other scripts that need to
# execute in Django land

import sys
from pathlib import Path

import django
from django.conf import settings

BASE_DIR = Path(__file__).parent.parent / "src"
REPO_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))


def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        SECRET_KEY="django-insecure-@!g#+nmv6464ignk@+mjx(r^+7e0ne6h6!o5y#h@u1d+$38(+9",
        DEBUG=True,
        DATABASES={
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        },
        INSTALLED_APPS=(
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
            "colorfield",
            "cadinspector",
        ),
        CAD_BLOCK_BLACKLIST=[
            "*Model_Space",
        ],
        CAD_LAYER_BLACKLIST=[
            "Defpoints",
        ],
        TIME_ZONE="UTC",
        USE_TZ=True,
        ROOT_URLCONF="urls",
        STATIC_URL="/static/",
        STATIC_ROOT="/home/andywar65/django-cad-inspector/static",
        MEDIA_URL="/media/",
        MEDIA_ROOT="/home/andywar65/django-cad-inspector/media",
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [REPO_DIR / "project/project/templates"],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ],
        MIDDLEWARE=[
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ],
    )

    django.setup()
