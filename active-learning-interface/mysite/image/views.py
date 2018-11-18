from django.shortcuts import render
from image.models import Image
from image.models import Probability

def index(request):
    # on calling the page, get the next picture from the database
    image = Image.objects.next_image()
    labels = Probability.objects.get_image_labels(image)
    context = {
        'image': image,
        'labels' : labels
    }
    return render(request, 'proto/main.html', context)

def password(request):
    return render(request, 'proto/changePassword.html')

def login(request):
    return render(request, 'proto/login.html')
