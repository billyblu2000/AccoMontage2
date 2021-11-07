import chorderator as cdt

cdt.set_melody('MIDI demos/inputs/10.mid')
cdt.set_phrase([1])
cdt.set_meta(tonic=cdt.Key.C, mode=cdt.Mode.MAJOR, meter=cdt.Meter.FOUR_FOUR, tempo=120)

cdt.set_output_chord_style(cdt.ChordStyle.EMOTIONAL)
cdt.set_output_progression_style(cdt.ProgressionStyle.POP)
cdt.generate_save('generated', with_log=True)
