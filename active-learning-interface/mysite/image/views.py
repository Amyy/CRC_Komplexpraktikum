from django.shortcuts import render, redirect
from .models import Image, Label, Userlabels
from django.http import HttpResponse
import datetime
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.hashers import check_password


def getImage(request):
    if not request.session.get('image'):
        next_image = Image.objects.next_image(request.user)
    else:
        next_image = Image.objects.next_image(request.user, request.session.get('image'))
    request.session['image'] = next_image.id
    return next_image


def getPictureInformation(request, image, previous=False):
    if image == None:
        context = {
            'message': 'noPics'
        }
        return context
    imagelabels = Userlabels.objects.get_image_labels(image)
    labels = Label.objects.all()
    description = image.description()
    context = {
        'image': image,
        'labels': labels,
        'imageLabels': imagelabels,
        'description': description,
        'previous': previous
    }
    return context


def index(request):
    if not request.user.is_authenticated:
        return render(request, 'proto/login.html')
    next_image = getImage(request)
    context = getPictureInformation(request, next_image)
    try:
        message = context.get('message')
        if message == 'noPics':
            return render(request, 'proto/noPictures.html')
    except:
        pass
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
    if request.user.is_authenticated:
        return redirect("main")
    return render(request, 'proto/login.html')


def checkLogin(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        image = getImage(request)
        context = getPictureInformation(request, image)
        return render(request, 'proto/main.html', context)
    else:
        context = {
            'message': 'Wrong username or password'
        }
        return render(request, 'proto/login.html', context)


def setLabels(request, answers):
    user = request.user
    image = Image.objects.get(id=request.session.get('image'))
    Userlabels.objects.set_userlabels_str(image, user, answers)


def noIdea(request):
    image = Image.objects.get(id=request.session.get("image"))
    Userlabels.objects.set_uncertain(image, request.user, True)
    return render(request, 'proto/main.html', context=getPictureInformation(request, image))


def noIdeaPrevious(request):
    image = Image.objects.get(id=request.session.get('currentPicture'))
    Userlabels.objects.set_uncertain(image, request.user, True)
    return render(request, 'proto/main.html', context=getPictureInformation(request, image))


def noToolVisible(request):
    # if no tool is visible, just set all the selected labels to empty
    setLabels(request, answers="")
    context = getPictureInformation(request, Image.objects.get(id=request.session.get("image")))
    return render(request, 'proto/main.html', context)


def noToolPrevious(request):
    setLabels(request, answers="")
    context = getPictureInformation(request, Image.objects.get(id=request.session.get('currentPicture')))
    return render(request, 'proto/main.html', context)


def getSelectedLabels(request):
    # get the checked checkboxes
    for answer in request.POST.getlist('answer'):
        print(answer)
    setLabels(request, answers=request.POST.getlist('answer'))
    # TODO: get the next picture (not only the next description) and present it to the user
    next_image = getImage(request)
    context = getPictureInformation(request, next_image)
    return render(request, 'proto/main.html', context)


def getSelectedLabelsPrevious(request):
    for answer in request.POST.getlist('answer'):
        print(answer)
    setLabels(request, answers=request.POST.getlist('answer'))
    pictureBefore = Image.objects.get(id=request.session.get('currentPicture'))
    context = getPictureInformation(request, pictureBefore)
    return render(request, 'proto/main.html', context)


def goToPreviousImage(request):
    # save the current picture to be able to jump back
    request.session['currentPicture'] = request.session.get('image')
    image = Image.objects.get(id=request.session.get('image'))
    previous_image = Image.objects.previous_image(request.user, image)
    context = getPictureInformation(request, previous_image, previous=True)
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
        Userlabels.objects.read_annotations(path)
    return index(request)


def handle_uploaded_file(f):
    path = 'uploads/' + datetime.datetime.now().strftime("%y-%m-%d-%H-%M") + '.csv'
    with open(path, 'wb') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return path
