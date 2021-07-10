# #######
# imports
# #######
from pretty_midi import PrettyMIDI, Instrument, Note
from settings import *
from chords.ChordProgression import read_progressions, query_progression, print_progression_list, ChordProgression
from utils.ProcessData import process_data
from utils.constants import PIANO, SHORT, DENSE, LONG, SPARSE
from mpl_toolkits import mplot3d

from utils.process_pop909 import process
from utils.string import STATIC_DIR
from utils.utils import listen, get_melo_notes_from_midi, get_bar_and_position, combine_ins, nmat2ins, \
    pick_progressions, MIDILoader
from matplotlib import pyplot as plt
import numpy as np

# this function will analyze the billboard original data and store the result in 'progression.txt'
# process_data()

POP909 = 'progressions_from_pop909.txt'
DEFAULT = 'progressions.txt'

# get melody
melos = MIDILoader()
melos.config(output_form='number')
melo = melos.get(name='6.mid')

# pickout all progressions with metre = 4/4 and bars = 8
prog_list = read_progressions(progression_file=DEFAULT)
new = []
for i in prog_list:
    if len(i.progression) == 8 and len(i.progression[0]) == 8:
        new.append(i)

# model parameters
score = {
    0: 1, 1: 0.5, 2: 0.8, 3: 0.5, 4: 0.9, 5: 0.5, 6: 0.7,
    0.5: 0.2, 1.5: 0.2, 2.5: 0.2, 3.5: 0.2, 4.5: 0.2, 5.5: 0.2, 6.5: 0.2, 7: 0.2  # strange chords, give smaller weight
}

# compute score for each progression
progression_score = []
for progression in new:
    i = 0
    tot_score = 0
    for chord in progression:
        temp_score = 0
        if melo[i] < chord:
            temp_score += score[melo[i] + 7 - chord]
        else:
            print(melo[i], chord)
            temp_score += score[melo[i] - chord]
        if melo[i + 1] < chord:
            temp_score += score[melo[i + 1] + 7 - chord]
        else:
            temp_score += score[melo[i + 1] - chord]
        temp_score /= 2
        tot_score += temp_score
        i += 2
        if i > len(melo) - 2:
            tot_score /= (i) // 2
            progression_score.append((tot_score, progression))
            break

# pick out the progression with max score
pure_score = [i[0] for i in progression_score]
max_index = pure_score.index(max(pure_score))
max_progression = progression_score[max_index][1]
print(max_progression)
print(melo)
