import jwt
from django.conf import settings
from django.contrib.auth.models import User, AnonymousUser
from rest_framework.request import Request
from starlette.authentication import AuthenticationBackend, AuthCredentials, AuthenticationError


def authentication_middleware(get_response):
    def middleware(request: Request):
        try:
            payload = jwt.decode(request.COOKIES.get('jwt_token'), settings.SECRET_KEY,
                                 algorithms=['HS256'])
            user = User.objects.get(pk=payload.get('id'))
            request.user = user
        except Exception as e:
            request.user = AnonymousUser()

        response = get_response(request)
        return response

    return middleware


class BasicAuthBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if conn.cookies.get('jwt_token') is None:
            return

        token = conn.cookies.get('jwt_token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY,
                                 algorithms=['HS256'])
            user = await User.objects.aget(pk=payload.get('id'))
        except Exception:
            raise AuthenticationError("Invalid Credentials")

        # TODO: You'd want to verify the username and password here.
        return AuthCredentials(["authenticated"]), user
