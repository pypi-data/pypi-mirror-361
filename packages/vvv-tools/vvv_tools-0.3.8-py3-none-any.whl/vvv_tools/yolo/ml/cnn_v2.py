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

def read_imginfos(file, class_types_list, numb):
    class_types = set()
    imginfos = []
    if class_types_list:
        class_types = list(class_types_list)
    else:
        for name in os.listdir(file):
            num_ens = list(name.rsplit('.',1)[0].split('_')[0])
            for i in num_ens:
                class_types.add(i)
        class_types = sorted(class_types)
    filelist = os.listdir(file)
    filelist = random.sample(filelist, numb) if len(filelist) > numb else random.sample(filelist, len(filelist))
    stable_len = 0
    for clzidx, imgfile in enumerate(filelist):
        clz_out = list(imgfile.rsplit('.',1)[0].split('_')[0])
        imgfile = os.path.join(file, imgfile)
        fil = imgfile
        img = cv2.imdecode(np.fromfile(fil, dtype=np.uint8), 1)
        img = cv2.resize(img, (64, 64))
        imginfo = {}
        imginfo['class'] = clz_out
        if not stable_len:
            stable_len = len(imginfo['class'])
        if stable_len:
            if stable_len != len(imginfo['class']):
                raise Exception('stable len not match.')
        imginfo['img'] = img
        imginfos.append(imginfo)
        if clzidx % 1000 == 0:
            print(f'process: {clzidx}/{len(filelist)}')
    class_types = {tp: idx for idx, tp in enumerate(class_types)}
    return imginfos, class_types, stable_len

def make_y_true(imginfo, class_types):
    alls = []
    for key in imginfo['class']:
        clz = [0.]*len(class_types)
        clz[class_types.get(key)] = 1.
        alls.extend(clz)
    return torch.FloatTensor(alls)

def load_data(filepath, numb=5000, class_types_list=None):
    imginfos, class_types, stable_len = read_imginfos(filepath, class_types_list, numb)
    train_data = []
    print(len(imginfos))
    for imginfo in imginfos:
        train_data.append([torch.FloatTensor(imginfo['img']), make_y_true(imginfo, class_types)])
    return train_data, class_types, stable_len

class MiniCNN(nn.Module):
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
    def __init__(self, class_types, stable_len, inchennel=3):
        super().__init__()
        self.oceil = len(class_types) * stable_len
        self.model = nn.Sequential(
            OrderedDict([
                ('DynamicResize', self.DynamicResize(self, [64, 64])),
                ('ConvBN_0',  self.ConvBN(inchennel, 32)),
                ('Pool_0',    nn.MaxPool2d(2, 2)),
                ('ConvBN_1',  self.ConvBN(32, 64)),
                ('Pool_1',    nn.MaxPool2d(2, 2)),
                ('ConvBN_2',  self.ConvBN(64, 64)),
                ('Pool_2',    nn.MaxPool2d(2, 2)),
                ('ConvBN_3',  self.ConvBN(64, 128)),
                ('Pool_3',    nn.MaxPool2d(2, 2)),
                ('ConvBN_4',  self.ConvBN(128, 128)),
                ('Flatten',   nn.Flatten()),
                ('Linear1',    nn.Linear(2048, 256)),
                ('Linear2',    nn.Linear(256, self.oceil)),
                # ('ConvBN_0',  self.ConvBN(inchennel, 32)),
                # ('Pool_0',    nn.MaxPool2d(2, 2)),
                # ('ConvBN_1',  self.ConvBN(32, 64)),
                # ('Pool_1',    nn.MaxPool2d(2, 2)),
                # ('ConvBN_2',  self.ConvBN(64, 128)),
                # ('Pool_2',    nn.MaxPool2d(2, 2)),
                # ('ConvBN_3',  self.ConvBN(128, 256)),
                # ('Flatten',   nn.Flatten()),
                # ('Linear1',    nn.Linear(16384, 256)),
                # ('Linear2',    nn.Linear(256, self.oceil)),
            ])
        )
    def forward(self, x):
        x = torch.sigmoid(self.model(x))
        return x

def train(mod_filename, train_data, class_types, stable_len, batch_size=1000):
    EPOCH = 40
    LR = 0.0001
    try:
        state = torch.load(mod_filename, map_location=torch.device(DEVICE))
        net = MiniCNN(class_types, stable_len)
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
        net = MiniCNN(class_types, stable_len)
        net.to(DEVICE)
        optimizer = torch.optim.Adam(net.parameters(), lr=LR)
        epoch = 0
        print('new train.')
    mloss = miniloss(class_types).to(DEVICE)
    optimizer = torch.optim.Adam(net.parameters(), lr=LR)
    train_loader = Data.DataLoader(
        dataset=train_data,
        batch_size=batch_size,
        shuffle=True,
    )
    for epoch in range(epoch, epoch+EPOCH):
        print('epoch', epoch)
        for step, (b_x, b_y) in enumerate(train_loader):
            b_x = Variable(b_x).to(DEVICE)
            b_y = Variable(b_y).to(DEVICE)
            loss = mloss(net(b_x), b_y)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
        state = {
            'net':net.state_dict(), 
            'MiniCNNcode': inspect.getsource(MiniCNN), 
            'epoch':epoch+1, 
            'class_types':class_types,
            'stable_len':stable_len,
        }
        torch.save(state, mod_filename)
        print('save.')
    print('end.')

class miniloss(nn.Module):
    def __init__(self, class_types):
        super().__init__()
        self.clazlen = len(class_types)

    def forward(self, pred, targ, callback=None):
        loss = F.mse_loss(pred,targ,reduction='sum')
        global print
        print = callback if callback else print
        print(loss)
        return loss



















