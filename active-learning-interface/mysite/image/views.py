from django.shortcuts import render
from image.models import Image
from image.models import Probability, Label, Userlabels
from django.http import HttpResponse


def index(request):
    # on calling the page, get the next picture from the database
    image = Image.objects.next_image()
    imagelabels = Probability.objects.get_image_labels(image)
    labels = Label.objects.all()
    print(labels)
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
    print(request.POST)

    return render(request, 'proto/login.html')

def annotations(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annotations.csv"'
    Userlabels.objects.write_csv(response)
    return response
