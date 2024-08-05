from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

from accounts.decorators import login_redirect


@login_required(login_url='login')
def home(request):
    return render(request, 'index.html')


@login_redirect
def login_user(request):
    return render(request, 'index.html')
