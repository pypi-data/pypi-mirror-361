# coding=utf-8

import io
import base64
import random
import os
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import OrderedDict

USE_CUDA = True if torch.cuda.is_available() else False
DEVICE = 'cuda' if USE_CUDA else 'cpu'
torch.set_printoptions(precision=2, sci_mode=False, linewidth=120, profile='full')

def read_img_by_base64(b64img, readtype=1):
    img = base64.b64decode(b64img.encode())
    image = cv2.imdecode(np.frombuffer(img, np.uint8), readtype)
    return image

def make_predict_func():
    def load_state(filename=None):
        state = torch.load(filename, map_location=torch.device('cpu'))
        vars = {}
        exec(state['MiniSiamcode'], globals(), vars)
        MiniSiam = vars['MiniSiam']
        net = MiniSiam()
        net.load_state_dict(state['net'])
        net.to(DEVICE)
        net.eval()
        state['net'] = net
        return state
    def make_get_siam_func(state):
        net = state['net'].to(DEVICE)
        def get_siam(filepath1, filepath2):
            img1 = cv2.imdecode(np.fromfile(filepath1, dtype=np.uint8), 1) if type(filepath1) == str else filepath1
            img2 = cv2.imdecode(np.fromfile(filepath2, dtype=np.uint8), 1) if type(filepath2) == str else filepath2
            x1 = torch.FloatTensor(img1).unsqueeze(0).to(DEVICE)
            x2 = torch.FloatTensor(img2).unsqueeze(0).to(DEVICE)
            r = net(x1, x2)
            if USE_CUDA:
                v = r.cpu().detach().cpu().numpy()
            else:
                v = r.detach().cpu().numpy()
            return v
        return get_siam
    return make_get_siam_func(load_state('./mods/siam_net.pkl'))


root = './imgs/cnn_siam'

get_siam = make_predict_func()
predict_siam_func = lambda i1,i2:get_siam(i1,i2)[0].tolist()

def get_random_n(filepath):
    flist = os.listdir(filepath)
    limit = 15
    flist = random.sample(flist, limit) if len(flist) > limit else random.sample(flist, len(flist))
    flist = [os.path.join(filepath, i) for i in flist]
    return flist
def get_rd_one(lst):
    return random.choice(lst)
def imread(filepath):
    with open(filepath, 'rb') as f: bcode = f.read()
    return cv2.imdecode(np.frombuffer(bcode, np.uint8), 1)
def get_rd_avoid(idx, left, right):
    while True:
        ridx = random.randint(left, right)
        if idx != ridx:
            return ridx
def mklog_img(f1, f2, d):
    f1 = cv2.resize(f1, (64,64))
    f2 = cv2.resize(f2, (64,64))
    img = np.hstack((f1, f2))
    cv2.putText(img, '{:.2f}'.format(d), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,0), 3)
    cv2.putText(img, '{:.2f}'.format(d), (10,10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,255,255), 1)
    return img

import os
show_dif = True
list_n = os.listdir(root)#[:3]
for idx, level1_1 in enumerate(list_n):
    level1_2 = list_n[get_rd_avoid(idx, 0, len(list_n)-1)]
    flist1 = get_random_n(os.path.join(root, level1_1))
    flist2 = get_random_n(os.path.join(root, level1_2))
    logs1 = []
    logs2 = []
    yes = []
    for fp1 in flist1:
        fp2 = get_rd_one(flist1)
        f1 = imread(fp1)
        f2 = imread(fp2)
        x = predict_siam_func(f1, f2)
        d = round(x, 2)
        yes.append(d)
        if show_dif: logs1.append(mklog_img(f1, f2, d))
    nots = []
    for fp1 in flist1:
        fp2 = get_rd_one(flist2)
        f1 = imread(fp1)
        f2 = imread(fp2)
        x = predict_siam_func(f1, f2)
        d = round(x, 2)
        nots.append(d)
        if show_dif: logs2.append(mklog_img(f1, f2, d))
    syes = round(sum(yes)/len(yes), 2)
    snots = round(sum(nots)/len(nots), 2)
    print(syes, snots, level1_1, level1_2)
    if show_dif:
        im1 = np.vstack(logs1)
        im2 = np.vstack(logs2)
        a, b, c = im1.shape
        imgp = np.zeros([a, 20, c]).astype(im1.dtype)
        showimg = np.hstack([im1, imgp, im2])
        cv2.imshow('test', showimg)
        cv2.waitKey()
    # break