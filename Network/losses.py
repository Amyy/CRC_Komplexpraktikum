# !/usr/bin/env python
# -*- coding: utf-8 -*-

""" Losses
    this file implements the following custom loss functions:

    - dice loss with pos_weight
"""

__author__ = "Alexaner Jenke"

from torch import Tensor
from torch.nn.modules.loss import _Loss
from torch.nn import Sigmoid


class WeightedDiceLoss(_Loss):
    """ Calculates the dice loss taking the pos_weight into account

    """

    def __init__(self, pos_weight=Tensor([1, 1, 1, 1, 1, 1, 1]).cuda()):
        """Sets up dice loss with pos_weight

        :param pos_weight: Tensor defining the negative to positive ratio of labels per tool
        """
        super(WeightedDiceLoss, self).__init__()
        self.pos_weight = pos_weight
        self.sig = Sigmoid()

    def forward(self, input, target):
        """calculates loss

        this function is called indirectly

        :param input: prediction to be analyzed
        :param target: ground truth
        :return: loss
        """
        if not (target.size() == input.size()):
            raise ValueError("Target size ({}) must be the same as input size ({})".format(target.size(), input.size()))

        input = self.sig(input)
        eps = 0.000000001  # eps to prevent zero division

        intersection = (input * target).sum(dim=0)
        target_sum = (target * target).sum(dim=0)
        input_sum = (input * input).sum(dim=0)

        # dice loss per tool
        loss = 1. - (2. * intersection + eps) / (target_sum + input_sum + eps)

        # weight the dice losses according to the proportion of positive to negative samples per tool  (pos_weight)
        # return the sum of the weighted losses as loss
        return (loss * self.pos_weight).sum() / self.pos_weight.sum()

    def set_pos_weight(self,pos_weight):
        """sets pos_weight to be used in loss calculation

        :param pos_weight: Tensor([7x float: neg/pos]).cuda()
        :return: None
        """
        self.pos_weight = pos_weight
