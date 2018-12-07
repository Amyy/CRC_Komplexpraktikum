from django.db import models
from django.contrib.auth.models import User
import numpy
import csv


class image_manager(models.Manager):
    def set_userlabels(self, image, label_set = []):
        image.label_set.set(label_set)
        image.save()


    def next_image(self):
        return self.order_by('variance', '-count_userlabels').last()


class probability_manager(models.Manager):
    def calc_variance(self, image):
        probabilities = self.filter(image=image).values_list('value')
        prob_values = [p[0] for p in probabilities]
        if len(prob_values) < 1:
            print ('calc_variance: No probability values.')
            return
        variance = numpy.var(prob_values)
        image.variance = variance
        image.save()

    def get_image_labels(self, image):
        im_prob = self.filter(image=image)

        thr_labels = []
        for prob in im_prob:
            if prob.value > Probability.THRESHOLD:
                thr_labels.append(prob.label)
        return thr_labels

    def set_probabilities(self, image, probabilities = []):
        self.filter(image=image).delete()
        labels = Label.objects.all()
        probabilities = list(zip(labels, probabilities))
        for prob in probabilities:
            probability = Probability(image=image, label=prob[0], value=prob[1])
            probability.save()

    def read_annotations(self, path):
        with open(path, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            for row in csvreader:
                print (', '.join(row))


class userlabels_mangager(models.Manager):
    def set_userlabels(self, image, user, label_set = []):
        userlabels = Userlabels(image = image, author = user)
        userlabels.save()
        for label in label_set:
            userlabels.label.add(label)
        userlabels.save()
        image.count_userlabels = self.countLabels(image)
        image.save()


    def countLabels(self, image):
        return self.filter(image=image).count()


    def write_csv(self, csvfile):
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        ul_all = self.all()
        for userlabel in ul_all:
            spamwriter.writerow([userlabel.image.name] + userlabel.get_labels())


class Image(models.Model):
    name = models.CharField(max_length=200)
    variance = models.FloatField()
    data = models.ImageField()
    count_userlabels = models.IntegerField()

    objects = image_manager()

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
    objects = userlabels_mangager()

    def __str__(self):
        toString = 'Picture {} by {}'.format(self.image, self.author)
        return toString

    def get_labels(self):
        labels_flags = []
        labels_all = Label.objects.all()
        for label in labels_all:
            if label in self.label.all():
                labels_flags.append('1')
            else:
                labels_flags.append('0')
        return labels_flags



class Probability(models.Model):
    THRESHOLD = 0.5
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    label = models.ForeignKey(Label, on_delete=models.CASCADE)
    value = models.FloatField()

    objects = probability_manager()

    def __str__(self):
        toString = '{} labeled {} with certainty {}'.format(self.image, self.label, self.value)
        return toString


