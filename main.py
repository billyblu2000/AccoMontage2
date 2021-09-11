# #######
# imports
# #######
import pickle

from pretty_midi import PrettyMIDI, Instrument, Note
from matplotlib import pyplot as plt

from chords.Chord import Chord
from settings import *
from chords.ChordProgression import read_progressions, print_progression_list, ChordProgression
from utils.constants import DENSE, SPARSE
from utils.string import STATIC_DIR

from utils.utils import MIDILoader, listen, Logging, pick_progressions, np, calculate_density, read_lib

my_progressions = read_progressions()
lib = read_lib()
i = 0
ins = Instrument(program=0)
for prog in my_progressions:
    if [6, 6, 6, 6, 6, 6, 6, 6, 4, 4, 4, 4, 4, 4, 4, 4, 1, 1, 1, 1, 1, 1, 1, 1, 5, 5, 5, 5, 5, 5, 5, 5] in prog and len(
            prog) == 32:
        all_notes = prog.to_midi(lib=lib).instruments[0].notes
        for note in all_notes:
            print(note)
            ins.notes.append(Note(start=note.start+8*i,
                                  end=note.end+8*i,
                                  pitch=note.pitch,
                                  velocity=note.velocity))
        i += 1
        print(i)
    if i > 100:
        break
my_midi = PrettyMIDI()
my_midi.instruments.append(ins)
# my_midi.write('100-6415.mid')
# my_progressions.to_midi(lib=lib).write('test.mid')
