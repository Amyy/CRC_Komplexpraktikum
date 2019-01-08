from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
import numpy
import csv
import math

FRAME_FREQ = 25
NETWORK_USER = 'network'


class image_manager(models.Manager):
    def next_image(self, user, image=None):
        nxt_img = None
        network_user = User.objects.get(username=NETWORK_USER)

        #print('last image:',image)

        if image:
            #find first labeled image after argument image
            image_ul = Userlabels.objects.filter(author=user, image=image).first()
            if image_ul:
                labeled_images = Userlabels.objects.filter(author=user, timestamp__gt=image_ul.timestamp)\
                    .order_by('timestamp')
                if labeled_images:
                    nxt_img = labeled_images.first().image
        #print(nxt_img)

        if not nxt_img:
            #find unlabeled image with highest variance and lowst userlabels count
            unlabeled_images = Image.objects.exclude(userlabels__author=user)
            nxt_img = unlabeled_images.annotate(num_ul=models.Count('userlabels'))\
                .order_by('-variance', 'num_ul').first()
            nxt_img2 = unlabeled_images.annotate(num_ul=models.Count('userlabels'))\
                .order_by('-variance', 'num_ul')[1]
            print('next image', nxt_img, nxt_img.variance, nxt_img.num_ul)
            print('next image2', nxt_img2, nxt_img2.variance, nxt_img2.num_ul)
        return nxt_img


    def previous_image(self, user, image):
        prev_image = image
        labeled_images = Userlabels.objects.filter(author=user).order_by('-timestamp')
        image_ul = Userlabels.objects.filter(author=user, image=image).first()
        if image_ul:
            labeled_images = labeled_images.filter(timestamp__lt=image_ul.timestamp)
        if labeled_images:
            prev_image = labeled_images.first().image
        return prev_image

    def get_image(self, opset=0, op=0, number=0, path=False):
        #Eigenschaften aus Pfad extrahieren
        if path:
            split = path.split('/')
            opset = split[len(split)-3]
            op = split[len(split)-2]
            number = int(split[len(split)-1].split('.')[0])

        images = self.filter(opset=opset, op=op, number=number)
        if not images:
            image = Image(name=str(number), opset=opset, op=op, number=number)
            image.save()
            images = self.filter(opset=opset, op=op, number=number)
        return images.first()

    def get_labeled_images(self, user, amount = 20):
        labeled_images = Userlabels.objects.filter(author=user).order_by('-timestamp')
        return labeled_images[0:amount]

"""
class probability_manager(models.Manager):

    def get_image_labels(self, image):
        im_prob = self.filter(image=image)

        thr_labels = []
        for prob in im_prob:
            if prob.value:
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
                probabilities = []
                path = row[0]
                for i in range(1,8):
                    probabilities.append(int(row[i]))
                variance = float(row[8])
                image = Image.objects.get_image(path=path)
                self.set_probabilities(image=image, probabilities=probabilities)
                image.variance = variance
                image.save()

"""
class userlabels_mangager(models.Manager):

    def set_userlabels(self, image, user, label_set = []):
        userlabels, created = Userlabels.objects.get_or_create(image=image, author=user)
        userlabels.label.set(label_set)
        userlabels.save()

    def set_userlabels_str(self, image, user, label_set = []):
        label_set_query = Label.objects.filter(name__in=label_set)
        self.set_userlabels(image, user, label_set_query)

    def set_uncertain(self, image, user, value):
        userlabels, created = Userlabels.objects.get_or_create(image=image, author=user)
        userlabels.uncertain = value
        userlabels.save()

    def generate_csv(self, csvfile, opset, op):
        spamwriter = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        network_user = User.objects.get(username=NETWORK_USER)
        #filter images by opset and op
        images = Image.objects.filter(opset=opset, op=op).order_by('number')
        #ul_op = self.filter(image__opset = opset, image__op = op)
        #ul_group_label_dict = dict((d['image__name'], dict(d, index=index)) for (index, d) in enumerate(ul_group_label))
        labels = Label.objects.all()

        #iterate through images
        for image in images:
            name = image.name
            ul_image = self.filter(image__name=name).exclude(author=network_user)
            ul_labels = ul_image.values('label__name').annotate(models.Count('label__name'))
            print('ul_labels', ul_labels)
            #TODO test Count label

            write_labels = []
            print(ul_image)
            #if userlabes exist
            #calculate majority vote
            if ul_image:
                min_votes = math.ceil(len(ul_image) / 2)
                label_votes = dict()
                print(name, min_votes)

                # generate dict of labels and count of votes
                ul_image_dict = dict([])
                for ulabel in ul_labels:
                    ul_image_dict[ulabel['label__name']] = ulabel['label__name__count']
                #print(ul_image_dict)

                # calculate majority vote and parse to string list
                for label in labels:
                    label_name = label.__str__()
                    label_string = '0'
                    if ul_image_dict.__contains__(label_name):
                        if ul_image_dict[label_name] >= min_votes:
                            label_string = '1'
                    write_labels.append(label_string)

            #if no userlabels exist
            #calculate NN prediction
            else:
                nn_labels = Label.objects.filter(userlabels__author=network_user, userlabels__image=image)
                for label in labels:
                    label_string = '0'
                    if label in nn_labels:
                        label_string = '1'
                    write_labels.append(label_string)

            #print([name] + write_labels)
            #write to csv file
            spamwriter.writerow([int(name) * FRAME_FREQ] + write_labels)

    def read_annotations(self, path):
        with open(path, 'r') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            images = []
            image_labels = []
            image_var = []
            label_classes = Label.objects.all()
            for row in csvreader:
                labels = []
                path = row[0]
                #convert labels
                for i in range(0,7):
                    if int(row[i+1]):
                        labels.append(label_classes[i])
                #convert variance
                variance = float(row[8])
                opset, op, number = convert_path(path)
                image, create = Image.objects.get_or_create(opset=opset, op=op, name=number)
                images.append(image)
                image_labels.append(labels)
                image_var.append(variance)
            self.update_annotations(images=images, image_labels=image_labels)
            self.update_variances(images=images, variances=image_var)

    def update_annotations(self, images, image_labels):
        network_user = User.objects.get(username=NETWORK_USER)
        new_labels = []
        for i, image in enumerate(images):
            userlabel, create = Userlabels.objects.get_or_create(image=image, author=network_user)
            userlabel.label.set(image_labels[i])
            userlabel.save()
        print(len(images), ' images annotated.')

        """
        network_user = User.objects.get(username=NETWORK_USER)
        #delete outdated network labels
        self.filter(image__in=images, author=network_user).delete()
        #create new network labels
        new_network_labels = []
        for image_label_list in image_labels:
            new_network_labels.append(Userlabels(image=images[i], author=network_user))
        self.bulk_create(new_network_labels)
        #add labels
        with transaction.atomic():
            for image in images:
                UserProfile.objects.filter(pk=image.pk).update()
        """

    def update_variances(self, images, variances):
        #bulk update
        print('updated variances of ', len(images), ' images')
        with transaction.atomic():
            for i, image in enumerate(images):
                Image.objects.filter(pk=image.pk).update(variance=variances[i])

    def get_image_labels(self, image):
        network_user = User.objects.get(username=NETWORK_USER)
        nn_labels = Label.objects.filter(userlabels__author=network_user, userlabels__image=image)
        return nn_labels


class Image(models.Model):
    name = models.CharField(max_length=200)
    variance = models.FloatField(null=True)
    data = models.ImageField(null=True, default='default.jpg')
    opset = models.IntegerField(null=True)
    op = models.IntegerField(null=True)
    number = models.IntegerField(null=True)

    objects = image_manager()

    def __str__(self):
        return self.name

    def description(self):
        descr = ''
        descr += str(self.name)
        return descr

class Label(models.Model):
    name = models.CharField(max_length=50)
    order = models.IntegerField()

    def __str__(self):
        return self.name

class Userlabels(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    label = models.ManyToManyField(Label)
    timestamp = models.DateTimeField(auto_now_add=True)
    uncertain = models.BooleanField(default=False)
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

def convert_path(path):
    split = path.split('/')
    opset = split[len(split) - 3]
    op = split[len(split) - 2]
    number = int(split[len(split) - 1].split('.')[0])
    return opset, op, number
