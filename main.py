from pretty_midi import PrettyMIDI, Instrument, Note
from settings import *
from chords.ChordProgression import read_progressions, query_progression, print_progression_list, ChordProgression
from utils.ProcessData import process_data
from utils.constants import PIANO
from mpl_toolkits import mplot3d

from utils.process_pop909 import process
from utils.string import STATIC_DIR
from utils.utils import listen, get_melo_notes_from_midi, get_bar_and_position, combine_ins, nmat2ins
from matplotlib import pyplot as plt
import numpy as np

# process_data()
POP909 = 'progressions_from_pop909.txt'
DEFAULT = 'progressions.txt'
prog_list = read_progressions(progression_file=DEFAULT)

# ONE_FOUR = []
# ONE_FIVE = []
# ONE_SIX = []
# ONE_FOUR_FIVE = []
# ONE_FOUR_FIVE_TWO = []
# ONE_FOUR_FIVE_THREE = []
# ONE_FOUR_FIVE_SIX = []
# TWO_FIVE_ONE = []
# OTHER = []
#
#
# def count_chord(progression):
#     chord_dict = {1: 0, 1.5: 0, 2: 0, 2.5: 0, 3: 0, 3.5: 0, 4: 0, 4.5: 0, 5: 0, 5.5: 0, 6: 0, 6.5: 0, 7: 0}
#     for i in progression:
#         if i in chord_dict.keys():
#             chord_dict[i] += 1
#         else:
#             chord_dict[i] = 1
#     total = sum([i for i in chord_dict.values()])
#     for key in chord_dict.keys():
#         chord_dict[key] = chord_dict[key] / total
#     return chord_dict
#
#
#
# major_prog_list = []
# for i in prog_list:
#     if i.meta['mode'] == 'M':
#         major_prog_list.append(i)
#
# for progression in major_prog_list:
#     chord_dict = count_chord(progression)
#     if len(chord_dict) == 1:
#         OTHER.append(progression)
#     elif chord_dict[1] + chord_dict[4] > 0.8:
#         ONE_FOUR.append(progression)
#     elif chord_dict[1] + chord_dict[5] > 0.8:
#         ONE_FIVE.append(progression)
#     elif chord_dict[1] + chord_dict[6] > 0.6:
#         ONE_SIX.append(progression)
#     elif chord_dict[1] + chord_dict[4] + chord_dict[5] >= 0.6 and \
#             chord_dict[1] > 0 and chord_dict[4] > 0 and chord_dict[5] > 0:
#         ONE_FOUR_FIVE.append(progression)
#     elif chord_dict[1] + chord_dict[4] + chord_dict[5] >= 0.3 and \
#             chord_dict[1] > 0 and chord_dict[4] > 0 and chord_dict[5] > 0:
#         if chord_dict[2] > chord_dict[3] and chord_dict[2] > chord_dict[6]:
#             ONE_FOUR_FIVE_TWO.append(progression)
#         elif chord_dict[3] > chord_dict[2] and chord_dict[3] > chord_dict[6]:
#             ONE_FOUR_FIVE_THREE.append(progression)
#         elif chord_dict[6] > chord_dict[2] and chord_dict[6] > chord_dict[3]:
#             ONE_FOUR_FIVE_SIX.append(progression)
#     elif chord_dict[2] + chord_dict[5] + chord_dict[1] >= 0.5 and chord_dict[2] > 0.15 and chord_dict[5] > 0.15 and chord_dict[1] > 0.15:
#         TWO_FIVE_ONE.append(progression)
#     else:
#         OTHER.append(progression)
#
#
# print(len(ONE_FOUR))
# print(len(ONE_FIVE))
# print(len(ONE_SIX))
# print(len(ONE_FOUR_FIVE))
# print(len(ONE_FOUR_FIVE_TWO))
# print(len(ONE_FOUR_FIVE_THREE))
# print(len(ONE_FOUR_FIVE_SIX))
# print(len(TWO_FIVE_ONE))
# print(len(OTHER))
#
SPARSE_LONG = []
DENSE_LONG = []
UNKNOWN_LONG = []
SPARSE_SHORT = []
DENSE_SHORT = []

density_list = []
len_list = []


def calculate_density(prog, WINDOW=None):
    if WINDOW is None:
        WINDOW = len(prog.progression[0])
    K = 0
    corre_with_k = {}
    progression = [i for i in prog]
    if WINDOW >= len(progression):
        if WINDOW > 10:
            return 0, 0
        else:
            return -1, len(progression)
    try:
        while True:

            x, y = [], []
            K += WINDOW
            if K > len(progression) // 2:
                break
            for i in range(len(progression) // WINDOW):
                x.append(progression[i * WINDOW:(i + 1) * WINDOW])
                y.append(progression[i * WINDOW + K:(i + 1) * WINDOW + K])
                if (i + 1) * WINDOW + K == len(progression):
                    break
            x = np.array(x).transpose()
            y = np.array(y).transpose()
            i = 0
            while True:
                x_row = x[i]
                y_row = y[i]
                if len(np.unique(x_row)) == 1 or len(np.unique(y_row)) == 1:
                    x = np.delete(x, i, axis=0)
                    y = np.delete(y, i, axis=0)
                else:
                    i += 1
                if i >= len(x):
                    break
            corre_mat = np.corrcoef(x, y)
            # print(corre_mat)
            avg_corre = 0
            for i in range(len(x)):
                avg_corre += corre_mat[i, i + len(x)]
            corre_with_k[K] = avg_corre / len(x)
        max_corre = -1
        max_k = 0
        for item in corre_with_k.items():
            if item[1] > max_corre:
                max_corre = item[1]
                max_k = item[0]
            elif item[1] == max_corre:
                if item[0] < max_k:
                    max_k = item[0]
        # print("Max autocorrelation {c} with K = {k}".format(c=max(value), k=max_k))
        return max_corre, max_k
    except Exception as e:
        return calculate_density(prog, WINDOW=WINDOW * 2)


dl, dl_c, dl_nc, dl_uk = [], [], [], []

for i in prog_list:
    dl.append(calculate_density(i))
for i in dl:
    if i[0] > 0:
        dl_c.append(i)
    elif i[0] == 0:
        dl_uk.append(i)
    else:
        dl_nc.append(i)
print("progression that somehow cycles:", len(dl_c))
print("progression unknown:", len(dl_uk))
print("progression that not cycles:", len(dl_nc))
print("avg length of cycles:", sum([i[1] for i in dl_c]) / len(dl_c))

for i in prog_list:
    d = calculate_density(i)
    if len(i) > 100:
        if d[1] >= 32:
            SPARSE_LONG.append((i, d))
        elif d[1] == 0:
            UNKNOWN_LONG.append((i, d))
        else:
            DENSE_LONG.append((i, d))
    else:
        if d[1] >= 32:
            SPARSE_SHORT.append((i, d))
        else:
            DENSE_SHORT.append((i, d))

print(len(SPARSE_LONG))
print(len(UNKNOWN_LONG))
print(len(DENSE_LONG))

print(len(SPARSE_SHORT))
print(len(DENSE_SHORT))
#

for i in DENSE_LONG:
    print(i[1])
    print(i[0])
