import pickle

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions

if __name__ == '__main__':
    cdt.set_meta(tonic='', mode=Const.Mode.MAJOR, meter=Const.Meter.FOUR_FOUR)
    cdt.generate()

