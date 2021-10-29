import math
import pickle
from matplotlib import pyplot as plt

import numpy
from matplotlib import pyplot

import chorderator as cdt
from chorderator import Const
from chords.ChordProgression import read_progressions, print_progression_list
from utils.string import STATIC_DIR

from utils.utils import read_lib, split_huge_progression_dict, PathGenerator, MIDILoader

# cdt.set_preprocess_model('PreProcessor')
# cdt.set_main_model('DP')
# cdt.set_postprocess_model('PostProcessor')

cdt.set_melody('124')
cdt.set_meta(tonic='', mode='maj', meter='4/4')

cdt.set_output_chord_style('standard')
cdt.set_output_progression_style('pop')
cdt.generate('generated.mid')
