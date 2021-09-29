import pickle

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions
from matplotlib import pyplot as plt

from utils.utils import read_lib

if __name__ == '__main__':
    # prog = read_progressions('progressions_representative.pcls', span=True)
    # file = open('span_progressions_representative.pcls', 'wb')
    # pickle.dump(prog, file)
    # file.close()
    prog = read_progressions('span_progressions_representative.pcls.pcls')
    print(len(prog))



