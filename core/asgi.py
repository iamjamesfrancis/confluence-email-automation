import os

from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from django.apps import apps
from django.conf import settings
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.authentication import AuthenticationMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
from channels.routing import ProtocolTypeRouter, URLRouter

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    # 'websocket': AllowedHostsOriginValidator(AuthMiddlewareStack(URLRouter(
    #
    # ))),
})

apps.populate(settings.INSTALLED_APPS)

from accounts.middleware import BasicAuthBackend
from .router import router


def get_application() -> FastAPI:
    app = FastAPI(
        title="Confluence Email Automation",
        debug=settings.DEBUG,
        openapi_url=''
    )
    app.add_middleware(
        AuthenticationMiddleware,
        backend=BasicAuthBackend(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.ALLOWED_HOSTS] or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router, prefix='/api')
    app.mount('', application)

    return app


app = get_application()
