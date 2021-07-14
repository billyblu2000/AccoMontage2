import os
import numpy as np
from pretty_midi import PrettyMIDI

from utils.dictionary import root_to_str
from utils.string import RESOURCE_DIR

if __name__ == '__main__':

    data_root = RESOURCE_DIR + 'phrase_split_data/'

    # get song key
    pop909_root = RESOURCE_DIR + 'POP909/'
    song_key = {i: 0 for i in range(910)}
    for song in os.listdir(pop909_root):
        if song[0] == '.' or song == 'index.xlsx':
            continue
        key_file = open(os.path.join(pop909_root, song) + '/key_audio.txt', 'r')
        song_key[int(song)] = key_file.readline().split('\t')[2].strip('\n')

    # load midi and melody
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
                melo_list.append([song + file[:-4], phrase_lable, melody_phrase])
            if file == 'midi':
                midi_root = os.path.join(song_root, file)
                for midi in os.listdir(midi_root):
                    midi_file = PrettyMIDI(os.path.join(midi_root, midi))
                    tonic = song_key[int(song)].split(':')[0]
                    mode = song_key[int(song)].split(':')[1]
                    midi_list.append([song + midi[:-4], midi_file, tonic, mode])
        for i in melo_list:
            for j in midi_list:
                if j[0] == i[0]:
                    i.append(j[3])
        print(midi_list)
        print(melo_list)
        # raise Exception
