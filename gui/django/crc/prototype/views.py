from django.shortcuts import HttpResponse, render
from django.template import loader
# Create your views here.


def index(request):
    #return HttpResponse('main.html')
    template = loader.get_template('templates/main.html')
    return HttpResponse(template)