from django.db import models

class Image(models.Model):
    path = models.CharField(max_length=200)

    def __str__(self):
        return self.image_path


class Label(models.Model):
    images = models.ManyToManyField(Image)
    #author = models.ForeignKey()
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Probability(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    value = models.FloatField()

    def __str__(self):
        toString = 'for {} in image {} is {}'.format(self.label, self.image, self.value)
        return toString
