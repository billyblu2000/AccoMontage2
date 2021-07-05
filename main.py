# #######
# imports
# #######
from pretty_midi import PrettyMIDI, Instrument, Note
from settings import *
from chords.ChordProgression import read_progressions, query_progression, print_progression_list, ChordProgression
from utils.ProcessData import process_data
from utils.constants import PIANO, SHORT, DENSE, LONG, SPARSE

from utils.process_pop909 import process
from utils.string import STATIC_DIR
from utils.utils import listen, get_melo_notes_from_midi, get_bar_and_position, combine_ins, nmat2ins, \
    pick_progressions, compute_destination
from matplotlib import pyplot as plt
import numpy as np

# this function will analyze the billboard original data and store the result in 'progression.txt'
# process_data()
#
# POP909 = 'progressions_from_pop909.txt'
# DEFAULT = 'progressions.txt'
#
# prog_list = read_progressions(progression_file=DEFAULT)
# print(len(prog_list))
# print(len(pick_progressions(SHORT,DENSE, progression_list=prog_list)))
# print(len(pick_progressions(SHORT,SPARSE, progression_list=prog_list)))
# print(len(pick_progressions(LONG,DENSE, progression_list=prog_list)))
# print(len(pick_progressions(LONG,SPARSE, progression_list=prog_list)))
