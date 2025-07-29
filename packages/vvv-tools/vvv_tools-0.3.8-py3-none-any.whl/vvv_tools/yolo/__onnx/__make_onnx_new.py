import os
import math
import json
import base64
import inspect
import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.onnx
import torch.nn.functional as F
import torch.utils.data as Data
from torch.autograd import Variable
from torchvision.ops import nms
from collections import OrderedDict

USE_CUDA = True if torch.cuda.is_available() else False
DEVICE = 'cuda' if USE_CUDA else 'cpu'
torch.set_printoptions(precision=2, sci_mode=False, linewidth=120, profile='full')
DEVICE = 'cpu'

def load_predict_func(mod_filename):
    def load_state(filename=None):
        state = torch.load(filename, map_location=torch.device(DEVICE))
        class_types = state['class_types']
        vars = {}
        exec(state['MiniCNNcode'], globals(), vars)
        MiniCNN = vars['MiniCNN']
        net = MiniCNN(class_types)
        net.load_state_dict(state['net'])
        net.to(DEVICE)
        net.eval()
        state['net'] = net
        return state
    return load_state(mod_filename)

def load_predict_yolo_func(mod_filename):
    def load_net(filename=None):
        state = torch.load(filename, map_location=torch.device(DEVICE))
        anchors = state['anchors']
        class_types = state['class_types']
        vars = {}
        exec(state['MiniYolo'], globals(), vars)
        MiniYolo = vars['MiniYolo']
        net = MiniYolo(anchors, class_types, is_train=False)
        net.load_state_dict(state['net'])
        net.to(DEVICE)
        net.eval()
        state['net'] = net
        return state
    return load_net(mod_filename)

g_code_clz = None
g_code_yolo = None
g_code_clz_tail = None
g_code_yolo_tail = None

def make_p_clz_code(mod):
    global g_code_clz, g_code_yolo, g_code_clz_tail, g_code_yolo_tail
    g_code_clz = ('''
def load_mod_predict_clz(model_path, class_types):
    ort_session = ort.InferenceSession(model_path)
    i1 = ort_session.get_inputs()[0].name
    c = [i[0] for i in sorted(class_types.items(), key=lambda e:e[1])]
    def _(filepath):
        i = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1) if type(filepath) == str else filepath
        r = ort_session.run(None, {i1: np.expand_dims(i.astype(np.float32), axis=0)})
        v = r[0][0].tolist()
        r = unquote(c[v.index(max(v))])
        return r
    return _
    ''').strip()
    g_code_clz_tail = ('''predict_clz_func = load_mod_predict_clz('predict_clz.onnx', class_types='''+json.dumps(mod['class_types'])+r''')''').strip()
    return g_code_clz, g_code_clz_tail

def make_p_yolo_code(mod):
    global g_code_clz, g_code_yolo, g_code_clz_tail, g_code_yolo_tail
    g_code_yolo = ('''
def load_mod_predict_yolo(model_path, anchors=None, class_types=None):
    ort_session = ort.InferenceSession(model_path)
    i1 = ort_session.get_inputs()[0].name
    i2 = ort_session.get_inputs()[1].name
    def _(filepath, predict_clz=None, pre_deal_img=None, filter_by_rect=None, threshold=0.2, nms_threshold=0.5):
        img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1) if type(filepath) == str else filepath
        i = pre_deal_img(img) if pre_deal_img else img.copy()
        c = np.array([threshold, nms_threshold]).astype(np.float32) # dyn nms_threshold not work! (always 0.5 in my build setting.)
        p = ort_session.run(None, {i1: np.expand_dims(i.astype(np.float32), axis=0), i2: c})[1]
        r = []
        for g in p[0].tolist():
            x1, y1, x2, y2, clz, con = g
            rect = [int(x1), int(y1), int(x2), int(y2)]
            if filter_by_rect and filter_by_rect(rect): continue
            if predict_clz: clz = predict_clz(i[rect[1]:rect[3], rect[0]:rect[2]])
            r.append([rect, clz, con])
        r = sorted(r, key=lambda v:v[0][0])
        return r
    return _
    ''').strip()
    g_code_yolo_tail = ('''predict_yolo_func = load_mod_predict_yolo('predict_yolo.onnx', class_types='''+json.dumps(mod['class_types'])+r''', anchors='''+json.dumps(mod['anchors'])+r''')''').strip()
    return g_code_yolo, g_code_yolo_tail

def save_mod_predict_clz(mod_filename):
    tarp = '.'
    name = 'predict_clz'
    mod = load_predict_func(mod_filename)
    dummy_input = torch.randn(1, 40, 40, 3, requires_grad=True)
    print(f"Model exported to {name}")
    tarf = os.path.join(tarp, name+'.onnx')
    dynamic_axes = {
        'input': {0: 'batch_size', 1: 'width', 2: 'height'},  # 第一维（批量大小）是动态的
        'output': {0: 'batch_size'}   # 如果输出也有批量大小，则也需要设置为动态
    }
    torch.onnx.export(
        mod['net'], 
        dummy_input, 
        tarf, 
        verbose=False, 
        input_names=['input'], 
        output_names=['output'],
        dynamic_axes=dynamic_axes,
    )
    code = '''
from urllib.parse import unquote
import cv2
import numpy as np
import onnxruntime as ort

'''+make_p_clz_code(mod)[0]+'''

'''+make_p_clz_code(mod)[1]+'''

import os
root = '../imgs/cnn_clz'
for p in os.listdir(root):
    fp = os.path.join(root, p)
    for pp in os.listdir(fp):
        fpp = os.path.join(fp, pp)
        if pp.endswith('.png') or pp.endswith('.jpg') or pp.endswith('.gif'):
            r = predict_clz_func(fpp)
            print(fp, r)
            break
    '''
    tarf = os.path.join(tarp, name+'_onnx.py')
    with open(tarf, 'w', encoding='utf8') as f:
        f.write(code.strip())
    print(f"code: {tarf}")

def save_mod_predict_yolo(mod_filename):
    tarp = '.'
    name = 'predict_yolo'
    mod = load_predict_yolo_func(mod_filename)
    dummy_input = torch.randn(1, 416, 416, 3, requires_grad=True)
    dummy_input2 = torch.tensor([0.0, 0.5], requires_grad=True)
    print(f"Model exported to {name}")
    tarf = os.path.join(tarp, name+'.onnx')
    dynamic_axes = {
        'input': {0: 'batch_size', 1: 'width', 2: 'height'},  # 第一维（批量大小）是动态的
        'input2': {0: 'batch_size'},  # 第一维（批量大小）是动态的
        'output': {0: 'batch_size'},   # 如果输出也有批量大小，则也需要设置为动态
        'output2': {0: 'batch_size'}
    }
    torch.onnx.export(
        mod['net'], 
        (dummy_input, dummy_input2), 
        tarf, 
        verbose=False, 
        input_names=['input', 'input2'], 
        output_names=['output', 'output2'],
        dynamic_axes=dynamic_axes,
    )
    code = '''
import math

import cv2
import numpy as np
import onnxruntime as ort
np.set_printoptions(precision=2, linewidth=200, suppress=True)

'''+make_p_yolo_code(mod)[0]+'''

'''+make_p_yolo_code(mod)[1]+'''

import os
root = '../imgs/data'
for p in os.listdir(root):
    fp = os.path.join(root, p)
    if p.endswith('.png') or p.endswith('.jpg') or p.endswith('.gif'):
        r = predict_yolo_func(fp)
        print([[rect,con] for rect,clz,con in r])
    break
    '''
    tarf = os.path.join(tarp, name+'_onnx.py')
    with open(tarf, 'w', encoding='utf8') as f:
        f.write(code.strip())
    print(f"code: {tarf}")

def save_mod_preimage():
    tarp = '.'
    if not (g_code_clz and g_code_yolo):
        raise Exception('not init')
    tail = (r'''
import math
import base64
from urllib.parse import unquote
import cv2
import numpy as np
import onnxruntime as ort
np.set_printoptions(precision=2, linewidth=200, suppress=True)

# import torch # for fix cuda
# providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
providers = ['CPUExecutionProvider']

def read_b64img_to_numpy(b64img):
    import os
    import tempfile
    temp = tempfile.NamedTemporaryFile(delete=False)
    temp.close()
    temp_name = temp.name
    def read_image_meta(f, isgif=False):
        if f.endswith('.gif') or isgif:
            gif = cv2.VideoCapture(f)
            ret, frame = gif.read()
            return frame
        else:
            return cv2.imread(f)
    try:
        img = base64.b64decode(b64img.split('base64,')[-1].encode())
        isgif = img[:3] == b'GIF'
        with open(temp_name, 'wb') as temp_file:
            temp_file.write(img)
        img = read_image_meta(temp_name, isgif=isgif)
        # img = cv2.imdecode(np.fromfile(temp_name, dtype=np.uint8), 1)
    finally:
        os.remove(temp_name)
    return img

def drawrect(img, rect, text):
    cv2.rectangle(img, tuple(rect[:2]), tuple(rect[2:]), (10,250,10), 2, 1)
    x, y = rect[:2]
    def cv2ImgAddText(img, text, left, top, textColor=(0, 255, 0), textSize=20):
        from PIL import Image, ImageDraw, ImageFont
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img)
        fontText = ImageFont.truetype( "font/simsun.ttc", textSize, encoding="utf-8")
        draw.text((left, top), text, textColor, font=fontText)
        return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)
    import re
    if re.findall('[\u4e00-\u9fa5]', text):
        img = cv2ImgAddText(img, text, x, y, (10,10,250), 12) # 如果存在中文则使用这种方式绘制文字
        # img = cv2ImgAddText(img, text, x, y-12, (10,10,250), 12) # 如果存在中文则使用这种方式绘制文字
    else:
        cv2.putText(img, text, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (10,10,250), 1)
    return img

def make_predict_yolo_func():
    def load_mod_predict_clz(model_path, class_types):
        ort_session = ort.InferenceSession(model_path, providers=providers)
        i1 = ort_session.get_inputs()[0].name
        c = [i[0] for i in sorted(class_types.items(), key=lambda e:e[1])]
        def _(filepath):
            i = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1) if type(filepath) == str else filepath
            r = ort_session.run(None, {i1: np.expand_dims(i.astype(np.float32), axis=0)})
            v = r[0][0].tolist()
            r = unquote(c[v.index(max(v))])
            return r
        return _
    def load_mod_predict_yolo(model_path, anchors=None, class_types=None):
        ort_session = ort.InferenceSession(model_path, providers=providers)
        i1 = ort_session.get_inputs()[0].name
        i2 = ort_session.get_inputs()[1].name
        def _(filepath, predict_clz=None, pre_deal_img=None, filter_by_rect=None, threshold=0.2, nms_threshold=0.5):
            img = cv2.imdecode(np.fromfile(filepath, dtype=np.uint8), 1) if type(filepath) == str else filepath
            i = pre_deal_img(img) if pre_deal_img else img.copy()
            c = np.array([threshold, nms_threshold]).astype(np.float32) # dyn nms_threshold not work! (always 0.5 in my build setting.)
            p = ort_session.run(None, {i1: np.expand_dims(i.astype(np.float32), axis=0), i2: c})[1]
            r = []
            for g in p[0].tolist():
                x1, y1, x2, y2, clz, con = g
                rect = [int(x1), int(y1), int(x2), int(y2)]
                if filter_by_rect and filter_by_rect(rect): continue
                if predict_clz: clz = predict_clz(i[rect[1]:rect[3], rect[0]:rect[2]])
                r.append([rect, clz, con])
            r = sorted(r, key=lambda v:v[0][0])
            return r
        return _
    ''' + g_code_clz_tail + r'''
    ''' + g_code_yolo_tail + r'''
    def pre_deal_img(img):
        return img
        # npimg = cv2.addWeighted(npimg, 1.5, npimg, -0.5, 0)
        # _, npimg = cv2.threshold(npimg, 178, 255, cv2.THRESH_BINARY)
        # npimg[np.logical_not(np.all(npimg < 150, axis=2))] = 255
        # return npimg
    def filter_by_rect(rect):
        y = (rect[1] + rect[3])/2.
        x = (rect[0] + rect[2])/2.
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        if w < 40 and h < 40:
            print('filter by size', w, h)
            return True
        return
    def _(b64img, isdrawimg=False):
        ret = {}
        npimg = read_b64img_to_numpy(b64img)
        r = predict_yolo_func(npimg, predict_clz_func, pre_deal_img=pre_deal_img, filter_by_rect=filter_by_rect)
        ret['r'] = [[_rect, clz] for _rect, clz, _ in r]
        if isdrawimg:
            npimg = read_b64img_to_numpy(b64img)
            for i in r:
                _rect, clz, con = i
                npimg = drawrect(npimg, _rect, '{}|{:<.2f}'.format(clz, con))
            ret['b64img'] = base64.b64encode(cv2.imencode('.jpg', npimg)[1]).decode('utf-8')
        return ret
    return _

predict_yolo = make_predict_yolo_func()











import os
tarp = '../imgs/data/'
for idx, i in enumerate(os.listdir(tarp)):
    if i.endswith('.jpg') or i.endswith('.png'):
        print(idx, tarp + i)
        with open(tarp + i, 'rb') as f:
            b64img = base64.b64encode(f.read()).decode()
        # import time
        # start = time.time()
        # for i in range(100):
        #     r = predict_yolo(b64img, isdrawimg=False)
        #     print(i, r['r'])
        # print(time.time() - start)
        # break
        r = predict_yolo(b64img, isdrawimg=True)
        print(i, r['r'])
        if r.get('b64img'):
            npimg = read_b64img_to_numpy(r.get('b64img'))
            cv2.imshow('test', npimg)
            cv2.waitKey(0)
    ''').strip()
    code = tail
    name = 'predict_image_all'
    tarf = os.path.join(tarp, name + '.py')
    with open(tarf, 'w', encoding='utf8') as f:
        f.write(code)

save_mod_predict_clz('../mods/clz_net.pkl')
save_mod_predict_yolo('../mods/yolo_net.pkl')
save_mod_preimage()