from django.urls import path

from . import views

urlpatterns = [
    # get the main page
    # accessed via http://localhost:8000/prototype/main
    path('main', views.index, name='main'),
    # login page -> accessed via http://localhost:8000/prototype/
    #path('', views.login, name='login'),
    # change password
    # accessed via http://localhost:8000/prototype/password
    path('changePassword', views.password, name='changePassword'),
    #path('', views.index, name='index'),
    path('', views.startpage, name='startpage')
]