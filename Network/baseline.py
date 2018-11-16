#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" pseudo active labeling
    
    This File trains a neural network onto tooldetection to determine the Baseline
    Therefore the Colec80 dataset is split into 3 Parts:
        - labeled images    the net is trained on this data
        - test images       the net is tested on this data
        - unlabeled images  unused images

        
    This task is structured as following:
    
    - define needed functions
    - define parameters
    - setup the environment (copy source-files, create log-files, etc.) 
    - load the datasets
    - load/create the NN
    - calculate pos_weight
    - train epochs:
    | - itterate over labeledset:
    | | - calculate net output 1x -> predictions
    | | - calculate loss
    | | - train net
    | | - calculate f1
    |
    | - itterate over testset:
    | | - calculate net output 1x -> predictions
    | | - calculate net output Nx -> variance
    | | - calculate f1
    | | - save results
"""

__author__ = "Alexaner Jenke"

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader

import torchvision.transforms as transforms

import os
import sys
import datetime
import numpy as np
from shutil import copy2

import datasets
import networks
import losses

################################################################################
# Define functions
################################################################################

def write_to_log(data):
    f_log.write(data)
    print(data)

def print_progress(current,goal):
    progress = int(current / goal * 100)
    sys.stdout.write('\r')
    bar = "["
    for _ in range(progress):
        bar += "="
    for _ in range(100 - progress):
        bar += " "
    bar += "]"
    sys.stdout.write("%s %i%%   " % (bar, progress))
    sys.stdout.flush()

def calculate_f1(prediction,label):
    p = np.concatenate(prediction).round()
    g = np.concatenate(label)
    tp = np.sum([(g[i] + p[i]) == 2 for i in range(len(g))])
    gtp = g.sum().item()
    pp = p.sum().item()
    prec = 1.0 * tp / pp
    rec = 1.0 * tp / gtp
    f1 = 2.0 * (prec * rec) / (prec + rec)
    return f1

def calculate_accuracy(prediction,label):
    p = np.concatenate(prediction).round().flatten()
    g = np.concatenate(label).flatten()
    t = np.sum([(g[i] == p[i]) for i in range(len(g))])
    return t / len(g)

################################################################################
# Define parameters
################################################################################
preload_images = False # load images to RAM once? else load from SSD every Epoche
trial_name = "Baseline_10_lr6"
output_path = "/local_home/wagnerame/Komplexpraktikum/network_output"
data_path  = "/local_home/bodenstse/cholec80_1fps/frames/"

epochs = 100
num_conf_cycles = 0

#batch_size = 128
batch_size = 1
width = 384
height = 216
num_classes = 7

labeled_opsets = []
labeled_ops = [data_path + "1/02/",
               data_path + "1/04/",
               data_path + "1/06/",
               data_path + "1/12/",
               data_path + "1/24/",
               data_path + "1/29/"]

unlabeled_opsets = []
unlabeled_ops =[]

test_opsets = [data_path+ "4/"]
test_ops = []

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
copy2(os.path.realpath(__file__),output_path)

device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
device_cpu = torch.device("cpu")

f_log = open(output_path + "log.txt", "w")

################################################################################
# Load datasets
################################################################################
normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

transform = transforms.Compose(
    [transforms.ToTensor(),
     normalize])

modulo = 1

labeledset = datasets.InstrumentDataset(width, height, transform,preload=preload_images,
                                        ops=labeled_ops,opsets=labeled_opsets, modulo=modulo)
lableled_loader = DataLoader(labeledset, batch_size=batch_size,shuffle=True, num_workers=7)


testset = datasets.InstrumentDataset(width, height, transform,preload=True,  # preload_images, (always preload testset)
                                     ops=test_ops,opsets=test_opsets, modulo=modulo)
test_loader = DataLoader(testset, batch_size=batch_size,shuffle=False, num_workers=7)

################################################################################
# Create/Load NN
################################################################################
net = networks.ProbabilisticAlexNet(num_classes,dropout_p=0.2)
net.to(device)
net.set_dropout(False) #Deactivate Dropouts

sig = nn.Sigmoid()

criterion = losses.WeightedDiceLoss()

optimizer = optim.Adam([
    {'params': net.alexnet.parameters(), 'lr': 1e-6},
    #{'params': net.alexnet.features.parameters(), 'lr': 1e-6},
    #{'params': net.alexnet.classifier.parameters(), 'lr': 1e-5}
    ], weight_decay=1e-4)

################################################################################
# Run training
################################################################################

write_to_log("Labeledset:   %i elements,\n \
             Testset:      %i elements,\n"
             %(len(labeledset), len(testset))
             )


labels = labeledset.get_labels()
pos_count = np.sum(labels, axis=0)
neg_count = (len(labeledset) - pos_count)
pos_weight = torch.Tensor(neg_count / pos_count).cuda()
criterion.set_pos_weight(pos_weight)
write_to_log("pos_weight: " + str(pos_weight) + "\n")

for epoch in range(epochs):
    write_to_log("Epoche " + str(epoch+1))

    labeled_count = 0
    test_count = 0

    prediction = []
    target = []
    paths = []
    loss_sum = 0
    for data in lableled_loader:
        print_progress(labeled_count+test_count,len(lableled_loader)+len(test_loader))

        images, labels_cpu, path = data
        images = images.to(device)
        labels = labels_cpu.to(device)

        optimizer.zero_grad()
        outputs = net(images)

        loss = criterion(outputs,labels)
        loss_sum += loss.item()

        loss.backward()
        optimizer.step()

        prediction.append(sig(outputs).data.cpu().numpy())
        target.append(labels_cpu.numpy())
        paths.append(path)

        labeled_count += 1

    train_f1 = calculate_f1(prediction,target)
    train_acc = calculate_accuracy(prediction,target)
    train_loss = loss_sum/labeled_count

    train_dict = {}
    p = np.concatenate(prediction)
    t = np.concatenate(target)
    for i, path in enumerate(np.concatenate(paths)):
        train_dict[path] = {'label': t[i], 'pred': p[i]}
    train_dict['f1'] = train_f1
    train_dict['acc'] = train_acc
    train_dict['loss'] = train_loss

    prediction = []
    target = []
    paths = []
    loss_sum = 0
    for data in test_loader:
        print_progress(labeled_count + test_count, len(lableled_loader) + len(test_loader))

        images, labels_cpu, path = data
        images = images.to(device)
        labels = labels_cpu.to(device)

        outputs = net(images)

        loss = criterion(outputs, labels)
        loss_sum += loss.item()

        prediction.append(sig(outputs).data.cpu().numpy())
        target.append(labels_cpu.numpy())
        paths.append(path)

        test_count += 1

    test_f1 = calculate_f1(prediction,target)
    test_acc = calculate_accuracy(prediction,target)
    test_loss = loss_sum / test_count

    test_dict = {}
    p = np.concatenate(prediction)
    t = np.concatenate(target)
    for i, path in enumerate(np.concatenate(paths)):
        test_dict[path] = {'label': t[i], 'pred': p[i]}
    test_dict['f1'] = test_f1
    test_dict['acc'] = test_acc
    test_dict['loss'] = test_loss

    torch.save({'test_dict': test_dict, 'train_dict': train_dict},
               output_path + "data_" + str(epoch + 1) + ".tar")

    print("\n")
    write_to_log("Train (loss: %.3f, acc %.3f, f1 %.3f) Test (loss: %.3f, acc %.3f, f1 %.3f)\n"
                 % (train_loss, train_acc, train_f1,
                    test_loss, test_acc, test_f1))
