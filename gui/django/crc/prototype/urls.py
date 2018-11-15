from django.urls import path

from . import views

urlpatterns = [
    # get the main page
    # accessed via http://localhost:8000/prototype/main
    path('main', views.index, name='index'),
    # login page -> accessed via http://localhost:8000/prototype/
    path('', views.login, name='login'),
    # change password
    # accessed via http://localhost:8000/prototype/password
    path('changePassword', views.password, name='changePassword')
]