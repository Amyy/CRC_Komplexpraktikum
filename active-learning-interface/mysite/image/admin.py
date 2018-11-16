from django.contrib import admin

from .models import Image, Label, Probability, Userlabels

admin.site.register(Image)
admin.site.register(Label)
admin.site.register(Probability)
admin.site.register(Userlabels)
