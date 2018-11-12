from django.db import models
from django.contrib.auth.models import User
import numpy



class gui_image_manager(models.Manager):
    def set_labels(self, image, label_set = []):
        image.label_set.set(label_set)
        image.save()
#        image.label_set.clear()
#        for label in label_set:
#            image.label_set.add(label)

    def next_image(self):
        return self.order_by('variance').first()

    def get_labels(self, image):
        return image.label_set.all()


class gui_probability_manager(models.Manager):
    def calc_variance(self, image):
        probabilities = self.filter(image=image).values_list('value')
        prob_values = [p[0] for p in probabilities]
        if len(prob_values) < 1:
            print ('calc_variance: No probability values.')
            return
        variance = numpy.var(prob_values)
        image.variance = variance
        image.save()



class Image(models.Model):
    name = models.CharField(max_length=200)
    variance = models.FloatField()
    data = models.ImageField()

    objects = models.Manager()
    gui = gui_image_manager()

    def __str__(self):
        return self.name



class Label(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Userlabels(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label = models.ManyToManyField(Label)

    def __str__(self):
        toString = 'Picture {} by {}'.format(self.image, self.author)
        return toString


class Probability(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    value = models.FloatField()

    objects = models.Manager()
    gui = gui_probability_manager()

    def __str__(self):
        toString = '{} labeled {} with certainty {}'.format(self.image, self.label, self.value)
        return toString
