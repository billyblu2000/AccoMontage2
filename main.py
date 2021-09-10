# #######
# imports
# #######
import pickle

from pretty_midi import PrettyMIDI
from matplotlib import pyplot as plt
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list, ChordProgression
from utils.constants import DENSE, SPARSE
from utils.string import STATIC_DIR

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np, calculate_density

# this function will analyze the billboard original data and store the result in 'progression_with_type.pk'
# process_data()
