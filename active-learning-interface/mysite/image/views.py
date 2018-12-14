from django.shortcuts import render
#from image.models import *
from .models import Image, Label, Probability, Userlabels
from django.http import HttpResponse
import datetime


def index(request):
    # on calling the page, get the next picture from the database
    image = Image.objects.next_image()
    imagelabels = Probability.objects.get_image_labels(image)
    labels = Label.objects.all()

    context = {
        'image': image,
        'labels' : labels,
        'imageLabels' : imagelabels
    }
    return render(request, 'proto/main.html', context)

def password(request):
    return render(request, 'proto/changePassword.html')

def login(request):
    return render(request, 'proto/login.html')

def getSelectedLabels(request):
    print("in getSelectedLabels")


    return render(request, 'proto/main.html')

def annotations(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annotations'+ datetime.datetime.now().strftime("%y-%m-%d-%H-%M")+'.csv"'
    Userlabels.objects.write_csv(response)
    return response

def upload_probabilities(request):
    if request.method == 'POST':
        path = handle_uploaded_file(request.FILES['file'])
        Probability.objects.read_annotations(path)
    return index(request)

def handle_uploaded_file(f):
    path = 'uploads/' + datetime.datetime.now().strftime("%y-%m-%d-%H-%M") + '.csv'
    with open(path, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path