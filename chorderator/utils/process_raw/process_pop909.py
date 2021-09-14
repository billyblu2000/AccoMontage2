import os

import numpy as np

from chords.ChordProgression import ChordProgression, print_progression_list

np.set_printoptions(edgeitems=1000)

POP909_DIR = "/Users/billyyi/Desktop/POP909 Phrase Split Data/Phrase Split Data/"
POP909_ORI_DIR = "/Users/billyyi/Desktop/POP909-Dataset-master/POP909/"

tonic_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
             'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}

chord_map = {0: 1, 2: 2, 4: 3, 5: 4, 7: 5, 9: 6, 11: 7}

c_major = [36, 38, 40, 41, 43, 45, 47, 48, 50, 52, 53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76, 77, 79, 81,
           83, 84, 86, 88, 89, 91, 93, 95, 96, 0]


def process(data_root):
    data = []
    for song in os.listdir(data_root):
        try:
            int(song)
        except:
            continue
        song_root = os.path.join(data_root, song)
        for file in os.listdir(song_root):
            if file.split('.')[-1] == 'npz':
                phrase_lable = file.split('.')[0].split('_')[1][0]  # capital letter denotes vocal phrases
                phrase_length = int(file.split('.')[0].split('_')[1][1:])  # phrase length is measured in bars
                phrase_data = np.load(os.path.join(song_root, file))
                """The following four matrix paired with each other"""
                melody_phrase = phrase_data['melody']  # vocal melody. Zero matrix if this is not a vocal phrase.
                # Quantized in 16th note
                bridge_phrase = phrase_data['bridge']  # accompanying melody. Could be a zero matrix, too. Quantized in
                # 16th note
                piano_phrase = phrase_data[
                    'piano']  # piano accompaniment, Should NOT be zero at MOST times. Quantized in
                # 16th note
                chord_phrase = phrase_data['chord']  # chord transcription. Could be zero at some times. Quantized in
                # quater notes

                # get tonic
                tonic_path = POP909_ORI_DIR + song + "/key_audio.txt"
                tonic_file = open(tonic_path, 'r')
                if len(tonic_file.readlines()) != 1:
                    continue
                else:
                    tonic_file.seek(0)
                    tonic = tonic_file.readline().split()[2].strip('\n')
                tonic = tonic.split(':')
                if tonic[1] == 'min':
                    continue
                else:
                    tonic = tonic[0]

                melody_pitch_sequence = melody_phrase_to_pitch_sequence(melody_phrase)
                melody_pitch_sequence_c_major = melody_to_c_major(melody_pitch_sequence, original_tonic=tonic)
                chord_sequence_c_major = chord_phrase_to_chord_sequence(chord_phrase, original_tonic=tonic)
                if melody_pitch_sequence_c_major is not None and chord_sequence_c_major is not None:
                    if sum(melody_pitch_sequence_c_major) != 0 and \
                            len(melody_pitch_sequence_c_major) == 4 * len(chord_sequence_c_major):
                        data.append([melody_pitch_sequence_c_major, chord_sequence_c_major])
    return np.array(data, dtype=object)


def melody_phrase_to_pitch_sequence(melody_phrase):
    melo_pitch_sequence = []
    memory, count_length = 0, 0
    for unit in melody_phrase:
        if sum(unit) == 0:
            if count_length == 0:
                melo_pitch_sequence.append(0)
            else:
                melo_pitch_sequence.append(memory)
                count_length -= 1
        else:
            pitch = np.argwhere(unit != 0)[0][0]
            melo_pitch_sequence.append(pitch)
            count_length = unit[pitch] - 1
            memory = pitch
    return np.array(melo_pitch_sequence)


def chord_phrase_to_chord_sequence(chord_phrase, original_tonic):
    chord_sequence = np.zeros(shape=chord_phrase.shape[0])
    distance = tonic_map[original_tonic]
    for i in range(len(chord_phrase)):
        root_note = chord_phrase[i][0] - distance
        if root_note < 0:
            root_note += 12
        try:
            chord_sequence[i] = chord_map[root_note]
        except:
            return None
    return chord_sequence


def melody_to_c_major(melody_pitch_sequence, original_tonic):
    melody_pitch_sequence_c_major = np.zeros(shape=melody_pitch_sequence.shape)
    distance = tonic_map[original_tonic]
    if distance > 7:
        distance -= 12
    for i in range(len(melody_pitch_sequence)):
        if melody_pitch_sequence[i] != 0:
            melody_pitch_sequence_c_major[i] = melody_pitch_sequence[i] - distance
        else:
            melody_pitch_sequence_c_major[i] = 0
    for i in melody_pitch_sequence_c_major:
        if i not in c_major:
            return None
    return melody_pitch_sequence_c_major


if __name__ == '__main__':
    data = process(POP909_DIR)
    prog_list = []
    for i in range(len(data)):
        chord = data[i][1].astype('int32').tolist()
        progression = []
        bar = []
        if len(chord) % 4 == 0:
            for j in chord:
                bar.append(j)
                bar.append(j)
                if len(bar) == 8:
                    progression.append(bar)
                    bar = []
        elif len(chord) % 3 == 0:
            for j in chord:
                bar.append(j)
                bar.append(j)
                if len(bar) == 6:
                    progression.append(bar)
                    bar = []
        else:
            continue
        p = ChordProgression()
        p.progression = progression
        prog_list.append(p)
    print_progression_list(prog_list)

