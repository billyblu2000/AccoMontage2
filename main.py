# #######
# imports
# #######
from pretty_midi import PrettyMIDI
from matplotlib import pyplot as plt
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list
from utils.constants import DENSE, SPARSE

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np

# this function will analyze the billboard original data and store the result in 'progression_with_type.pk'
# process_data()

prog_list = read_progressions()


def calculate_density(prog, WINDOW=None):
    if WINDOW is None:
        WINDOW = len(prog.progression[0])
    K = 0
    corre_with_k = {}
    progression = prog.get(only_root=True, flattened=True)
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


index = 10
print(prog_list[index])
print(calculate_density(prog_list[index]))
# count_dict = {}
# for i in prog_list:
#     cyc = len(i)
#     if cyc in count_dict.keys():
#         count_dict[cyc] += 1
#     else:
#         count_dict[cyc] = 1
# x = sorted(list(count_dict.keys()))
# y = [count_dict[i] for i in x]
# plt.bar(x, y)
# plt.show()
