#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Datasets
    this file implements the following custom datasets:

    - InstrumentDataset to load images & instrument labels of Cholec80

"""

__author__ = "Alexander Jenke" 

from PIL import Image, ImageFile
import torch.utils.data as data
import csv
import numpy as np
import os
from pathlib import Path

data_path = '/local_home/bodenstse/cholec80_1fps/frames/'
data_pathlib = Path(data_path)



csv_path =  "/home/titizovlj/Desktop/KP/KP_Final_Version/CRC_Komplexpraktikum/Annotations/"


class InstrumentDataset(data.Dataset):
    """InstrumentDataset

    A dataset managing images and instrument labels of Cholec80

    """


    def __init__(self,width,height,transform=None,preload=True,ops=None,opsets=None,modulo = 3, labeled=True):
        """Initializes a dataset

        :param width: width the images should be resized to
        :param height: height the images should be resized to
        :param transform: transformation that gets applied to images when being returned
        :param preload: boolean, defining if images should be loaded on initialisation or on return
        :param ops: list of OPs to be added to the dataset
        :param opsets: list of opset's to be added to the dataset
        :param modulo: load every <modulo>. image. default = 3

        """
        self.width = width
        self.height = height
        self.transform = transform
        self.preload = preload
        self.modulo = modulo
        self.labeled = labeled

        self.data = [] # data type: <class 'list'>, f.e. data: [{'img': None, 'labels': array([0., 0., 0., 0., 0., 0., 0.], dtype=float32), 'path': '/local_home/bodenstse/cholec80_1fps/frames/1/02/00000000.png'}]

        if ops is not None:
            self.load_ops(ops)


        if opsets is not None:
            self.load_opsets(opsets)



    def _load_image(self,path):
        """Loads and resizes an image

        :param path: path of hte image
        :return: PIL Image

        """
        ImageFile.LOAD_TRUNCATED_IMAGES = True
        im = Image.open(path)
        height2 = int(self.width * (im.height / im.width))
        offset_y = (self.height - height2) // 2
        img_y = im.resize((self.width, height2))
        img = Image.new('RGB', (self.width, self.height), (0, 0, 0))
        img.paste(img_y, box=(0, offset_y))
        im.close()
        img_y.close()
        return img

    def _get_index_by_path(self, path):
        """Returns the index of a date defined by the path

        If no date contaning the path can be found a KeyError is raised.

        :param path: path defining the date
        :return: index

        """

        for index, element in enumerate(self.data):
            if element['path'] == path:
                return index
        raise KeyError("Path not found in Dataset")

    def add_sample(self, path, labels):
        """Adds a single date to th dataset

        :param path: path of the image to be added
        :param labels: label of the image to be added

        """

        if self.preload:
            self.data.append({'path': path, 'img': self._load_image(path), 'labels': labels})
        else:
            self.data.append({'path': path, 'img': None, 'labels': labels})

    def load_ops(self,ops):
        """Loads a list of OPs into the dataset

        an OP is a folder containing images and labels of an opperation video

        :param ops: list of OPs

        """
        zero_label = np.zeros(12, dtype=np.float32)

        for op in ops:
            print("loading op", op, "labeled:", self.labeled)
            print(csv_path + op + "/Ins2.csv")
            #with open(csv_path + op + "/Ins.csv", "r") as f:
            try:
                f = open(csv_path + op + "/Ins2.csv", "r")
                
            except FileNotFoundError:
                # no csv exists
                if not self.labeled:
                    # add all images of dataset, remove already labeled ones
                    images_paths = [x for x in Path(data_path + op).glob("*") if (x not in Path(data_path + op).glob("*.csv"))]
                    #print('images_paths',images_paths)

                    for path in images_paths:
                        self.add_sample(str(path), zero_label)

            else:
                # csv exists
                reader = csv.reader(f, delimiter=',')
                labels = []
                labeled_img_paths = []
                for i, row in enumerate(reader):

                    # Generate path to image (out of .csv)
                    path = data_path + op + "/%08d.png" % (int(row[0]) / 25)
                    label = np.array(row[1:], dtype=np.float32)
                    # add labels to labellist
                    labels.append(label)
                    # add pathes to labeled images in list
                    labeled_img_paths.append(path)

                if self.labeled:
                    # add sample for labeled images only
                    for i in range(len(labels)):
                        self.add_sample(labeled_img_paths[i], labels[i])
                        #print('LABELED image path', labeled_img_paths[i])
                        #print('LABELS for labeled img', labels[i])
                else:
                    # add all images of dataset, remove already labeled ones
                    images_paths = [x for x in Path(data_path + op).glob("*") if (x not in Path(data_path + op).glob("*.csv")) and (str(x) not in labeled_img_paths)]

                    for path in images_paths:
                        self.add_sample(str(path), zero_label)



    def load_opsets(self,opsets):
        """Loads a list of opset's into the dataset

        an opset is a folder containing OPs

        :param opsets: list of opset's

        """
        ops = []
        for opset in opsets:
            opset_path = data_path + opset
            ops += [os.path.join(opset, dI) for dI in os.listdir(opset_path) if os.path.isdir(os.path.join(opset_path, dI))]
        self.load_ops(ops)

    def __getitem__(self, index):
        """Returns image, label & path of date defined by index

        :param index: index of the date to be returned
        :return: img, label, path

        """
        sample = self.data[index]
        img = sample['img']

        if not self.preload:
            img = self._load_image(sample['path'])

        if self.transform is not None:
            img = self.transform(img)

        return img, sample['labels'], sample['path']

    def del_sample_by_index(self, index):
        """ Deletes date defined by index in dataset

        :param index: index of the date to be deleted
        :return: path & label of the deleted date

        """
        path = self.data[index]['path']
        label = self.data[index]['labels']
        del self.data[index]
        return path, label

    def del_sample_by_path(self, path):
        """Deletes date defined by path

        :param path: path of the date to be deleted
        :return: path & label of the deleted date

        """
        return self.del_sample_by_index(self._get_index_by_path(path))

    def get_labels(self):
        """Returns an unsorted list of all labels managed by the dataset

        :return: list of labels

        """
        return [self.data[i]['labels'] for i in range(len(self.data))]

    def __len__(self):
        """Returns number of dates the Dataset manages

        :return: number of dates

        """
        return len(self.data)
