from chorderator.chords.ChordProgression import read_progressions
from pretty_midi import PrettyMIDI
from chorderator.utils.utils import pickle_read
import chorderator.chords.parse_chord as phrase
import chorderator as cdt

# cdt.set_melody('MIDI demos/inputs/30.mid')
# cdt.set_phrase([1])
# cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR, tempo=120)
#
# cdt.set_output_chord_style(cdt.ChordStyle.EMOTIONAL)
# cdt.set_output_progression_style(cdt.ProgressionStyle.POP)
# cdt.generate_save('generated')
rep = pickle_read('rep')
