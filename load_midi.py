import os
import numpy as np
from utils.string import RESOURCE_DIR

data_root = RESOURCE_DIR + 'phrase_split_data/'
for song in os.listdir(data_root):
    if song[0] == '.':
        continue
    song_root = os.path.join(data_root, song)
    midi_list = []
    melo_list = []
    for file in os.listdir(song_root):
        if file.split('.')[-1] == 'npz':
            phrase_lable = file.split('.')[0].split('_')[1][0]
            phrase_length = int(file.split('.')[0].split('_')[1][1:])
            melody_phrase = np.load(os.path.join(song_root, file))['melody']
            melo_list.append((file,phrase_lable,melody_phrase))
        if file == 'midi':
            for midi in os.listdir(os.path.join(song_root,file)):
                pass
