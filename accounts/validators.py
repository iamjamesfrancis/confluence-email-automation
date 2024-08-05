from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from email_validator import validate_email, EmailSyntaxError, EmailUndeliverableError
from fastapi import HTTPException
from starlette import status
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from accounts.tokens import forgot_password_token, account_activation_token



class OrganizationUniqueNameValidator:
    def __init__(self, min_length=3, max_length=15):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, uniqueName):
        if len(uniqueName) < self.min_length:
            raise ValidationError(
                _("Organization Unique Name must contain at least %(min_length)d characters."),
                code='unique_name_too_short',
                params={'min_length': self.min_length},
            )
        if len(uniqueName) > self.max_length:
            raise ValidationError(
                _("Organization Unique Name must contain at most %(max_length)d characters."),
                code='unique_name_too_long',
                params={'max_length': self.max_length},
            )
        if any(char.isnumeric() for char in uniqueName):
            raise ValidationError(
                _("Organization Unique Name must not contain any numbers."),
                code='unique_name_contains_number',
            )
        if any(char.isspace() for char in uniqueName):
            raise ValidationError(
                _("Organization Unique Name must not contain any spaces."),
                code='unique_name_contains_space',
            )
        if any(not char.isalnum() for char in uniqueName if char not in ('-',)):
            raise ValidationError(
                _("Organization Unique Name must not contain any special characters."),
                code='unique_name_contains_special',
            )


class PasswordValidator:
    def __init__(self, min_length=8):
        self.min_length = min_length

    def validate(self, password, email=None):
        if len(password) < self.min_length:
            raise ValidationError(
                _("This password must contain at least %(min_length)d characters."),
                code='password_too_short',
                params={'min_length': self.min_length},
            )
        if not any(char.isupper() for char in password):
            raise ValidationError(
                _("This password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not any(char.isnumeric() for char in password):
            raise ValidationError(
                _("This password must contain at least one number."),
                code='password_no_number',
            )
        if not any(not char.isalnum() for char in password):
            raise ValidationError(
                _("This password must contain at least one special character."),
                code='password_no_special',
            )
        if email is not None:
            email_lower = email.lower()
            password_lower = password.lower()
            if email_lower in password_lower:
                raise ValidationError(
                    _("This password must not contain your email."),
                    code='password_contains_email',
                )
            if email_lower.split('@')[0] in password_lower:
                raise ValidationError(
                    _("This password must not contain your username."),
                    code='password_contains_username',
                )

    def get_help_text(self):
        return _(
            "Your password must contain at least %(min_length)d characters."
            % {'min_length': self.min_length}
        )


# def is_signup_valid(response: UserSignupSchema):
#     """
#     Required Fields:
#     email: str
#     password: str
#     organization_name: str
#     organization_id: str
#
#     :param response: UserSignupSchema
#     :return: boolean/HTTPException
#     """
#     if response.email is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email is required')
#     else:
#         if User.objects.filter(email=response.email).exists():
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email already exists')
#         try:
#             validate_email(response.email)
#         except EmailSyntaxError as error:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{error}')
#         except EmailUndeliverableError as error:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{error}')
#     if response.password is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Password is required')
#     else:
#         try:
#             PasswordValidator(min_length=settings.PASSWORD_MIN_LENGTH).validate(response.password, email=response.email)
#         except ValidationError as error:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{list(error)[0]}')
#
#     if response.organization_name is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Organization Name is required')
#     if response.organization_id is None:
#         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Organization ID is required')
#     else:
#         if Organization.objects.filter(unique_name=response.organization_id).exists():
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
#                                 detail='Organization ID already exists')
#         try:
#             OrganizationUniqueNameValidator(min_length=settings.ORGANIZATION_UNIQUE_NAME_MIN_LENGTH).validate(
#                 response.organization_id)
#         except ValidationError as error:
#             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{list(error)[0]}')
#     return True


def is_account_activation_link_valid(uidb64: str, token: str):
    try:
        user_id = urlsafe_base64_decode(uidb64).decode()
        if User.objects.filter(pk=user_id).exists():
            user = User.objects.get(pk=user_id)
            if account_activation_token.check_token(user, token):
                account_activation_token.make_token(user)
                return True
            else:
                raise HTTPException(
                    status_code=400,
                    detail='Invalid activation link'
                )
        else:
            raise HTTPException(
                status_code=400,
                detail='Invalid activation link'
            )
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail=f'Link is broken'
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f'Link is broken'
        )


def is_forgot_password_link_valid(uidb64: str, token: str):
    user_id = urlsafe_base64_decode(uidb64).decode()
    if User.objects.filter(pk=user_id).exists():
        user = User.objects.get(pk=user_id)
        if forgot_password_token.check_token(user, token):
            return True
        else:
            raise HTTPException(
                status_code=400,
                detail='Invalid link'
            )
    else:
        raise HTTPException(
            status_code=400,
            detail='Invalid link'
        )
