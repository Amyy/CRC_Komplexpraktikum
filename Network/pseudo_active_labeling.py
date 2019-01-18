#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" pseudo active labeling
    
    This File simulates the active labeling while training a neural network 
    onto tooldetection.
    Therefore the Colec80 dataset is split into 3 Parts:
        - labeled images    the net is trained on this data
        - unlabeled images  the net can choose images to be labeled
        - test images       the net is tested on this data
        
    This task is structured as following:

    - define parameters
    - define needed functions
    - setup the environment (copy source-files, create log-files, etc.) 
    - load the datasets
    - load/create the NN
    - run 6 rounds:
    | - calculate round specific parameters (pos_weight)
    | - train epochs:
    | | - iterate over labeledset:
    | | | - calculate net output 1x -> predictions
    | | | - calculate loss
    | | | - train net    
    | | | - calculate f1
    | |
    | | - iterate over testset:
    | | | - calculate net output 1x -> predictions
    | | | - calculate net output Nx -> variance
    | | | - calculate f1
    | | | - save results
    |
    | - iterate over unlabeledset:
    | | - calculate net output Nx -> variance
    |
    | - select images to be labeled
"""

__author__ = "Alexander Jenke"

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

import torchvision.transforms as transforms

import os
import sys
import getopt
import datetime
import numpy as np
from shutil import copy2

import datasets
import networks
import losses
from datasets import data_path

################################################################################
# Define parameters
################################################################################
preload_images = False  # load images to RAM once? else load from SSD every epoch
trial_name = "Ins_AlexNet"
output_path = "/mnt/g27prist/TCO/TCO-Studenten/wagnerame/testing_alexnet/"

#TODO: separate data_path and specific .csv path (maybe here: only give "4/57" to datasets.py

# rounds = 10
rounds = 1

# epochs = 100
epochs = 2

new_labels_per_round = None  # gets calculated when unlabledset is loaded
num_var_samples = 10  # how many outputs are calculated to determine the variance

batch_size = 128
width = 384
height = 216
num_classes = 7

labeled_opsets = []
labeled_ops = ["4/57"]

unlabeled_opsets = []

unlabeled_ops = ["1/34"]

test_opsets = []
test_ops = ["4/07"]

################################################################################
# Parse Comandline args
################################################################################
opts = []
try:
    opts, args = getopt.getopt(sys.argv[1:], "hdt:i:o:")
except getopt.GetoptError:
    print("pseudo_active_labeling.py [OPTIONS] \n\n"
          "OPTIONS: \n"
          "-d activates debug output \n"
          "-t trial name (effects folder naming)\n"
          "-i path to Cholec80 data\n"
          "-o path where trial folder gets saved to\n"
          "-h print this help\n")
for opt, arg in opts:
    if opt == '-h':
        print("pseudo_active_labeling.py [OPTIONS] \n\n"
              "OPTIONS: \n"
              "-d activates debug output \n"
              "-t trial name (effects folder naming)\n"
              "-i path to Cholec80 data\n"
              "-o path where trial folder gets saved to\n"
              "-h print this help\n")
        sys.exit()
    elif opt == '-i':
        data_path = arg
    elif opt == '-o':
        output_path = arg
    elif opt == '-t':
        trial_name = arg

do_debug = '-d' in [e for e, _ in opts]

################################################################################
# Define functions
################################################################################


def write_to_log(log_data):
    """write data to log & console

    :param log_data: data to be written
    """
    f_log.write(log_data)
    print(log_data)


def debug(debug_data):
    """Prints debug data when debug mode is enabled

    :param debug_data:  data to be written
    """
    if do_debug:
        print(debug_data)


def print_progress(current, goal):
    """prints a progess bar to the console when debug mode is enabled

    :param current: current progress
    :param goal: max value 'current' can reach
    :return: None; prints to console
    """
    if do_debug:
        bar_progress = int(current / goal * 100)
        sys.stdout.write('\r')
        bar = "["
        for _ in range(bar_progress):
            bar += "="
        for _ in range(100 - bar_progress):
            bar += " "
        bar += "]"
        sys.stdout.write("%s %i%%   " % (bar, bar_progress))
        sys.stdout.flush()


def calculate_f1(prediction, label):
    """ Calculates the f1 score of the prediction

    prediction & target are lists of lists of lists of floats:
    [
      [
        [7x float one per tool] #one per image in batch
      ] #one per batch in dataset
    ]

    :param prediction: prediction to be analyzed
    :param label: ground truth the prediction is compared to
    :return: f1 score of the prediction
    """
    input = prediction.round()
    tp = np.sum([(label[e] + input[e]) == 2 for e in range(len(label))])
    gtp = label.sum().item()
    pp = input.sum().item()
    prec = 1.0 * tp / pp
    rec = 1.0 * tp / gtp
    f1 = 2.0 * (prec * rec) / (prec + rec)
    return f1


def calculate_accuracy(prediction, label):
    """Calculates the accuracy of the prediction

    prediction & target are lists of lists of lists of floats:
    [
      [
        [7x float one per tool] #one per image in batch
      ] #one per batch in dataset
    ]

    :param prediction: prediction to be analyzed
    :param label: ground truth the prediction is compared to
    :return: accuracy of the prediction
    """
    p = prediction.round().flatten()
    g = label.flatten()
    t = np.sum([(g[e] == p[e]) for e in range(len(g))])
    return t / len(g)


################################################################################
# Prepare environment
################################################################################
output_path += trial_name + "_"
output_path += datetime.datetime.now().strftime("%Y%m%d-%H%M") + "/"

# replace existing folder
if os.path.isdir(output_path):
    import shutil
    shutil.rmtree(output_path)

os.makedirs(output_path)
copy2(os.path.realpath(__file__), output_path)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device_cpu = torch.device("cpu")

f_log = open(output_path + "log.txt", "w")

################################################################################
# Load datasets
################################################################################

# activate the sharing strategy 'file_system' when a dataset exceeds 120000 dates
torch.multiprocessing.set_sharing_strategy('file_system')


normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

transform = transforms.Compose(
    [transforms.ToTensor(),
     normalize])

modulo = 1

labeledset = datasets.InstrumentDataset(width, height, transform, preload=preload_images,
                                        ops=labeled_ops, opsets=labeled_opsets, modulo=modulo, labeled=True)
lableled_loader = DataLoader(labeledset, batch_size=batch_size, shuffle=True, num_workers=7)

unlabeledset = datasets.InstrumentDataset(width, height, transform, preload=preload_images,
                                          ops=unlabeled_ops, opsets=unlabeled_opsets, modulo=modulo, labeled=False)
unlableled_loader = DataLoader(unlabeledset, batch_size=batch_size, shuffle=False, num_workers=7)

testset = datasets.InstrumentDataset(width, height, transform, preload=True,  # preload_images, (always preload testset)
                                     ops=test_ops, opsets=test_opsets, modulo=modulo)
test_loader = DataLoader(testset, batch_size=batch_size, shuffle=False, num_workers=7)

new_labels_per_round = int(len(unlabeledset)/9) # 'split' unlabeledset into 9 parts to be labeled -> 10 rounds = 100%
write_to_log("new_labels_per_round:" + str(new_labels_per_round) + "\n")

################################################################################
# Create/Load NN
################################################################################
# ---Init in Round--- net = networks.ProbabilisticAlexNet(num_classes, dropout_p=0.2)
# ---Init in Round--- net.to(device)

sig = nn.Sigmoid()

criterion = losses.WeightedDiceLoss()

# ---Init in Round--- optimizer = optim.Adam([{'params': net.alexnet.parameters(), 'lr': 1e-6}], weight_decay=1e-4)

################################################################################
# Run training
################################################################################

for round_nr in range(rounds):
    net = networks.ProbabilisticAlexNet(num_classes, dropout_p=0.2)
    net.to(device)
    optimizer = optim.Adam([{'params': net.alexnet.parameters(), 'lr': 1e-6}], weight_decay=1e-4)

    write_to_log("Round %i \n\n \
                 Labeledset:   %i elements,\n \
                 Unlabeledset: %i elements,\n \
                 Testset:      %i elements,\n"
                 % (round_nr + 1, len(labeledset),
                    len(unlabeledset),
                    len(testset)))

    round_output_path = output_path + "/labeling_round_" + str(round_nr) + "/"
    os.makedirs(round_output_path)

    labels = labeledset.get_labels()
    pos_count = np.sum(labels, axis=0)
    neg_count = (len(labeledset) - pos_count)
    print("pos:", pos_count, "neg:", neg_count)
    pos_weight = torch.Tensor(neg_count / pos_count).cuda()
    criterion.set_pos_weight(pos_weight)
    write_to_log("pos_weight: " + str(pos_weight.data.cpu().numpy()) + "\n")

    for epoch in range(epochs):
        write_to_log("Epoch " + str(epoch+1) + ": ")
        progress = 0

        """ iterate over labeledset
            train the net by claculating predictions 
        """
        prediction = []
        target = []
        loss_sum = 0
        for data in lableled_loader:
            print_progress(progress, len(lableled_loader)+len(test_loader))

            # prepare data
            images, labels_cpu, _ = data
            images = images.to(device)
            labels = labels_cpu.to(device)

            # calculate net output -> prediction
            optimizer.zero_grad()
            outputs = net(images)

            # calculate loss
            loss = criterion(outputs, labels)
            loss_sum += loss.item()

            # train net
            loss.backward()
            optimizer.step()

            # provide stats
            prediction.append(sig(outputs).data.cpu().numpy())
            target.append(labels_cpu.numpy())
            progress += 1

        # calculate stats
        prediction = np.concatenate(prediction)
        target = np.concatenate(target)

        train_f1 = calculate_f1(prediction, target)
        train_acc = calculate_accuracy(prediction, target)
        train_loss = loss_sum/len(lableled_loader)

        """ iterate over testset (once per epoche)
            evaluate the net by calculating predictions & f1 on the testset
        """
        prediction = []
        target = []
        paths = []
        for data in test_loader:
            print_progress(progress, len(lableled_loader) + len(test_loader))

            # prepare data
            images, labels_cpu, path = data
            images = images.to(device)
            labels = labels_cpu.to(device)

            # calculate net output without dropouts-> prediction
            net.set_dropout(False)
            outputs = net(images)
            net.set_dropout(True)

            # provide stats
            prediction.append(sig(outputs).data.cpu().numpy())
            target.append(labels_cpu.numpy())
            paths.append(path)
            progress += 1

        # calculate stats
        prediction = np.concatenate(prediction)
        target = np.concatenate(target)
        paths = np.concatenate(paths)

        test_f1 = calculate_f1(prediction, target)
        test_acc = calculate_accuracy(prediction, target)

        # save epoch data
        epoch_dict = {}
        rawdata_dict = {}
        for i, path in enumerate(paths):
            rawdata_dict[path] = {'label': target[i],
                                  'pred': prediction[i]}
        epoch_dict['raw'] = rawdata_dict
        epoch_dict['f1'] = test_f1
        epoch_dict['acc'] = test_acc
        torch.save(epoch_dict, round_output_path + "testdata_" + str(epoch + 1) + ".tar")

        debug("\n")  # new line after progress bar
        write_to_log("Train (loss %.3f, acc %.3f, f1 %.3f) Test (acc %.3f, f1 %.3f)\n"
                     % (train_loss, train_acc, train_f1,
                        test_acc, test_f1))

    """ iterate over testset (once per round)
        evaluate the net by calculating variance on the testset
    """
    debug("Calculating testdata variance:")

    raw_variance = []
    target = []
    paths = []
    for i, data in enumerate(test_loader):
        print_progress(i, len(test_loader))

        # prepare data
        images, labels_cpu, path = data
        images = images.to(device)
        labels = labels_cpu.to(device)

        # calculate net output with dropouts-> variance
        batch_variance = np.zeros((labels.size(0), num_var_samples, num_classes))
        for var_nr in range(num_var_samples):
            outputs_np = sig(net(images)).data.cpu().numpy()
            for sample_nr in range(len(outputs_np)):
                batch_variance[sample_nr][var_nr] = outputs_np[sample_nr]

        # provide stats
        raw_variance.append(batch_variance)
        target.append(labels_cpu.numpy())
        paths.append(path)

    # calculate stats
    raw_variance = np.concatenate(raw_variance)
    target = np.concatenate(target)
    paths = np.concatenate(paths)

    test_var_f1 = calculate_f1(np.mean(raw_variance, axis=1), target)
    test_var = np.mean(np.var(raw_variance, axis=1), axis=0)

    # save variance data
    round_dict = {}
    rawdata_dict = {}
    for i, path in enumerate(paths):
        rawdata_dict[path] = {'label': target[i],
                              'var': raw_variance[i]}
    round_dict['raw'] = rawdata_dict
    round_dict['f1'] = test_var_f1
    round_dict['var'] = test_var
    torch.save(round_dict, round_output_path + "testdata_variance.tar")

    debug("\n")  # new line after progress bar
    write_to_log("         Test (var_f1 %.3f, var [%.5f %.5f %.5f %.5f %.5f %.5f %.5f])\n"
                 % (test_var_f1, test_var[0], test_var[1], test_var[2],
                    test_var[3], test_var[4], test_var[5], test_var[6]))

    """ iterate over unlabeledset (once per round)
                  calculate variance on unlabeled data
    """
    debug("Calculating unlabeled variance:")

    raw_variance = []
    paths = []
    for progress, data in enumerate(unlableled_loader):
        print_progress(progress, len(unlableled_loader))

        # prepare data
        images, labels_cpu, path = data
        images = images.to(device)
        labels = labels_cpu.to(device)

        # calculate net output with dropouts-> variance
        batch_variance = np.zeros((labels.size(0), num_var_samples, num_classes))
        for i in range(num_var_samples):
            outputs_np = sig(net(images)).data.cpu().numpy()
            for sample_nr in range(len(outputs_np)):
                batch_variance[sample_nr][i] = outputs_np[sample_nr]

        raw_variance.append(batch_variance)
        paths.append(path)

    raw_variance = np.concatenate(raw_variance)
    paths = np.concatenate(paths)

    # select images to be labeled
    selected_dict = {}
    unlabeledset_list = sorted([(variance, paths[i]) for i, variance in enumerate(np.var(raw_variance, axis=1))],
                               key=lambda x: np.max(x[0]), reverse=True)

    print(np.max(unlabeledset_list[0][0]), np.max(unlabeledset_list[-1][0]))

    for _ in range(min(new_labels_per_round, len(unlabeledset_list))):
        path, label = unlabeledset.del_sample_by_path(unlabeledset_list.pop(0)[1])
        labeledset.add_sample(path, label)
        selected_dict[path] = label
        #debug("Added %s to labeledset. %s" % (path, str(label)))

    # save variance of unlabeled data
    unlabeled_dict = {}
    rawdata_dict = {}
    for i, path in enumerate(paths):
        rawdata_dict[path] = raw_variance[i]
    unlabeled_dict['raw'] = rawdata_dict
    unlabeled_dict['mean_var'] = np.mean(np.var(raw_variance, axis=1))
    unlabeled_dict['selected'] = selected_dict
    torch.save(unlabeled_dict, round_output_path + "unlabeled_variance.tar")
