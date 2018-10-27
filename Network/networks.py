#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Networks
    this file implements the following custom neural networks:

    - probabilistic AlexNet using 1D dropouts
"""

__author__ = "Alexander Jenke"

import torch
import torch.nn as nn
import torchvision

class ProbabilisticAlexNet(nn.Module):
    """ ProbabilisticAlexNet

        A neural network basically according to the structure of AlexNet with additional dropout layers following
        every ReLu layer to achieve a probabilistic output.
    """
    def __init__(self, num_features=4096,dropout_p=0.5):
        """ Initializes an probabilistic AlexNet with pretrained features and untrained classifier

        using the pretrained net of torchvision

        :param num_features: number of features the network will output
        :param dropout_p: the dropout probability per dropout layer
        """
        super(ProbabilisticAlexNet, self).__init__()
        self.alexnet = torchvision.models.alexnet(pretrained=True)
        self.dropout = nn.Dropout(p=dropout_p)
        self.do_dropout = True
        self.alexnet.classifier = nn.Sequential(
            nn.Linear(14080, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, num_features),
        )

    def forward(self, x):
        """ Calculates the output of the network

            according to the do_dropout boolean the dropout layers get added after the ReLu layers

        :param x: input tensor
        :return: output tensor
        """
        if self.do_dropout: #use dropouts
            # Features
            x = self.alexnet.features[0](x)  # Conv
            x = self.alexnet.features[1](x)  # ReLu
            x = self.dropout(x)
            x = self.alexnet.features[2](x)  # MaxPool
            x = self.alexnet.features[3](x)  # Conv
            x = self.alexnet.features[4](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.features[5](x)  # MaxPool
            x = self.alexnet.features[6](x)  # Conv
            x = self.alexnet.features[7](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.features[8](x)  # Conv
            x = self.alexnet.features[9](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.features[10](x)  # Conv
            x = self.alexnet.features[11](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.features[12](x)  # MaxPool

            x = x.view(x.size(0), -1)
            # Classifier
            x = self.alexnet.classifier[0](x)  # Linear
            x = self.alexnet.classifier[1](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.classifier[2](x)  # Linear
            x = self.alexnet.classifier[3](x)  # ReLU
            x = self.dropout(x)
            x = self.alexnet.classifier[4](x)  # Linear

        else: #don't use dropouts
            x = self.alexnet.features(x)
            x = x.view(x.size(0), -1)
            x = self.alexnet.classifier(x)

        return x

    def load(self, model_file):
        """ Loads a network model

        used to load an earlier trained network

        :param model_file: network file to be loaded
        """
        self.load_state_dict(torch.load(model_file))

    def save(self, model_file):
        """ Saves a trained network

        used to save a trained network for later usage

        :param model_file: network file to be saved to
        """
        torch.save(self.state_dict(), model_file)

    def set_dropout(self,bool):
        """ Sets the do_dropout boolean defining the dropout usage

        :param bool: boolean defining the dropout usage
        """
        self.do_dropout = bool
