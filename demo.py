import pickle

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions
from matplotlib import pyplot as plt

from utils.utils import read_lib, split_huge_progression_dict

if __name__ == '__main__':
    prog = read_progressions('span_progressions_dict.pcls')
    print(sum(len(i) for i in prog.values()))


