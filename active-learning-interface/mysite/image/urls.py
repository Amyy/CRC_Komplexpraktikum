from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # get the main page
    # accessed via http://localhost:8000/prototype/main
    path('main', views.index, name='main'),
    # login page -> accessed via http://localhost:8000/prototype/
    path('', views.showLogin, name='login'),
    path('checkLogin', views.checkLogin, name="checkLogin"),
    path('logout_view', views.logout_view, name="logout_view"),
    # change password
    # accessed via http://localhost:8000/prototype/password
    path('showChangePassword', views.showChangePassword, name="showChangePassword"),
    path('changePassword', views.changePassword, name='changePassword'),
    path('getSelectedLabels', views.getSelectedLabels, name='getSelectedLabels'),
    path('goToPreviousImage', views.goToPreviousImage, name='goToPreviousImage'),
    path('noTools', views.noToolVisible, name='noTools'),
    path('dontKnow', views.noIdea, name="noIdea"),
    # get annotations csv file
    path('annotations', views.annotations, name='annotations'),
    # upload variance from NN
    path('upload', views.upload_probabilities),
    # download csv file for specified opset, op
    path('csv/<int:opset>/<int:op>/', views.download_csv)


]

