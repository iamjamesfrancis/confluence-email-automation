import time
from datetime import timedelta

from fastapi import APIRouter, BackgroundTasks, Depends, Response, Request, Cookie, HTTPException
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from fastapi import APIRouter
from fastapi import status
from starlette.authentication import requires

from .decorator import permission_required
from .responses import *

router = APIRouter()


# Login
@router.post("/login", tags=['accounts'], name='login/')
def user_login(body: dict, response: Response):
    return login(body, response)


# Logout
@router.get("/logout", tags=['accounts'])
@requires('authenticated', status_code=status.HTTP_401_UNAUTHORIZED)
def logout(request: Request, response: Response):
    response.delete_cookie('jwt_token')
    return {'detail': 'Logout successful'}
