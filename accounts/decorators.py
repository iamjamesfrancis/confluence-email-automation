from django.shortcuts import redirect


def login_redirect(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        else:
            return func(request, *args, **kwargs)

    return wrapper
