from django.shortcuts import HttpResponse, render
from django.template import loader
# Create your views here.
from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    #return HttpResponse('main.html')
    #template = loader.get_template('main.html')
    #return HttpResponse(template)
    #template = loader.get_template("proto/main.html")
    #return HttpResponse(template.render())
    return render(request, 'proto/main.html')

   # return HttpResponse("Hello World")