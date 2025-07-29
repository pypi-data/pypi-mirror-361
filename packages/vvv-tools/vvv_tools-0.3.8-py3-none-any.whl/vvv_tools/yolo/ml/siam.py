# coding=utf-8
# pip install opencv-contrib-python torch torchvision torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple/

import os
import base64
import random
import inspect
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.utils.data as Data
from torch.autograd import Variable
from collections import OrderedDict

USE_CUDA = True if torch.cuda.is_available() else False
DEVICE = 'cuda' if USE_CUDA else 'cpu'
torch.set_printoptions(precision=2, sci_mode=False, linewidth=120, profile='full')

def read_imginfos(file, numb):
    retlists = []
    labels = []
    imginfos = []
    for clzidx, clazz in enumerate(os.listdir(file)):
        clazzfilepath = os.path.join(file, clazz)
        clazzfilepathlist = os.listdir(clazzfilepath)
        clazzfilepathlist = random.sample(clazzfilepathlist, numb) if len(clazzfilepathlist) > numb else random.sample(clazzfilepathlist, len(clazzfilepathlist))
        print(clzidx, clazz, len(clazzfilepathlist))
        templist = []
        for imgfile in clazzfilepathlist:
            imgfile = os.path.join(clazzfilepath, imgfile)
            fil = imgfile
            img = cv2.imdecode(np.fromfile(fil, dtype=np.uint8), 1)
            img = cv2.resize(img, (64, 64))
            templist.append(torch.FloatTensor(img))
            # cv2.imshow('test', img)
            # cv2.waitKey(0)
        imginfos.append(templist)
    count = 0
    def logcount():
        nonlocal count
        count += 1
        if count % 100 == 0: print(count)
    if len(imginfos) <= 1:
        raise Exception('error len')
    def get_rd_false(imginfos):
        while True:
            x = random.randint(0, len(imginfos)-1)
            if x != idx:
                break
        infos2 = imginfos[x]
        return random.choice(infos2)
    for idx, infos in enumerate(imginfos):
        for i1 in infos:
            logcount()
            retlists.append([i1, random.choice(infos)])
            labels.append(torch.tensor(1., dtype=torch.float32))
        for i1 in infos:
            logcount()
            retlists.append([i1, get_rd_false(imginfos)])
            labels.append(torch.tensor(0., dtype=torch.float32))
    return retlists, labels

def load_data(filepath, numb=5000):
    return read_imginfos(filepath, numb)

class SiameseDataset(Data.Dataset):
    def __init__(self, image_pairs, labels):
        self.image_pairs = image_pairs
        self.labels = labels
    def __len__(self):
        return len(self.image_pairs)
    def __getitem__(self, idx):
        img1_path, img2_path = self.image_pairs[idx]
        label = self.labels[idx]
        img1 = img1_path
        img2 = img2_path
        return img1, img2, label

class MiniSiam(nn.Module):
    class DynamicResize(nn.Module):
        def __init__(self, _self, target_size=(128, 128), mode='bilinear', align_corners=True):
            super(_self.DynamicResize, self).__init__()
            self.target_size = target_size
            self.mode = mode
            self.align_corners = align_corners if mode in ['bilinear', 'bicubic', 'trilinear'] else None
        def forward(self, x):
            x = x.permute(0, 3, 2, 1).contiguous()
            x = F.interpolate(x, size=self.target_size, mode=self.mode, align_corners=self.align_corners)
            return x
    class ConvBN(nn.Module):
        def __init__(self, cin, cout, kernel_size=3, stride=1, padding=None):
            super().__init__()
            padding   = (kernel_size - 1) // 2 if not padding else padding
            self.conv = nn.Conv2d(cin, cout, kernel_size, stride, padding, bias=False)
            self.bn   = nn.BatchNorm2d(cout, momentum=0.01)
            self.relu = nn.LeakyReLU(0.1, inplace=True)
        def forward(self, x): 
            return self.relu(self.bn(self.conv(x)))
    def __init__(self, inchennel=3):
        super().__init__()
        self.dyn1 = self.DynamicResize(self, [64, 64])
        self.dyn2 = self.DynamicResize(self, [64, 64])
        self.cnn = nn.Sequential(
            OrderedDict([
                ('ConvBN_0',  self.ConvBN(inchennel, 32)),
                ('Pool_0',    nn.MaxPool2d(2, 2)),
                ('ConvBN_1',  self.ConvBN(32, 64)),
                ('Pool_1',    nn.MaxPool2d(2, 2)),
                ('ConvBN_2',  self.ConvBN(64, 64)),
                ('Pool_2',    nn.MaxPool2d(2, 2)),
                ('ConvBN_3',  self.ConvBN(64, 64)),
                ('Pool_3',    nn.MaxPool2d(2, 2)),
                ('ConvBN_4',  self.ConvBN(64, 64)),
                ('Flatten',   nn.Flatten()),
                ('Linear1',    nn.Linear(1024, 128)),
                ('Linear2',    nn.Linear(128, 128)),
            ])
        )
        self.full_connect = nn.Sequential(
            OrderedDict([
                ('LinearEnd',   nn.Linear(128, 1)),
            ])
        )
    def forward(self, x1, x2):
        out1 = self.cnn(self.dyn1(x1))
        out2 = self.cnn(self.dyn2(x2))
        x = torch.abs(out1 - out2)
        x = self.full_connect(x)
        x = F.sigmoid(x).view(-1)
        return x

def train(mod_filename, retlists, labels, batch_size=1000):
    EPOCH = 2
    LR = 0.0001
    try:
        state = torch.load(mod_filename, map_location=torch.device(DEVICE))
        net = MiniSiam()
        net.load_state_dict(state['net'])
        net.to(DEVICE)
        optimizer = torch.optim.Adam(net.parameters(), lr=LR)
        epoch = state['epoch']
        print('load train.')
    except:
        import traceback
        excp = traceback.format_exc()
        if 'FileNotFoundError' not in excp:
            print(traceback.format_exc())
        net = MiniSiam()
        net.to(DEVICE)
        optimizer = torch.optim.Adam(net.parameters(), lr=LR)
        epoch = 0
        print('new train.')
    criterion = ContrastiveLoss().to(DEVICE)
    dataset = SiameseDataset(retlists, labels)
    train_loader = Data.DataLoader(dataset, batch_size=batch_size, shuffle=False)
    for epoch in range(epoch, epoch+EPOCH):
        print('epoch', epoch)
        for img1, img2, label in train_loader:
            img1, img2, label = img1.to(DEVICE), img2.to(DEVICE), label.to(DEVICE)
            optimizer.zero_grad()
            x = net(img1, img2)
            loss = criterion(x, label)
            loss.backward()
            optimizer.step()
        state = {
            'net':net.state_dict(), 
            'MiniSiamcode': inspect.getsource(MiniSiam), 
            'epoch':epoch+1, 
        }
        torch.save(state, mod_filename)
        print('save.')
    print('end.')

class ContrastiveLoss(nn.Module):
    def __init__(self, margin=1.0):
        super().__init__()
        self.margin = margin
    def forward(self, x, label, callback=None):
        loss = F.mse_loss(x, label, reduction='sum')
        global print
        print = callback if callback else print
        print(loss)
        return loss
