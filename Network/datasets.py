#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Datasets
    this file implements the following custom datasets:

    - InstrumentDataset to load images & instrument labels of Cholec80

"""

__author__ = "Alexander Jenke" 

from PIL import Image
import torch.utils.data as data
import csv
import numpy as np
import os
from pathlib import Path


class InstrumentDataset(data.Dataset):
    """InstrumentDataset

    A dataset managing images and instrument labels of Cholec80

    """

    # TODO: add .csv path, separated from data path
    data_path = Path('/local_home/bodenstse/cholec80_1fps/frames')

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

        self. data = [] # data type: <class 'list'>, f.e. data: [{'img': None, 'labels': array([0., 0., 0., 0., 0., 0., 0.], dtype=float32), 'path': '/local_home/bodenstse/cholec80_1fps/frames/1/02/00000000.png'}]

        if ops is not None:
            self.load_ops(ops)

        if opsets is not None:
            self.load_opsets(opsets)

    def _load_image(self,path):
        """Loads and resizes an image

        :param path: path of hte image
        :return: PIL Image

        """
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
        image_path = path

        if self.labeled:
            parts = Path(path).parts
            image_path = self.data_path / parts[-3] / parts[-2] / parts[-1]

        print('image path', str(image_path))

        if self.preload:
            self.data.append({'path': str(path), 'img': self._load_image(str(image_path)), 'labels': labels})
        else:
            self.data.append({'path': str(path), 'img': None, 'labels': labels})


    def load_ops(self,ops):
        """Loads a list of OPs into the dataset

        an OP is a folder containing images and labels of an operation video

        :param ops: list of OPs

        """

# ORIGINAL CODE SNIPPET:
        # for op in ops:
        #     f = open(op + "/Ins.csv", "r")
        #     print(op)
        #     reader = csv.reader(f, delimiter=',')
        #     for i, row in enumerate(reader):
        #         if i % self.modulo == 0:
        #             path = op + "/%08d.png" % i
        #             label = np.array(row[1:], dtype=np.float32)
        #             self.add_sample(path, label)

# MODIFIED CODE SNIPPET;
        if self.labeled:

            for op in ops:
                f = open(op + "/Ins.csv", "r") # f.e. op == /local_home/bodenstse/cholec80_1fps/frames/4/57 ->
                # f == /local_home/bodenstse/cholec80_1fps/frames/4/57/Ins.csv || /mnt/g27prist/TCO/TCO-Studenten/wagnerame/CRC_Komplexpraktikum/Annotations/4/57/Ins.csv

                reader = csv.reader(f, delimiter=',') # reader: reads csv file
                for i, row in enumerate(reader):
                    if i % self.modulo == 0:
                        # print('row:', row) # row type: <class 'list'>, f.e. row: ['0', '0', '0', '0', '0', '0', '0', '0']

                        # path = op + "/%08d.png" % i # f.e. path: /local_home/bodenstse/cholec80_1fps/frames/1/02/00000000.png (for i == 0)
                        split = op.split('/')
                        opset_nr = split[len(split) -2] # get opset number out of path: /mnt/g27prist/TCO/TCO-Studenten/wagnerame/CRC_Komplexpraktikum/Annotations/4/57
                        op_nr = split[len(split) - 1]
                        path = self.data_path / opset_nr / op_nr / ("%08d.png" % (int(row[0]) / 25))

                        label = np.array(row[1:], dtype=np.float32) # label type: <class 'numpy.ndarray'> , f.e. label: [0. 0. 0. 0. 0. 0. 0.]

                        self.add_sample(path,label)

        else:


            for op in ops:

                # load all images out of folder EXCEPT .csv file
                images_paths = [x for x in Path(op).glob("*") if x not in Path(op).glob("*.csv")]

                # TODO: open .csv from separate .csv path -> load only images from data_path
                # TODO: insert delete function again, but load .csv from specfic .csv path

                """
                f = open(op + "/Ins.csv", "r")

                reader = csv.reader(f, delimiter=',') # reader: reads csv file
                labeled_image_path = []
                for i, row in enumerate(reader):
                    if i % self.modulo == 0:
                        split = op.split('/')
                        opset_nr = split[len(split) -2] # get opset number out of path: /mnt/g27prist/TCO/TCO-Studenten/wagnerame/CRC_Komplexpraktikum/Annotations/4/57
                        op_nr = split[len(split) - 1]
                        labeled_image_path.append(self.data_path / opset_nr / op_nr / ("%08d.png" % (int(row[0]) / 25)))

                images_paths = [x for x in images_paths if x not in labeled_image_path]
                """

                for image_path in images_paths:

                        label = np.zeros(7, dtype=np.float32)
                        self.add_sample(image_path, label)

                        print(image_path)


    def load_opsets(self,opsets):
        """Loads a list of opset's into the dataset

        an opset is a folder containing OPs

        :param opsets: list of opset's

        """
        ops = []
        for opset in opsets:
            ops += [os.path.join(opset, dI) for dI in os.listdir(opset) if os.path.isdir(os.path.join(opset, dI))]
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
