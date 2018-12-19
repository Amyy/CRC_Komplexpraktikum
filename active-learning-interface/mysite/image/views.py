from django.shortcuts import render
from .models import Image, Label, Probability, Userlabels
from django.http import HttpResponse
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password


def getPictureInformation():
    image = Image.objects.next_image()
    imagelabels = Probability.objects.get_image_labels(image)
    labels = Label.objects.all()
    description = image.description()
    context = {
        'image': image,
        'labels': labels,
        'imageLabels': imagelabels,
        'description': description
    }
    return context


def index(request):
    # on calling the page, get the next picture from the database
    context = getPictureInformation()
    return render(request, 'proto/main.html', context)


def showChangePassword(request):
    return render(request, 'proto/changePassword.html')


def changePassword(request):
    user = User.objects.get(username=request.user.username)
    currentpassword = request.user.password
    enteredcurrentpasword = request.POST.get('oldPassword')
    newPassword = request.POST.get('newPassword')
    newPasswordCheck = request.POST.get('confirmNew')
    matchcheck = check_password(enteredcurrentpasword, currentpassword)

    if not matchcheck and enteredcurrentpasword:
        context = {
            "message": "wrongOldPassword"
        }
        return render(request, 'proto/changePassword.html', context)
    if not enteredcurrentpasword or not newPassword or not newPasswordCheck:
        context = {
            "message": "empty"
        }
        return render(request, 'proto/changePassword.html', context)

    if newPassword == newPasswordCheck and matchcheck:
        user.set_password(newPassword)
        user.save()
        update_session_auth_hash(request, user)
        return render(request, 'proto/changedPassword.html')
    elif newPassword and newPasswordCheck:
        context = {
            'message': 'passwordNoMatch'
        }
        return render(request, 'proto/changePassword.html', context)
    else:
        context = {
            'message': ''
        }
        return render(request, 'proto/changePassword.html', context)


def logout_view(request):
    logout(request)
    return render(request, 'proto/logged_out.html')


def showLogin(request):
    return render(request, 'proto/login.html')


def checkLogin(request):
    # TODO: Reaktion, wenn Nutzer falsches Passwort eingegeben hat

    username = request.POST.get('username')
    print("user", username)
    password = request.POST.get('password')
    print("password", password)
    user = authenticate(request, username=username, password=password)
    print("user", user )

    if user is not None:
        login(request, user)
        context = getPictureInformation()
        return render(request, 'proto/main.html', context)
    else:
        print("not success with login")
        context = {
            'message' : 'Wrong username or password'
        }
        return render(request, 'proto/login.html', context)



def setLabels(request, answers):
    user = request.user
    image = Image.objects.next_image()  # should get the current picture, as there are no labels set to the current one
    Userlabels.objects.set_userlabels_str(image, user, answers)


def noIdea(request):
    print("in no idea")
    return render(request, 'proto/main.html', context=getPictureInformation())


def noToolVisible(request):
    print("no tool visible")
    setLabels(request, answers="")
    context = getPictureInformation()
    return render(request, 'proto/main.html', context)


def getSelectedLabels(request):
    # get the checked checkboxes
    for answer in request.POST.getlist('answer'):
        print(answer)
    setLabels(request, answers=request.POST.getlist('answer'))
    # TODO: get the next picture and present it to the user
    context = getPictureInformation()
    return render(request, 'proto/main.html', context)


def annotations(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annotations' + datetime.datetime.now().strftime(
        "%y-%m-%d-%H-%M") + '.csv"'
    Userlabels.objects.write_csv(response)
    return response


def download_csv(request, opset, op):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="annotations-' + str(opset) + '-' + str(op) + '.csv"'
    Userlabels.objects.generate_csv(response, opset, op)
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
