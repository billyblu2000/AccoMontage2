import pickle

import numpy
from matplotlib import pyplot

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions, print_progression_list
from utils.string import STATIC_DIR

from utils.utils import read_lib, split_huge_progression_dict, PathGenerator

if __name__ == '__main__':
    all_prog = read_progressions('dict.pcls')
    score = pickle.load(open('minor_socre', 'rb'))
    print(len(score))
    input()
    for item in score:
        print(item[0])
        for id in item[1]:
            print(all_prog[id][0].progression)
