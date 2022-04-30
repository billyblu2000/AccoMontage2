import copy
import os
import pickle

from chorderator.chords.ChordProgression import read_progressions
from pretty_midi import PrettyMIDI
from chorderator.utils.utils import pickle_read, split_huge_progression_dict
from accomontage.AccoMontage_inference import accomontage
import chorderator.chords.parse_chord as phrase
import chorderator as cdt

name = 'D#_78_4-4-4-4.mid'
cdt.set_melody('MIDI demos/inputs/' + name)
cdt.set_phrase([1, 5, 9, 13])
cdt.set_meta(tonic=cdt.Key.DSharp, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR)

cdt.set_output_style(cdt.Style.POP_STANDARD)
cdt.generate_save('generated_' + name, with_log=True)

accomontage(song_name='generated_' + name + '.mid',
            song_root='generated_'+name,
            segmentation='A4A4A4A4\n',
            output_name='final.mid')