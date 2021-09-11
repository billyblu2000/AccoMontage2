# #######
# imports
# #######
import pickle

from pretty_midi import PrettyMIDI
from matplotlib import pyplot as plt

from chords.Chord import Chord
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list, ChordProgression
from utils.constants import DENSE, SPARSE
from utils.string import STATIC_DIR

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np, calculate_density, read_lib

my_progressions = read_progressions()[4520]
lib = read_lib()
print(my_progressions)
my_progressions.to_midi(lib=lib).write('test.mid')