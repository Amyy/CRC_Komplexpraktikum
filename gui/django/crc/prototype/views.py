from django.shortcuts import HttpResponse, render
from django.template import loader
# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    return render(request, 'proto/main.html')

def password(request):
    return render(request, 'proto/changePassword.html')

def login(request):
    return render(request, 'proto/login.html')