# #######
# imports
# #######
import pickle

from pretty_midi import PrettyMIDI
from matplotlib import pyplot as plt
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list
from utils.constants import DENSE, SPARSE
from utils.string import STATIC_DIR

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np

# this function will analyze the billboard original data and store the result in 'progression_with_type.pk'
# process_data()

file = open(STATIC_DIR + 'new_progressions.pcls', 'rb')
prog_list = pickle.load(file)
print_progression_list(prog_list)
file.close()

# file = open(STATIC_DIR + 'source_base.pnt', 'rb')
# all_midis = pickle.load(file)
# print(all_midis)
# file.close()