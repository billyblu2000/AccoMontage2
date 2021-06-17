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
from utils.utils import listen, get_melo_notes_from_midi, get_bar_and_position, combine_ins, nmat2ins, pick_progressions
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

temp = {'maj': 43429, 'min': 10195, 'maj/5': 1855, 'min7': 6427, 'maj/9': 820, '7': 7573, 'maj6/9': 21, 'maj/3': 1133, 'maj(9)': 905, 'sus4': 986, 'maj(11)': 84, 'maj6/5': 55, '1': 2009, 'maj6': 766, 'sus4(b7)': 683, 'maj7': 1937, 'min6': 123, '7(#11)': 30, 'min7(11)': 54, 'maj7/3': 41, 'maj9': 468, 'aug(9)': 2, 'min9': 568, 'sus2': 159, 'aug': 32, 'sus4(b7,9)': 742, 'maj/bb13': 3, '5': 1605, 'min(9)': 94, 'min/b3': 303, 'min/3': 4, 'maj7/5': 9, '9': 286, 'sus4(9)': 85, '7/3': 131, '7/5': 148, 'aug(b7)': 155, 'min/5': 267, 'maj/b7': 314, 'min/b7': 364, 'maj/13': 94, 'maj/7': 177, 'min6/9': 2, 'min/7': 4, 'min/bb7': 1, 'sus4(9)/7': 4, 'dim': 146, 'dim7': 28, 'min7/11': 83, 'maj/11': 304, 'sus4/11': 2, '11': 314, 'maj6(9)': 147, '7/b7': 81, 'hdim7/b5': 11, 'min11': 203, 'hdim7': 91, '5/5': 30, 'min(11)': 62, 'maj(9)/3': 66, 'min9/b7': 8, 'dim/b5': 11, 'minmaj7': 14, 'min7/5': 127, 'dim/b3': 16, 'sus2(b7)': 37, 'maj6(9)/5': 8, 'min9/5': 5, 'sus4/9': 9, '1(b7)/b7': 2, '1(13)/13': 2, '1(3)': 3, '7(b13)': 14, 'maj7/9': 76, 'maj9/3': 17, 'min/11': 206, 'min/13': 60, '7(b9,b13)': 10, '7/b3': 7, 'maj6(b7)': 17, 'maj7/7': 30, '7(b9)': 101, 'dim/#11': 1, 'maj/b13': 1, 'dim/7': 1, 'maj7(#9)': 1, 'min(9)/7': 1, '7(#9)': 586, 'maj(9)/5': 32, 'maj6/3': 12, 'sus4(b7,9,13)': 54, 'maj6(7,#11)': 4, '13': 270, 'maj/b3': 2, '9(b13)': 4, 'minmaj7/5': 8, 'sus4/5': 52, '1(3,7)': 3, '1(11)': 24, 'sus4(b7)/11': 15, 'min7/b3': 71, '7/11': 42, 'maj6/11': 3, 'maj(9)/9': 4, 'maj7(#11)': 26, 'min9/11': 4, '5(b7)': 176, 'sus2/9': 24, '5/13': 20, 'dim/b7': 28, '7(b9)/3': 13, 'hdim7/b3': 3, 'dim(b13)': 2, '7(b9,#11)': 2, 'min7/b7': 105, 'min(11)/7': 3, 'min(b13)': 32, '1(b3,b7,11,9)': 19, '9/3': 17, 'min11/5': 2, 'hdim7/11': 1, 'sus4/b7': 26, 'maj(11)/11': 6, 'maj(#9)': 20, 'min13': 30, 'min7(b13)': 6, '7/9': 1, 'maj/#11': 9, '7(b13,#9)': 1, 'maj6(7)': 5, '5(b13)': 8, 'hdim7/b7': 21, 'min(11)/b7': 2, 'min(11)/11': 2, 'min6/5': 64, 'min11/b3': 6, 'aug(7)': 1, 'maj13': 78, 'sus4(b7,9,#11)': 2, 'maj(#11)': 21, '1(b7)': 35, '9/5': 20, 'maj6/13': 15, 'sus2/3': 1, 'maj(11)/b7': 1, 'min7/9': 33, '7/13': 27, '1(b5,11)': 1, '5(b7)/5': 1, '7(b9)/b9': 5, 'maj9(13)': 2, 'sus4(b7)/b7': 8, 'maj7/11': 2, '1(3)/9': 10, 'min/b1': 1, 'sus4(b13,b7)': 1, 'min(11,9)': 2, '7(b9)/5': 3, '7(b9)/b7': 3, 'maj7(#11)/3': 1, 'sus2(#11)': 1, '7/b9': 1, '1(b3,b7)/b7': 14, '5/11': 12, 'min/9': 5, 'min9/b3': 2, '5/9': 2, 'aug(b7,9)': 1, '1(b5,b7,3)': 1, 'sus4/7': 1, 'sus4(b7,9)/9': 2, 'min6/b3': 5, '7(11)': 4, 'maj(9,#11)': 1, 'maj9(#11)': 8, 'maj6/b5': 7, '7/b11': 5, 'sus4(b7)/5': 8, '7(b9)/11': 2, 'maj6/b7': 1, 'maj7(#5)': 1, '7/b5': 1, '5(b7)/b7': 8, '5(b7)/9': 10, '5(b7)/3': 10, 'maj6(9)/3': 4, 'dim7/b3': 2, 'min11/b7': 5, 'maj6(b7,11)': 4, '9(13,#11)': 12, 'maj/b11': 8, 'min7/13': 48, '1(b3)': 1, '7(b13)/3': 4, 'min9/9': 2, '1(11,9)': 3, '1(b5,b7,3)/b5': 1, 'sus2/5': 4, 'maj6(b9)': 2, 'min7/b9': 2, 'aug(b7)/3': 5, 'min6(9)/5': 1, '1(#5)': 4, 'aug/5': 6, 'min(9)/b7': 2, 'min(9)/13': 2, 'min/b13': 7, '1(3)/3': 1, 'maj9/11': 1, 'min9(b13)': 2}
new = {}
for item in temp.items():
    if item[1] > 100:
        new[item[0]] = item[1]
print(new)
print(len(new))
