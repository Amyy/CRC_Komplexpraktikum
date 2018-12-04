from django.shortcuts import HttpResponse, render
from django.template import loader
# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader


from django.contrib.auth import authenticate, login

def index(request):
    return render(request, 'proto/main.html')
    #return HttpResponse("Hello, world. You're at the polls index.")

def password(request):
    return render(request, 'proto/changePassword.html')


def login(request):
    return render(request, 'proto/login.html')

"""
def login(request):
    return render(request, 'prototype/accounts/login.html')
"""

def startpage(request):
    return render(request, 'proto/startpage.html')


def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return render(request, 'proto/success.html')
    else:
        return render(request, 'proto/failure.html')
