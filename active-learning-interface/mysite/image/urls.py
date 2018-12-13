from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    # get the main page
    # accessed via http://localhost:8000/prototype/main
    path('main', views.index, name='main'),
    # login page -> accessed via http://localhost:8000/prototype/
    path('', views.login, name='login'),
    # change password
    # accessed via http://localhost:8000/prototype/password
    path('changePassword', views.password, name='changePassword'),
    # created a function in the view, so that the selected labels can get saved
    path('getSelectedLabels', views.getSelectedLabels, name='getSelectedLabels'),
    # get annotations csv file
    path('annotations', views.annotations, name='annotations'),
    # upload variance from NN
    path('upload', views.upload_probabilities),
    # download csv file for specified opset, op
    path('csv/<int:opset>/<int:op>/', views.download_csv)

]

