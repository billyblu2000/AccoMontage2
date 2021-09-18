# #######
# imports
# #######
import pickle

import pandas
from pretty_midi import PrettyMIDI, Instrument, Note
from matplotlib import pyplot as plt

from chords.Chord import Chord
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list, ChordProgression
from utils.constants import DENSE, SPARSE
from utils.string import STATIC_DIR

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np, calculate_density, read_lib

# my_progressions = read_progressions()
# my_dict = {}
# count_key = 0
# count = 0
# for i in my_progressions:
#     count += 1
#     print(count)
#     for key in my_dict.keys():
#         if my_dict[key][0] == i:
#             my_dict[key].append(i)
#             break
#     else:
#         count_key += 1
#         print(count_key)
#         my_dict[count_key] = [i]
# progressions_representative = [lst[0] for lst in my_dict.values()]
# for item in my_dict.items():
#     new = []
#     for p in item[1]:
#         p.progression_class['duplicate-id'] = item[0]
#         new.append(p)
#     my_dict[item[0]] = new
#
#
# file = open('progressions_dict.pcls', 'wb')
# pickle.dump(my_dict, file)
# file.close()
#
# file = open('progressions_representative.pcls', 'wb')
# pickle.dump(progressions_representative, file)
# file.close()

p = read_progressions('progressions_dict.pcls')
lst = []
for i in p.items():
    sub_lst = [i[0], len(i[1])]
    progression = i[1][0].get(only_root=True, flattened=True)
    sequence = [progression[0]]
    for j in progression:
        sequence.append(j) if j != sequence[-1] else None
    sub_lst.append(sequence)
    sub_lst.append(i[1][0].meta['source'])
    sub_lst.append(i[1][-1].meta['source'])
    lst.append(sub_lst)
pandas.DataFrame(lst).to_excel('out.xlsx',index=False)

