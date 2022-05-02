import chorderator as cdt

cdt.set_melody('MIDI demos/inputs/E_86_8-8.mid')
cdt.set_meta(tonic=cdt.Key.E, meter=cdt.Meter.FOUR_FOUR, mode=cdt.Mode.MAJOR)
cdt.set_segmentation('A8A8')
cdt.set_output_style(cdt.Style.POP_STANDARD)
cdt.generate_save('final_out', task=['textured_chord', 'chord'], log=True)
