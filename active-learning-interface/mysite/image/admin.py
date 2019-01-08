from django.contrib import admin

from .models import Image, Label, Userlabels

admin.site.register(Image)
admin.site.register(Label)
admin.site.register(Userlabels)
