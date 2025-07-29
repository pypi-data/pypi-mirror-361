import time
from ml import siam

load_data = siam.load_data
train = siam.train

root = './imgs/cnn_siam'
mod_filename = './mods/siam_net.pkl'
for i in range(20):
    retlists, labels = load_data(root, numb=15)
    retlists = retlists * 1
    train(mod_filename, retlists, labels)
    print('wait 3 sec.')
    time.sleep(1)
