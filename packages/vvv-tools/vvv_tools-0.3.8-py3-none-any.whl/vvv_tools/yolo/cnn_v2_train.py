import time
from ml import cnn_v2

load_data = cnn_v2.load_data
train = cnn_v2.train

root = './imgs/cnn_clz_v2'
mod_filename = './mods/clz_v2_net.pkl'
for i in range(10):
    train_data, class_types, stable_len = load_data(root, numb=50000)
    train_data = train_data * 1
    train(mod_filename, train_data, class_types, stable_len)
    print('wait 3 sec.')
    time.sleep(3)