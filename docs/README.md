# CHORDERATOR

> A useful tool to generate chord progressions and accompaniment according to melody MIDIs


### Demo

```python
import chorderator as cdt

if __name__ == '__main__':

    demo_name = 'hpps30'
    input_melody_path = 'MIDI demos/inputs/' + demo_name + '/melody.mid'

    cdt.set_melody(input_melody_path)
    cdt.set_meta(tonic=cdt.Key.A)
    cdt.set_segmentation('A8B8A8B8')
    cdt.set_texture_prefilter((0, 2))
    cdt.set_note_shift(16)
    cdt.set_output_style(cdt.Style.POP_STANDARD)
    cdt.generate_save(demo_name + '_output_results')
    
```

Folder ``chorderator/utils/models/accomontage`` referencing AccoMontage by Jingwei Zhao and Gus Xia, available at https://github.com/zhaojw1998/AccoMontage
