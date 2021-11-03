import chorderator as cdt
from chords.ChordProgression import read_progressions

cdt.set_melody('MIDI demos/inputs/35.mid')
cdt.set_phrase([1])
cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

cdt.set_output_chord_style(cdt.ChordStyle.STANDARD)
cdt.set_output_progression_style(cdt.ProgressionStyle.POP)
cdt.generate('MIDI demos/outputs/generated.mid')