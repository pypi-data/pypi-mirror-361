import time
from ml import cnn

load_data = cnn.load_data
train = cnn.train

root = './imgs/cnn_clz'
mod_filename = './mods/clz_net.pkl'
for i in range(10):
    train_data, class_types = load_data(root, numb=300)
    train_data = train_data * 1
    train(mod_filename, train_data, class_types)
    print('wait 3 sec.')
    time.sleep(3)
