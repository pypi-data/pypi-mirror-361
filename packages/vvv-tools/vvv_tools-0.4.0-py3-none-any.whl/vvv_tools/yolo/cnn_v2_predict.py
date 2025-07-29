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
        class_types = state['class_types']
        stable_len = state['stable_len']
        vars = {}
        exec(state['MiniCNNcode'], globals(), vars)
        MiniCNN = vars['MiniCNN']
        net = MiniCNN(class_types, stable_len)
        net.load_state_dict(state['net'])
        net.to(DEVICE)
        net.eval()
        state['net'] = net
        return state
    def make_get_class_func(state):
        net = state['net'].to(DEVICE)
        def get_class(filepath):
            class_types = state['class_types']
            class_types = [i[0] for i in sorted(class_types.items(), key=lambda e:e[1])]
            if type(filepath) == str:
                img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1)
            else:
                img = filepath
            x = torch.FloatTensor(img).unsqueeze(0).to(DEVICE)
            v = net(x)
            if USE_CUDA:
                v = v.cpu().detach().numpy()
            else:
                v = v.detach().numpy()
            v = v[0].tolist()
            def split_list(lst, n):
                return [lst[i:i + n] for i in range(0, len(lst), n)]
            v = split_list(v, len(class_types))
            r = ''
            for i in v:
                r += class_types[i.index(max(i))]
            return r
        return get_class
    return make_get_class_func(load_state('./mods/clz_v2_net.pkl'))


root = './imgs/cnn_clz_v2'

get_clazz = make_predict_func()

p = 0
q = 0
for filepath in os.listdir(root):
    clazz = filepath.rsplit('.',1)[0].split('_')[0]
    filepath = os.path.join(root, filepath)
    t = get_clazz(filepath)
    if t == clazz:
        p += 1
    else:
        print('    ', t, filepath)
        # img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1)
        # cv2.imshow('test', img)
        # cv2.waitKey(0)
        q += 1
    # print(t)
    # break
    if (p + q) % 1000 == 0:
        print('aaa', p, 'bbb', q, 'ccc', p/(p+q))