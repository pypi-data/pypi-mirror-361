import time
from ml import yolo
load_voc_data = yolo.load_voc_data
train = yolo.train

xmlpath = './imgs/data'
mod_filename = './mods/yolo_net.pkl'
anchors = [[40, 40]]


def file_filter(filename):
    return True
    fls = ['ce32887f1abb41419469c1cd14e3dbd0_13.jpg']
    print(filename)
    for i in fls:
        if i.split('.')[0] in filename:
            return True

for i in range(10):
    start = (i%3)*1500
    limitnum = 1500
    train_data, _, class_types = load_voc_data(xmlpath, anchors, start, limitnum, file_filter=file_filter)
    train_data = train_data * 1
    train(mod_filename, train_data, anchors, class_types, batch_size=15, LR=0.0001)
    train_data = None
    class_types = None
    print('wait 3 sec.')
    time.sleep(3)