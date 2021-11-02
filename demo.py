import math
import pickle
from matplotlib import pyplot as plt

import numpy
from matplotlib import pyplot

import chorderator as cdt
from chords.ChordProgression import read_progressions, print_progression_list
from utils.string import STATIC_DIR

from utils.utils import read_lib, split_huge_progression_dict, PathGenerator, MIDILoader

# cdt.set_preprocess_model('PreProcessor')
# cdt.set_main_model('DP')
# cdt.set_postprocess_model('PostProcessor')

cdt.set_melody('MIDI demos/inputs/3.mid')
cdt.set_phrase([1])
cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

cdt.set_output_chord_style(cdt.ChordStyle.STANDARD)
cdt.set_output_progression_style(cdt.ProgressionStyle.POP)
cdt.generate('MIDI demos/outputs/generated.mid')
