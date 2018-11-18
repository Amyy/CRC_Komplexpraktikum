from django.shortcuts import render



def index(request):
    return render(request, 'proto/main.html')

def password(request):
    return render(request, 'proto/changePassword.html')

def login(request):
    return render(request, 'proto/login.html')
