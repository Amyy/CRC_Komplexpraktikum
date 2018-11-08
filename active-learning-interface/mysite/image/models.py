from django.db import models

class Image(models.Model):
    image_path = models.CharField(max_length=200)

    def __str__(self):
        return self.image_path


class Label(models.Model):
    images = models.ManyToManyField(Image)
    #author = models.ForeignKey()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name



