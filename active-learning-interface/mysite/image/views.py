from django.shortcuts import render
from image.models import Image
from django.template.context import Context
from django.template import loader
from django.http import HttpResponse

def index(request):
    # on calling the page, get the next picture from the database
    image = Image.objects.next_image()
    context = {
        'images': image
    }

    #template = loader.get_template('proto/main.html')
    #return HttpResponse(template.render(context, request))
    return render(request, 'proto/main.html', context)

def password(request):
    return render(request, 'proto/changePassword.html')

def login(request):
    return render(request, 'proto/login.html')
