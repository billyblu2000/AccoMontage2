import chorderator as cdt

cdt.set_melody('MIDI demos/inputs/E_86_8-8.mid')
cdt.set_meta(tonic=cdt.Key.E)
cdt.set_segmentation('A8A8')
cdt.set_output_style(cdt.Style.POP_STANDARD)
cdt.generate_save('final_out')
