import copy
import pickle

from chorderator.chords.ChordProgression import read_progressions
from pretty_midi import PrettyMIDI
from chorderator.utils.utils import pickle_read, split_huge_progression_dict
import chorderator.chords.parse_chord as phrase
import chorderator as cdt

name = 'D#_78_4-4-4-4.mid'
cdt.set_melody('MIDI demos/inputs/' + name)
cdt.set_phrase([1, 5, 9, 13])
cdt.set_meta(tonic=cdt.Key.DSharp, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

cdt.set_output_chord_style(cdt.ChordStyle.EMOTIONAL)
cdt.set_output_progression_style(cdt.ProgressionStyle.POP)
cdt.generate_save('generated_' + name)
