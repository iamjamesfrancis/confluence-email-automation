import jwt
from django.conf import settings
from django.contrib.auth.models import User
from fastapi import Request, HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def token_authentication(token: Request) -> User:
    try:
        payload = jwt.decode(token.cookies.get('jwt_token'), settings.SECRET_KEY, algorithms=['HS256'])
        user = User.objects.get(pk=payload.get('id'))
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password'
        )
    return user
