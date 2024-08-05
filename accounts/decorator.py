from functools import wraps

from fastapi.responses import JSONResponse
from starlette import status


def permission_required(func):
    @wraps(func)
    def wrapper(permission: list, *args, **kwargs):
        requests = kwargs.get('request')
        if requests.user.has_perms(permission):
            return func(*args, **kwargs)
        else:
            return JSONResponse(
                status_code=403,
                content={
                    'detail': 'You do not have permission to perform this action'
                }
            )

    return wrapper


def super_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        requests = kwargs.get('request')
        if requests.user.is_superuser:
            return func(*args, **kwargs)
        else:
            return JSONResponse(
                status_code=403,
                content={
                    'detail': 'You do not have permission to perform this action'
                }
            )

    return wrapper


def organization_check(func):
    @wraps(func)
    def wrapper(organization_id: str, *args, **kwargs):
        requests = kwargs.get('request')
        if requests.user.organization_set.filter(unique_name=organization_id).exists():
            return func(*args, **kwargs, organization_id=organization_id)
        else:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    'detail': 'You do not have permission to perform this action'
                }
            )

    return wrapper
