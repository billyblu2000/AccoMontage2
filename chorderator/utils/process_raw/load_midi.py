import os
import pickle

import numpy as np
from pretty_midi import PrettyMIDI

from utils.structured import root_to_str, str_to_root, major_map, minor_map
from utils.string import RESOURCE_DIR

if __name__ == '__main__':

    data_root = RESOURCE_DIR + 'phrase_split_data/'
    data = {
        'midi': [],
        'melo': [],
        'roll': []
    }

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

        # load
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

        # change melody format
        for i in melo_list:
            melody = i[2]
            new_melody = []
            length, last = 0, 0
            for unit in melody:
                if sum(unit) == 0:
                    if length != 0:
                        new_melody.append(last)
                        length -= 1
                    else:
                        new_melody.append(0)
                else:
                    for j in range(len(unit)):
                        if unit[j] != 0:
                            new_melody.append(j)
                            last = j
                            length = unit[j] - 1
                            break
            i[2] = new_melody

        # change melody/midi list format
        new_melo_list, new_midi_list = [], []
        for i in melo_list:
            for j in midi_list:
                if j[0] == i[0]:
                    new_melo_list.append((i[0], j[2], '4/4', j[3], i[1], i[2]))
        for i in midi_list:
            for j in melo_list:
                if j[0] == i[0]:
                    new_midi_list.append((i[0], i[2], '4/4', i[3], j[1], i[1]))
        melo_list, midi_list = new_melo_list, new_midi_list

        new = []
        for midi in melo_list:
            tonic_index = str_to_root[midi[1]]
            note_list = []
            map = major_map if midi[3] == 'maj' else minor_map
            for pitch in midi[5]:
                if pitch == 0:
                    note_list.append(0)
                else:
                    note_list.append(map[(pitch - tonic_index) % 12])
            new.append((midi[0], midi[1], midi[2], midi[3], midi[4], note_list))
        roll_list = new

        # data['midi'] += midi_list
        data['melo'] += melo_list
        data['roll'] += roll_list

    file = open('melodies.pk', 'bw')
    pickle.dump(data, file, 1)
