
from datetime import timedelta, datetime

from django.template.loader import render_to_string
from fastapi import APIRouter, BackgroundTasks, Depends, Response, Request, Cookie, HTTPException
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from fastapi import APIRouter
from fastapi import status
from starlette.responses import JSONResponse

from .responses import *

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from fastapi import APIRouter, BackgroundTasks, Depends, Response, Request, Cookie, HTTPException
from django.db import transaction
from accounts.tokens import account_activation_token, forgot_password_token
from accounts.validators import *
from .serializers import *


def activate(uidb64: str, token: str):
    if is_account_activation_link_valid(uidb64, token):
        user = User.objects.get(pk=urlsafe_base64_decode(uidb64))
        user.is_active = True
        user.save()
        return {'detail': 'Account activated successfully'}


def resend_activate_email(uidb64: str, token: str):
    return {'detail': 'Account activated successfully'}


def login(body: dict, response: Response):
    if 'username' in body and 'password' in body:
        user = authenticate(username=body['username'], password=body['password'])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid username or password'
            )
        TIME_SPAN_IN_HOURS = 168
        token = jwt.encode({
            'id': user.id,
            'username': user.username,
            'exp': datetime.utcnow() + timedelta(hours=TIME_SPAN_IN_HOURS)

        }, settings.SECRET_KEY, algorithm='HS256')
        if settings.DEBUG:
            response.set_cookie(key='jwt_token', value=token, expires=int(3600 * TIME_SPAN_IN_HOURS))
        else:
            response.set_cookie(key='jwt_token', value=token, expires=int(3600 * TIME_SPAN_IN_HOURS), secure=True,
                                httponly=True,
                                samesite='strict')
        return {'detail': 'Login successful', }
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'username' and 'password' are required"
        )


def send_reset_password_email(body: dict, request: Request):
    if 'email' in body:
        if User.objects.filter(email=body['email']).exists():
            return {'detail': 'Email sent successfully'}
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email doesn't exist"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'email' is required"
        )


def check_password_reset_link(uidb64: str, token: str):
    if is_forgot_password_link_valid(uidb64, token):
        return {'detail': 'Valid link'}


def check_password_reset(body: dict, uidb64: str, token: str):
    if 'password' in body:
        if is_forgot_password_link_valid(uidb64, token):
            user = User.objects.get(pk=urlsafe_base64_decode(uidb64))
            user.set_password(body['password'])
            user.save()
            print('password reset successfully')
            forgot_password_token.make_token(user)
            return {'detail': 'Password reset successfully'}
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="'password' is required"
        )


def update_profile(user: dict, request: Request):
    if User.objects.filter(pk=request.user.pk).exists():
        if User.objects.filter(username=user['username']).exclude(pk=request.user.pk).exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        user_instance = User.objects.get(pk=request.user.pk)
        data = UserSerializer(user_instance, data=user)
        if data.is_valid():
            data.save()
            return data.data
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=data.errors
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User doesn't exist"
        )
