import os
import numpy as np
from utils.string import RESOURCE_DIR

data_root = RESOURCE_DIR + 'phrase_split_data/'
for song in os.listdir(data_root):
    if song[0] == '.':
        continue
    song_root = os.path.join(data_root, song)
    for file in os.listdir(song_root):
        if file.split('.')[-1] == 'npz':
            phrase_lable = file.split('.')[0].split('_')[1][0] #capital letter denotes vocal phrases
            phrase_length = int(file.split('.')[0].split('_')[1][1:])  #phrase length is measured in bars
            phrase_data = np.load(os.path.join(song_root, file))
            """The following four matrix paired with each other"""
            melody_phrase = phrase_data['melody']   #vocal melody. Zero matrix if this is not a vocal phrase. Quantized in 16th note
            bridge_phrase = phrase_data['bridge']   #accompanying melody. Could be a zero matrix, too. Quantized in 16th note
            piano_phrase = phrase_data['piano'] #piano accompaniment, Should NOT be zero at MOST times. Quantized in 16th note
            chord_phrase = phrase_data['chord'] #chord transcription. Could be zero at some times. Quantized in quater notes
        if file == 'midi':
            for midi in os.listdir(os.path.join(song_root,file)):
                pass
